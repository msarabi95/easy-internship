from __future__ import unicode_literals

from copy import copy

from accounts.models import Intern
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone
from month.models import MonthField


class Hospital(models.Model):
    name = models.CharField(max_length=128)
    abbreviation = models.CharField(max_length=16)
    is_kamc = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Specialty(models.Model):
    name = models.CharField(max_length=128)
    abbreviation = models.CharField(max_length=4)
    required_months = models.PositiveIntegerField()
    parent_specialty = models.ForeignKey("Specialty", related_name="subspecialties", null=True,
                                         blank=True)

    def is_subspecialty(self):
        """
        Return True if the specialty has a parent_specialty.
        """
        if self.parent_specialty is not None:
            return True
        else:
            return False

    def get_general_specialty(self):
        """
        Return `self` if already a general specialty (no parent specialty).
        Return parent specialty otherwise.
        """
        if not self.is_subspecialty():
            return self
        else:
            return self.parent_specialty

    def __unicode__(self):
        return self.name


"""

General Specialties, General Departments
========================================

    Specialty 1 ----- * Department
        1                   1
        |                   |
        |                   |
        |                   |
        *                   *
    Specialty 1 ----- * Department

========================================
Subspecialties, Sub-departments (Sections)

"""


class Department(models.Model):
    hospital = models.ForeignKey(Hospital, related_name="departments")
    parent_department = models.ForeignKey("Department", related_name="sections", null=True,
                                          blank=True)
    name = models.CharField(max_length=128)
    specialty = models.ForeignKey(Specialty, related_name="departments")
    contact_name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    phone = models.CharField(max_length=128)
    extension = models.CharField(max_length=16)

    def get_available_seats(self, month):
        """
        Return the number of available seats for a specific month.
        """
        try:
            return self.seats.get(month=month).available_seat_count
        except SeatAvailability.DoesNotExist:
            return None

    def get_contact_details(self):
        """
        Return the contact details of the department if saved.
        If no details are supplied, return the details of the parent department.
        """
        if self.email != "":
            return {
                "contact_name": self.contact_name,
                "email": self.email,
                "phone": self.phone,
                "extension": self.extension,
            }
        elif self.parent_department is not None:
            return self.parent_department.get_contact_details()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.hospital.abbreviation)


class SeatAvailability(models.Model):
    month = MonthField()
    specialty = models.ForeignKey(Specialty, related_name="seats")  # FIXME: This field is unnecessary
    department = models.ForeignKey(Department, related_name="seats")
    available_seat_count = models.PositiveIntegerField()

    def __unicode__(self):
        return "Seat availability for %s in %s during %s" % (self.specialty.name,
                                                             self.department.__unicode__(),
                                                             self.month)

    # class Meta:
    #     unique_together = ("month", "specialty", "department")


class Internship(models.Model):
    intern = models.OneToOneField(Intern)
    start_month = MonthField()

    def clean(self):
        """
        Checks 2 conditions:
        1- The internship plan consists of exactly 12 rotations.
        2- The internship plan achieves the minimum number of months for each required specialty.
        """
        errors = []

        if self.rotations.count() != 12:
            errors.append(ValidationError("The internship plan should contain exactly 12 months."))

        # Get a list of general specialties
        general_specialties = Specialty.objects.filter(parent_specialty__isnull=True)

        # For each general specialty, check that the number of rotations under that specialty is not less
        # the required number of months.
        for specialty in general_specialties:
            if len(filter(lambda rotation: rotation.specialty.get_general_specialty() == specialty,
                          self.rotations.all())) < specialty.required_months:
                errors.append(ValidationError("The internship plan should contain at least %d month(s) of %s.",
                                              params=(specialty.required_months, specialty.name)))
        if errors:
            raise ValidationError(errors)


class Rotation(models.Model):
    internship = models.ForeignKey(Internship, related_name="rotations")
    month = MonthField()
    specialty = models.ForeignKey(Specialty, related_name="rotations")
    department = models.ForeignKey(Department, related_name="rotations")

    def __unicode__(self):
        return "%s rotation in %s (%s)" % (self.specialty, self.department, self.month)


class PlanRequest(models.Model):
    internship = models.ForeignKey(Internship, related_name="plan_requests")
    creation_datetime = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)
    submission_datetime = models.DateTimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    closure_datetime = models.DateTimeField(blank=True, null=True)

    def get_predicted_plan(self):
        """
        Returns an `Internship` object representing what the internship plan will look like
        if all the rotation requests in this plan request are accepted.
        """
        # Make a list of new rotation objects based on the rotation requests attached to the
        # plan request
        updated_rotations = [
            Rotation(internship=self.internship,
                     month=request.month,
                     department=request.requested_department.get_department(),
                     specialty=request.specialty)
            
            for request in self.rotation_requests.filter(delete=False)
        ]

        # Exclude the rotations that have been requested to be deleted
        excluded_months = self.rotation_requests.filter(delete=True).values_list("month", flat=True)

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
        
    def clean(self):
        """
        Checks 3 conditions:
        1- The plan request contains at least 1 rotation request.
        2- The plan request alters the internship plan in a way that keeps it at exactly 12 rotations.
        3- The plan request alters the internship plan in a way that achieves the minimum number of months for
         each required specialty.
        """
        # This checks for condition 1
        if not self.rotation_requests.exists():
            raise ValidationError("The plan request should contain at least 1 rotation request.")

        # This checks for conditions 2 & 3
        predicted_plan = self.get_predicted_plan()
        predicted_plan.clean()

    def check_closure(self):
        """
        Returns whether the current plan request has been closed or not.
        """
        if self.rotation_requests.filter(response__isnull=True).exists():
            return False
        else:
            self.is_closed = True

            # Set the closure time to the datetime of the last response
            self.closure_datetime = \
                self.rotation_requests.latest("response__response_datetime").response.response_datetime
            return True

    def submit(self):
        """
        Submit the plan request for review.
        """
        if not self.is_submitted:

            # Make sure the plan request is valid before submission
            self.full_clean()

            self.is_submitted = True
            self.submission_datetime = timezone.now()

            # TODO: send notification?
        else:
            raise Exception("This plan request has already been submitted.")  # FIXME: more appropriate exception?

    def __unicode__(self):
        return "%s's plan request created on %s" % (self.internship.intern.profile.get_en_full_name(),
                                                    self.creation_datetime)


class RequestedDepartment(models.Model):
    is_in_database = models.BooleanField()
    department = models.ForeignKey(Department, related_name="department_requests", null=True, blank=True)

    department_hospital = models.ForeignKey(Hospital, null=True, blank=True)
    department_name = models.CharField(max_length=128)
    department_specialty = models.ForeignKey(Specialty, null=True, blank=True)
    department_contact_name = models.CharField(max_length=128)
    department_email = models.EmailField(max_length=128)
    department_phone = models.CharField(max_length=128)
    department_extension = models.CharField(max_length=16)

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
        if department in Department.objects.all():

            self.department = department
            self.is_in_database = True

            # Empty the department_* details fields
            self.department_hospital = None
            self.department_name = ""
            self.department_specialty = None
            self.department_contact_name = ""
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
        if self.department in Department.objects.all():
            raise Exception("Department already exists in database!")  # FIXME: A more accurate exception class?

        new_department = Department.objects.create(  # FIXME: What about the dept. being actually a section of another?
            hospital=self.department_hospital,
            name=self.department_name,
            specialty=self.department_specialty,
            contact_name=self.department_contact_name,
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
        if self.is_in_database:
            return self.department
        else:
            return Department(
                hospital=self.department_hospital,
                name=self.department_name,
                specialty=self.department_specialty,
                contact_name=self.department_contact_name,
                email=self.department_email,
                phone=self.department_phone,
                extension=self.department_extension,
            )

    def __unicode__(self):
        return self.get_department().name


class RotationRequest(models.Model):
    plan_request = models.ForeignKey(PlanRequest, related_name="rotation_requests")
    month = MonthField()
    specialty = models.ForeignKey(Specialty, related_name="rotation_requests")  # TODO: Is this field really necessary?
    requested_department = models.OneToOneField(RequestedDepartment)
    delete = models.BooleanField(default=False)  # Flag to determine if this is a "delete" request
    # FIXME: Maybe department & specialty should be optional with delete=True
    # FIXME: The name `delete` conflicts with the api function `delete()`

    PENDING_STATUS = "P"
    FORWARDED_STATUS = "F"
    REVIEWED_STATUS = "R"

    def get_status(self):
        """
        The status of a rotation request is one of 3:
        (1) Pending: if the request hasn't received a repsonse
        (2) Forwarded: if the request has been forwarded but hasn't received a response yet
        (3) Reviewed: if either the request or the request forward has received a response
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

            try:
                self.forward.response
                forward_has_response = True
            except ObjectDoesNotExist:
                forward_has_response = False

        except ObjectDoesNotExist:
            has_forward = False

        # Return the appropriate status based on the presence/absence of the response,
        # forward, and forward response
        if not has_response and not has_forward:
            return self.PENDING_STATUS

        elif has_forward and not forward_has_response:
            return self.FORWARDED_STATUS

        elif has_response or \
            (has_forward and forward_has_response):
            return self.REVIEWED_STATUS

    def respond(self, is_approved, comments=""):
        """
        Respond to the rotation request; raise an error if it's already responded to.
        """
        try:
            self.response
        except ObjectDoesNotExist:
            RotationRequestResponse.objects.create(
                rotation_request=self,
                is_approved=is_approved,
                comments=comments,
            )

            # TODO: Notify
        else:
            raise Exception("This rotation request has already been responded to.")

    def forward_request(self):
        """
        Forward the rotation request; raise an error if it's already forwarded.
        """
        try:
            self.forward
        except ObjectDoesNotExist:
            RotationRequestForward.objects.create(
                rotation_request=self,
            )

            # TODO: Notify
        else:
            raise Exception("This rotation request has already been forwarded.")

    def __unicode__(self):
        return "Request for %s rotation at %s (%s)" % (self.specialty.name,
                                                       self.requested_department.get_department().name,
                                                       self.month)


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

    def respond(self, is_approved, response_memo, respondent_name, comments=""):
        try:
            self.response
        except ObjectDoesNotExist:
            RotationRequestForwardResponse.objects.create(
                forward=self,
                is_approved=is_approved,
                response_memo=response_memo,
                comments=comments,
                respondent_name=respondent_name,
            )

            # TODO: Notify
        else:
            raise Exception("This rotation request has already been responded to.")

    def __unicode__(self):
        return "Forward of request #%d" % self.rotation_request.id


class RotationRequestForwardResponse(models.Model):
    forward = models.OneToOneField(RotationRequestForward, related_name="response")
    is_approved = models.BooleanField()
    response_memo = models.FileField(upload_to="forward_response_memos")
    comments = models.TextField()
    respondent_name = models.CharField(max_length=128)
    response_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Response to forward #%d (for request #%d)" % (self.forward.id, self.forward.rotation_request.id)
