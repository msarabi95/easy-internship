from __future__ import unicode_literals

from copy import copy

from django.core import validators
from django.core.exceptions import ObjectDoesNotExist, ValidationError, MultipleObjectsReturned
from django.db import models
from django.utils.crypto import get_random_string
from django_nyt.utils import notify
from month.models import MonthField

from months.models import Internship


class RotationManager(models.Manager):
    def current_for_month(self, month):
        try:
            return self.get(month=month)
        except ObjectDoesNotExist:
            return None

    def non_electives(self):
        return self.filter(is_elective=False)

    def electives(self):
        return self.filter(is_elective=True)


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
                email=self.department_email,
                phone=self.department_phone,
                extension=self.department_extension,
            )

    def __unicode__(self):
        return self.get_department().name


class RotationRequestQuerySet(models.QuerySet):
    def month(self, month):
        """
        Return rotation requests for a particular month.
        """
        return self.filter(month=month)

    def unreviewed(self):
        """
        Return rotation requests that don't have a response nor forward.
        """
        return self.filter(response__isnull=True, forward__isnull=True)

    def forwarded_unreviewed(self):
        """
        Return rotation requests that have been forwarded but are awaiting response.
        """
        return self.filter(forward__isnull=False, forward__response__isnull=True)

    def open(self):
        """
        Return rotation requests that don't yet have a response nor a forward response.
        Equivalent to `unreviewed` + `forwarded_unreviewed`.
        """
        return self.filter(response__isnull=True, forward__response__isnull=True)

    def closed(self):
        """
        Return rotation requests that have received either a response or a forward response.
        """
        return self.exclude(response__isnull=True, forward__response__isnull=True)

    def current_for_month(self, month):
        """
        Return the current open request for a specific month.
        (There should only be one open request per month at a time.)
        """
        # This only has meaning when filtering requests for a specific internship
        open_requests = self.month(month).open()
        if open_requests.count() > 1:
            raise MultipleObjectsReturned(
                "Expected at most 1 open rotation request for the month %s, found %d!" % (
                    month.first_day().strftime("%B %Y"),
                    open_requests.count()
                )
            )
        try:
            return open_requests.latest("submission_datetime")
        except ObjectDoesNotExist:
            return None


class RotationRequest(models.Model):
    internship = models.ForeignKey(Internship, related_name="rotation_requests")
    month = MonthField()
    specialty = models.ForeignKey('hospitals.Specialty', related_name="rotation_requests")  # TODO: Is this field really necessary?
    requested_department = models.OneToOneField(RequestedDepartment)
    delete = models.BooleanField(default=False)  # Flag to determine if this is a "delete" request
    # FIXME: Maybe department & specialty should be optional with delete=True
    # FIXME: The name `delete` conflicts with the api function `delete()`
    is_elective = models.BooleanField(default=False)
    submission_datetime = models.DateTimeField(auto_now_add=True)

    objects = RotationRequestQuerySet().as_manager()

    PENDING_STATUS = "P"
    FORWARDED_STATUS = "F"
    REVIEWED_STATUS = "R"

    def save(self, *args, **kwargs):
        # Make sure the request is valid before saving
        self.full_clean()

        super(RotationRequest, self).save(*args, **kwargs)

    def clean(self):
        """
        Checks that:
        1- The rotation request alters the internship plan in a way that keeps it at 12 rotations or less.
        2- The rotation request alters the internship plan in a way that doesn't exceed the maximum number of months
         for each required specialty.
        """
        predicted_plan = self.get_predicted_plan()
        predicted_plan.clean()

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

            for request in self.internship.rotation_requests.open().filter(delete=False)
        ]

        # Don't forget this rotation request (self), since it's not yet saved when this is running
        if not self.delete:
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

            # TODO: Test
            if is_approved:
                # Remove any previous rotation in the current month
                self.internship.rotations.filter(month=self.month).delete()

                # Unless this is a delete, request, add a new rotation object for the current month
                if not self.delete:
                    # If the requested department is not in the database, add it.
                    # FIXME: This shouldn't be default behavior
                    if not self.requested_department.is_in_database:
                        self.requested_department.add_to_database()

                    self.internship.rotations.create(
                        month=self.month,
                        specialty=self.specialty,
                        department=self.requested_department.get_department(),
                        is_elective=self.is_elective,
                        rotation_request=self,
                    )

            # Notify intern
            if is_approved:

                # --notifications--

                notify(
                    "Rotation request %d for %s has been approved." % (self.id, self.month.first_day().strftime("%B %Y")),
                    "rotation_request_approved",
                    target_object=self,
                    url="/planner/%d/" % int(self.month),
                )
            else:

                # --notifications--
                notify(
                    "Rotation request %d for %s has been declined." % (self.id, self.month.first_day().strftime("%B %Y")),
                    "rotation_request_declined",
                    target_object=self,
                    url="/planner/%d/history/" % int(self.month),
                )
        else:
            raise Exception("This rotation request has already been responded to.")

    def forward_request(self):
        """
        Forward the rotation request; raise an error if it's already forwarded.
        """
        try:
            self.forward
        except ObjectDoesNotExist:
            # TODO: Add department to database if it's not there already

            RotationRequestForward.objects.create(
                rotation_request=self,
            )

            # TODO: Notify
            # --notifications--
        else:
            raise Exception("This rotation request has already been forwarded.")

    def get_response(self):
        """
        Return the request response if it exists, or the forward's response if it exists;
        otherwise raise a RelatedObjectDoesNotExist error.
        """
        try:
            return self.response
        except ObjectDoesNotExist:
            try:
                return self.forward.response
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist("RotationRequest has no response or forward response.")

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
    key = models.CharField(max_length=20, unique=True)
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

            # TODO: Test
            if is_approved:
                # Remove any previous rotation in the current month
                self.rotation_request.internship.rotations.filter(month=self.rotation_request.month).delete()

                # Unless this is a delete request, add a new rotation object for the current month
                if not self.rotation_request.delete:
                    self.rotation_request.internship.rotations.create(
                        month=self.rotation_request.month,
                        specialty=self.rotation_request.specialty,
                        department=self.rotation_request.requested_department.get_department(),
                        is_elective=self.rotation_request.is_elective,
                        rotation_request=self.rotation_request,
                    )

            # Close the plan request if this is the last rotation request within it
            self.rotation_request.check_closure()

            # Notify intern
            if is_approved:
                # --notifications--
                notify(
                    "Rotation request %d for %s has been approved." % (self.id, self.month.first_day().strftime("%B %Y")),
                    "rotation_request_approved",
                    target_object=self.rotation_request,
                    url="/planner/%d/" % int(self.month),
                )
            else:
                # --notifications--
                notify(
                    "Rotation request %d for %s has been declined." % (self.id, self.month.first_day().strftime("%B %Y")),
                    "rotation_request_declined",
                    target_object=self.rotation_request,
                    url="/planner/%d/history/" % int(self.month),
                )

        else:
            raise Exception("This rotation request has already been responded to.")

    def save(self, *args, **kwargs):

        # TODO: Test
        # Generate a random string to represent
        if self.key is None or self.key == "":
            # Choose a unique key for the rotation request forward
            self.key = get_random_string(length=20)

            while self.__class__.objects.filter(key=self.key).exists():
                self.key = get_random_string(length=20)

        super(RotationRequestForward, self).save(*args, **kwargs)

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