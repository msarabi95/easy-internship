from __future__ import unicode_literals

from accounts.models import Intern
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone
from month.models import MonthField


# 3 types of TODO's:
# 1- Method TODO's
# 2- Test TODO's
# 3- Question TODO's


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
                                         blank=True)  # TODO: confirm if this works??

    def is_subspecialty(self):
        """
        Return True if the specialty has a parent_specialty.
        """
        # TODO:
        # 1- Test with general specialty (no parent)
        # 2- Test with subspecialty (with parent)
        if self.parent_specialty is not None:
            return True
        else:
            return False

    def get_general_specialty(self):
        """
        Return `self` if already a general specialty (no parent specialty).
        Return parent specialty otherwise.
        """
        # TODO:
        # 1- Test with general specialty (no parent)
        # 2- Test with subspecialty (with parent)
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
                                          blank=True)  # TODO: confirm if this works??
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
        # TODO: Test
        return self.seats.filter(month=month).available_seat_count

    def get_contact_details(self):
        """
        Return the contact details of the department if saved.
        If no details are supplied, return the details of the parent department.
        """
        # TODO: Test
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
    specialty = models.ForeignKey(Specialty, related_name="seats")
    department = models.ForeignKey(Department, related_name="seats")
    available_seat_count = models.PositiveIntegerField()

    def __unicode__(self):
        return "Seat availability for %s in %s during %s" % (self.specialty.name,
                                                             self.department.__unicode__(),
                                                             self.month)


class Internship(models.Model):
    intern = models.OneToOneField(Intern)
    start_month = MonthField()

    def clean(self):
        """
        Checks 2 conditions:
        1- The internship plan consists of exactly 12 rotations.
        2- The internship plan achieves the minimum number of months for each required specialty.
        """
        # TODO: Test
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
    submission_datetime = models.DateTimeField()
    is_closed = models.BooleanField(default=False)
    closure_datetime = models.DateTimeField()

    def get_predicted_plan(self):
        """
        Returns an `Internship` object representing what the internship plan will look like
        if all the rotation requests in this plan request are accepted.
        """
        # TODO: Test!

        # Make a list of new rotation objects based on the rotation requests attached to the
        # plan request
        updated_rotations = [
            Rotation(internship=self.internship,
                     month=request.month,
                     department=request.requested_department.get_department(),
                     specialty=request.specialty)
            
            for request in self.rotation_requests.all()
        ]

        # The updated rotations should remove older rotations that share the same months, so exclude those
        # Beware that the internship plan should exist in one of 2 states:
        # 1- Either it's empty (a new plan)
        # 2- Or it's full (12 months)
        # To avoid throwing a DoesNotExist error, this statement should only be called with a full plan.
        excluded_pks = [
            self.internship.rotations.get(month=rotation.month).pk for rotation in updated_rotations
        ] if self.internship.rotations.exists() else []

        # FIXME: If the request contains a rotation request that changes a rotation to a new month
        # (e.g. internship freeze):
        # 1- The previous statement will throw a DoesNotExist error when it reaches that new month
        # 2- How will this updated be handled? (There's no "old" month to override.)

        # To make the final list of the updated rotations, add the existing unaffected rotations to the
        # list of new ones
        updated_rotations.extend(self.internship.rotations.exclude(id__in=excluded_pks))

        # Make a copy of the internship object
        predicted = self.internship
        predicted.pk = None
        predicted.intern = None

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
        1- The plan request contains at least 1 rotation request, and at most 12.
        2- The plan request alters the internship plan in a way that keeps it at exactly 12 rotations.
        3- The plan request alters the internship plan in a way that achieves the minimum number of months for
         each required specialty.
        """
        # TODO: Test with a "clean" object + each of the conditions violated
        # This checks for condition 1
        if not self.rotation_requests.exists():
            raise ValidationError("The plan request should contain at least 1 rotation request.")

        # This checks for conditions 2 & 3
        predicted_plan = self.get_predicted_plan()
        predicted_plan.full_clean()

    def check_closure(self):
        """
        Returns whether the current plan request has been closed or not.
        """
        # TODO:
        # 1- Test with closed plan request
        # 2- Test with ("partially") open plan request (some requests responded to, some not)
        # 3- Test with ("fully") open plan request (no responses at all)
        if self.rotation_requests.filter(response__isnull=True).exists():
            return False
        else:
            self.is_closed = True
            self.closure_datetime = timezone.now()  # FIXME: This date should = date of the last closed rotation request
            return True

    def submit(self):
        """
        Submit the plan request for review.
        """
        # TODO:
        # 1- Test with unsubmitted plan request
        # 2- Test with already submitted plan request
        if not self.is_submitted:
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
        # TODO
        pass

    def link_to_existing_department(self, department):
        """
        Clears all the department_* details fields and links to an existing department through
         the `department` field.
        """
        # TODO:
        # 1- Test with a database department
        # 2- Test with a department object that doesn't exist in the database
        if department in Department.objects.all():
            self.__dict__.update({
                "department": department,
                "is_in_database": True,
                "department_hospital": None,
                "department_name": "",
                "department_specialty": None,
                "department_contact_name": "",
                "department_email": "",
                "department_phone": "",
                "department_extension": "",
            })
            self.save()
        else:
            raise ObjectDoesNotExist("This department doesn't exist in the database.")

    def add_to_database(self):
        """
        Create a new department based on the data in this request, then link the request to that
        department and clear the department_* details fields.
        """
        # TODO:
        # 1- Test with a department that doesn't exist in the db
        # 2- Test with one that does
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

    def get_status(self):
        # TODO
        pass

    def get_details(self):
        # TODO
        pass

    def respond(self, is_approved):
        # TODO
        pass

    def forward(self):
        # TODO
        pass

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

    def respond(self, is_approved):
        # TODO
        pass

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
