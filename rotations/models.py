from __future__ import unicode_literals

from copy import copy

from django.core import validators
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.crypto import get_random_string
from django_nyt.utils import notify
from month.models import MonthField

from months.models import Internship
from rotations.managers import RotationManager, RotationRequestQuerySet


class Rotation(models.Model):
    internship = models.ForeignKey(Internship, related_name="rotations")
    month = MonthField()
    specialty = models.ForeignKey('hospitals.Specialty', related_name="rotations")
    department = models.ForeignKey('hospitals.Department', related_name="rotations")
    is_elective = models.BooleanField(default=False)
    rotation_request = models.OneToOneField("RotationRequest")

    objects = RotationManager()

    def __unicode__(self):
        return "%s rotation in %s (%s)" % (self.specialty, self.department, self.month)


class RequestedDepartment(models.Model):
    is_in_database = models.BooleanField()
    department = models.ForeignKey('hospitals.Department', related_name="department_requests", null=True, blank=True)

    department_hospital = models.ForeignKey('hospitals.Hospital', null=True, blank=True)
    department_name = models.CharField(max_length=128, blank=True)
    department_specialty = models.ForeignKey('hospitals.Specialty', null=True, blank=True)
    department_contact_name = models.CharField(max_length=128, blank=True)
    department_contact_position = models.CharField(max_length=128, null=True, blank=True)
    department_email = models.EmailField(max_length=128, blank=True)
    department_phone = models.CharField(
        max_length=128,
        blank=True,
        validators=[
            validators.RegexValidator(
                r'^\+\d{12}$',
                code='invalid_phone_number',
                message="Phone number should follow the format +966XXXXXXXXX."
            )
        ]
    )
    department_extension = models.CharField(
        max_length=16,
        blank=True,
        validators=[
            validators.RegexValidator(
                r'^\d{3}\d*$',
                code='invalid_extension',
                message="Extension should be at least 3 digits long."
            )
        ]
    )

    def clean(self):
        """
        Check that *either* of the department field or the department_* details
        fields are filled, but not both or none; and that `is_in_database` flag
        is correctly assigned.
        """
        department_field_filled = self.department is not None
        department_details_filled = all([
            self.department_hospital is not None,
            self.department_name != "",
            self.department_specialty is not None,
            self.department_contact_name != "",
            self.department_contact_position != "",
            self.department_email != "",
            self.department_phone != "",
            self.department_extension != "",
        ])

        if department_field_filled and department_details_filled:
            raise ValidationError("Either an existing department should be chosen, "
                                  "or the details of a new department be filled; but not both.")

        elif not department_field_filled and not department_details_filled:
            raise ValidationError("Either an existing department should be chosen, "
                                  "or the details of a new department be filled.")

        elif department_field_filled and not self.is_in_database:
            raise ValidationError("`is_in_database` flag should be True if an existing department is chosen.")

        elif department_details_filled and self.is_in_database:
            raise ValidationError("`is_in_database` flag should be False if "
                                  "the details of a new department are filled in.")

    def link_to_existing_department(self, department):
        """
        Clears all the department_* details fields and links to an existing department through
         the `department` field.
        """
        from hospitals.models import Department

        if department in Department.objects.all():

            self.department = department
            self.is_in_database = True

            # Empty the department_* details fields
            self.department_hospital = None
            self.department_name = ""
            self.department_specialty = None
            self.department_contact_name = ""
            self.department_contact_position = ""
            self.department_email = ""
            self.department_phone = ""
            self.department_extension = ""

            self.save()
        else:
            raise ObjectDoesNotExist("This department doesn't exist in the database.")

    def add_to_database(self):
        """
        Create a new department based on the data in this request, then link the request to that
        department and clear the department_* details fields.
        """
        from hospitals.models import Department

        if self.department in Department.objects.all():
            raise Exception("Department already exists in database!")  # FIXME: A more accurate exception class?

        new_department = Department.objects.create(  # FIXME: What about the dept. being actually a section of another?
            hospital=self.department_hospital,
            name=self.department_name,
            specialty=self.department_specialty,
            contact_name=self.department_contact_name,
            contact_position=self.department_contact_position,
            email=self.department_email,
            phone=self.department_phone,
            extension=self.department_extension,
        )
        self.link_to_existing_department(new_department)

    def get_department(self):
        """
        Return the `Department` instance if that exists in the database. Otherwise return
        a `Department` object containing all the details from the department_* fields.
        """
        from hospitals.models import Department
        if self.is_in_database:
            return self.department
        else:
            return Department(
                hospital=self.department_hospital,
                name=self.department_name,
                specialty=self.department_specialty,
                contact_name=self.department_contact_name,
                contact_position=self.department_contact_position,
                email=self.department_email,
                phone=self.department_phone,
                extension=self.department_extension,
            )

    def __unicode__(self):
        return self.get_department().name


class RotationRequest(models.Model):
    internship = models.ForeignKey(Internship, related_name="rotation_requests")
    month = MonthField()
    specialty = models.ForeignKey('hospitals.Specialty', related_name="rotation_requests")  # TODO: Is this field really necessary?
    requested_department = models.OneToOneField(RequestedDepartment)
    is_delete = models.BooleanField(default=False)  # Flag to determine if this is a "delete" request
    # FIXME: Maybe department & specialty should be optional with delete=True
    # FIXME: The name `delete` conflicts with the api function `delete()`
    is_elective = models.BooleanField(default=False)
    submission_datetime = models.DateTimeField(auto_now_add=True)

    objects = RotationRequestQuerySet().as_manager()

    PENDING_STATUS = "P"
    FORWARDED_STATUS = "F"
    REVIEWED_STATUS = "R"

    def validate_request(self):
        """
        Checks that:
        1- The rotation request alters the internship plan in a way that keeps it at 12 rotations or less.
        2- The rotation request alters the internship plan in a way that doesn't exceed the maximum number of months
         for each required specialty.
        """
        predicted_plan = self.get_predicted_plan()
        predicted_plan.validate_internship_plan()

    def get_predicted_plan(self):
        """
        Returns an `Internship` object representing what the internship plan will look like
        if all the rotation requests in this plan request are accepted.
        """
        # Make a list of new rotation objects based on the rotation requests attached to the
        # internship plan
        updated_rotations = [
            Rotation(internship=self.internship,
                     month=request.month,
                     department=request.requested_department.get_department(),
                     specialty=request.specialty,
                     is_elective=request.is_elective)

            for request in self.internship.rotation_requests.open().filter(is_delete=False)
        ]

        # Don't forget this rotation request (self), since it's not yet saved when this is running
        if not self.is_delete:
            updated_rotations.append(
                Rotation(internship=self.internship,
                         month=self.month,
                         department=self.requested_department.get_department(),
                         specialty=self.specialty,
                         is_elective=self.is_elective)
            )

        # Exclude overlapping months
        excluded_months = self.internship.rotation_requests.open().values_list("month", flat=True)

        # To make the final list of the updated rotations, add the existing unaffected rotations to the
        # list of new ones
        updated_rotations.extend(self.internship.rotations.exclude(month__in=excluded_months))

        # Make a copy of the internship object
        predicted = copy(self.internship)
        predicted.pk = None
        # predicted.intern = None

        # We need to tweak some internal Django attributes to allow us to relate the updated rotations
        # to the predicted internship object without having to save them in the database
        # Check: http://stackoverflow.com/a/16222603
        qs = predicted.rotations.all()
        qs._result_cache = updated_rotations
        qs._prefetch_done = True
        predicted._prefetched_objects_cache = {'rotations': qs}

        return predicted

    def get_status(self):
        """
        The status of a rotation request is one of 3:
        (1) Pending: if the request hasn't received a repsonse
        (2) Forwarded: if the request has been forwarded but hasn't received a response yet
        (3) Reviewed: if the request has received a response
        """
        # Set the three booleans `has_response`, `has_forward`, and `forward_has_response`
        # to reflect the status of the request
        try:
            self.response
            has_response = True
        except ObjectDoesNotExist:
            has_response = False

        try:
            self.forward
            has_forward = True

        except ObjectDoesNotExist:
            has_forward = False

        # Return the appropriate status based on the presence/absence of the response,
        # forward, and forward response
        if not has_response and not has_forward:
            return self.PENDING_STATUS

        elif has_forward and not has_response:
            return self.FORWARDED_STATUS

        elif has_response:
            return self.REVIEWED_STATUS

    def __unicode__(self):
        return "Request for %s rotation at %s (%s)" % (self.specialty.name,
                                                       self.requested_department.get_department().name,
                                                       self.month)

    class Meta:
        ordering = ('internship', 'month', )


class RotationRequestResponse(models.Model):
    rotation_request = models.OneToOneField(RotationRequest, related_name="response")
    is_approved = models.BooleanField()
    comments = models.TextField()
    response_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Response to request #%d" % self.rotation_request.id


class RotationRequestForward(models.Model):
    rotation_request = models.OneToOneField(RotationRequest, related_name="forward")
    forward_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Forward of request #%d" % self.rotation_request.id
