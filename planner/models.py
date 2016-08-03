from __future__ import unicode_literals

from copy import copy

from accounts.models import Intern
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
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

    class Meta:
        verbose_name_plural = "Specialties"


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

    def get_internship_info(self):
        """
        Return a dictionary containing information about the internship and current
        plan request, if any.
        """
        return {
            "currentPlanRequest": True if self.plan_requests.current() else False,
            "currentPlanRequestSubmitted": self.plan_requests.current().is_submitted if self.plan_requests.current() else False,
            "currentPlanRequestSubmitDateTime": self.plan_requests.current().submission_datetime.strftime("%-d %B %Y")
                                            if self.plan_requests.current() and self.plan_requests.current().is_submitted else None,
        }

    def get_internship_months(self):
        """
        Returns a list containing 15 month items starting with the internships' `start_month`.
        Each month item is a dictionary of the format:
        {
            "month": `Month` object,
            "rotations": a list of all `Rotation` objects associated with this month,
            "requests": a list of all `RotationRequest` objects associated with this month,
        }
        """
        months = []
        for add in range(15):
            month = self.start_month + add
            current_rotation = self.rotations.current(month)
            rotation_history = self.rotations.history(month)

            current_rotation_dict = {
                "id": current_rotation.id,
                "specialty": current_rotation.specialty.get_general_specialty().name,
                "subSpecialty": current_rotation.specialty.name if current_rotation.specialty.is_subspecialty() else "-",
                "department": current_rotation.department.parent_department.name
                            if current_rotation.department.parent_department
                            else current_rotation.department.name,
                "section": current_rotation.department.name if current_rotation.department.parent_department else "-",
                "hospital": current_rotation.department.hospital.name,
                "submitDate": RotationRequest.objects.filter(month=current_rotation.month,
                                                             response__is_approved=True).last()
                                                            .plan_request.submission_datetime.strftime("%-d %B %Y"),
                "reviewDate": RotationRequest.objects.filter(month=current_rotation.month,
                                                             response__is_approved=True).last()
                                                            .response.response_datetime.strftime("%-d %B %Y"),
            } if current_rotation else None

            rotation_history_dict = [{
                "id": rotation.id,
                "label": rotation.department.__unicode__(),
            } for rotation in rotation_history]

            if self.plan_requests.current():  # FIXME: reconsider?
                current_request = self.plan_requests.current().rotation_requests.filter(month=month,
                                                                                        response__isnull=True,
                                                                                        forward__response__isnull=True).first()

                current_request_dict = {
                    "id": current_request.id,
                    "delete": current_request.delete,
                    "specialty": current_request.specialty.get_general_specialty().name,
                    "subSpecialty": current_request.specialty.name if current_request.specialty.is_subspecialty() else "-",
                    "department": current_request.requested_department.get_department().parent_department.name
                                if current_request.requested_department.get_department().parent_department
                                else current_request.requested_department.get_department().name,
                    "section": current_request.requested_department.get_department().parent_department.name
                                if current_request.requested_department.get_department().parent_department
                                else "-",
                    "hospital": current_request.requested_department.get_department().hospital.name,
                    "date": current_request.plan_request.submission_datetime.strftime("%-d %B %Y")
                                if current_request.plan_request.is_submitted else "Not submitted",


                } if current_request else None

            else:
                current_request_dict = None

            request_history = RotationRequest.objects.filter(plan_request__internship=self, month=month) \
                .exclude(plan_request=self.plan_requests.current(), response__isnull=True, forward__response__isnull=True)

            request_history_dict = [{
                "id": request.id,
                "delete": request.delete,
                "department": request.requested_department.get_department().__unicode__(),
                "shortDate": request.plan_request.submission_datetime.strftime("%-d %B")
                            if request.plan_request.is_submitted else "Not submitted",
                "fullDate": request.plan_request.submission_datetime.strftime("%-d %B %Y")
                            if request.plan_request.is_submitted else "Not submitted",
                "reviewed": request.get_status() == RotationRequest.REVIEWED_STATUS,
                "approved": request.get_response().is_approved
                            if request.get_status() == RotationRequest.REVIEWED_STATUS else False,
                "reviewDate": request.get_response().response_datetime.strftime("%-d %B %Y")
                            if request.get_status() == RotationRequest.REVIEWED_STATUS else "Pending",
            } for request in request_history]

            months.append({
                "monthLabel": month.first_day().strftime("%B %Y"),
                "month": int(month),
                "currentRotation": current_rotation_dict,
                "rotationHistory": rotation_history_dict,
                "currentRequest": current_request_dict,
                "requestHistory": request_history_dict,
            })
        return months

    def clean(self):
        """
        Checks 2 conditions:
        1- The internship plan consists of exactly 12 rotations.
        2- The internship plan achieves the minimum number of months for each required specialty.
        """
        # FIXME: Doesn't work with admin, because it checks data that's stored in the database; i.e. a ModelForm
        # can never evaluate! (e.g. the admin site)
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


class RotationManager(models.Manager):
    def current(self, month):
        try:
            return self.filter(month=month).latest("pk")  # TODO: Should be sorted by a new `addition_datetime` field
        except ObjectDoesNotExist:
            return None

    def history(self, month):
        if self.current(month):
            return self.filter(month=month).exclude(id=self.current(month).id)
        else:
            return self.none()


class Rotation(models.Model):
    internship = models.ForeignKey(Internship, related_name="rotations")
    month = MonthField()
    specialty = models.ForeignKey(Specialty, related_name="rotations")
    department = models.ForeignKey(Department, related_name="rotations")

    objects = RotationManager()

    def __unicode__(self):
        return "%s rotation in %s (%s)" % (self.specialty, self.department, self.month)


class PlanRequestManager(models.Manager):
    def current(self):
        if self.open().exists():
            return self.open().last()
        else:
            return None

    def unsubmitted(self):
        return self.filter(is_submitted=False)

    def open(self):
        return self.filter(is_closed=False)

    def closed(self):
        return self.filter(is_submitted=True, is_closed=True)


class PlanRequest(models.Model):
    internship = models.ForeignKey(Internship, related_name="plan_requests")
    creation_datetime = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)
    submission_datetime = models.DateTimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    closure_datetime = models.DateTimeField(blank=True, null=True)

    objects = PlanRequestManager()

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

        # Exclude overlapping months
        excluded_months = self.rotation_requests.values_list("month", flat=True)

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
        if self.rotation_requests.filter(response__isnull=True, forward__response__isnull=True).exists():
            return False
        else:
            self.is_closed = True

            # Set the closure time to now
            self.closure_datetime = timezone.now()

            self.save()
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

            self.save()

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

            # TODO: Test
            if is_approved:
                # Remove any previous rotation in the current month
                self.plan_request.internship.rotations.filter(month=self.month).delete()

                # Unless this is a delete, request, add a new rotation object for the current month
                if not self.delete:
                    # If the requested department is not in the database, add it.
                    # FIXME: This shouldn't be default behavior
                    if not self.requested_department.is_in_database:
                        self.requested_department.add_to_database()

                    self.plan_request.internship.rotations.create(
                        month=self.month,
                        specialty=self.specialty,
                        department=self.requested_department.get_department(),
                    )

            # Close the plan request if this is the last rotation request within it
            self.plan_request.check_closure()

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
            # TODO: Add department to database if it's not there already

            RotationRequestForward.objects.create(
                rotation_request=self,
            )

            # TODO: Notify
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
        ordering = ('plan_request', 'month', )


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
                self.rotation_request.plan_request.internship.rotations.filter(month=self.rotation_request.month).delete()

                # Unless this is a delete request, add a new rotation object for the current month
                if not self.rotation_request.delete:
                    self.rotation_request.plan_request.internship.rotations.create(
                        month=self.rotation_request.month,
                        specialty=self.rotation_request.specialty,
                        department=self.rotation_request.requested_department.get_department(),
                    )

            # Close the plan request if this is the last rotation request within it
            self.rotation_request.plan_request.check_closure()

            # TODO: Notify
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