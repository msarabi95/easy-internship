from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models

from month.models import MonthField
from accounts.models import Intern


class InternshipMonth(object):
    def __init__(self, month, current_rotation, current_request, request_history,
                 current_leaves, current_leave_requests, current_leave_cancel_requests, leave_request_history,
                 leave_cancel_request_history):
        self.month = month
        self.label = month.first_day().strftime("%B %Y")
        self.label_short = month.first_day().strftime("%b. %Y")

        self.current_rotation = current_rotation
        self.current_request = current_request
        self.request_history = request_history

        self.current_leaves = current_leaves
        self.current_leave_requests = current_leave_requests
        self.current_leave_cancel_requests = current_leave_cancel_requests
        self.leave_request_history = leave_request_history
        self.leave_cancel_request_history = leave_cancel_request_history


class Internship(models.Model):
    intern = models.OneToOneField(Intern)
    start_month = MonthField()

    def get_months(self):
        months = []
        for add in range(15):
            month = self.start_month + add

            current_rotation = self.rotations.current_for_month(month)
            current_request = self.rotation_requests.current_for_month(month)
            request_history = self.rotation_requests.month(month).closed()

            current_leaves = self.intern.profile.user.leaves.current_for_month(month)
            current_leave_requests = self.intern.profile.user.leave_requests.current_for_month(month)
            current_leave_cancel_requests = self.intern.profile.user.leave_cancel_requests.current_for_month(month)
            leave_request_history = self.intern.profile.user.leave_requests.month(month).closed()
            leave_cancel_request_history = self.intern.profile.user.leave_cancel_requests.month(month).closed()

            months.append(InternshipMonth(
                month,
                current_rotation,
                current_request,
                request_history,
                current_leaves,
                current_leave_requests,
                current_leave_cancel_requests,
                leave_request_history,
                leave_cancel_request_history,
            ))
        return months

    months = property(get_months)

    def clean(self):
        """
        Checks that:
        1- The internship plan doesn't exceed 12 months.
        2- Each specialty doesn't exceed its required months in non-elective rotations.
        3- Not more than 2 months are used for electives. (Electives can be any specialty)
        """
        # FIXME: Doesn't work with admin, because it checks data that's stored in the database; i.e. a ModelForm
        # can never evaluate! (e.g. the admin site)
        errors = []
        if self.rotations.count() > 12:
            errors.append(ValidationError("The internship plan should contain no more than 12 months."))

        from hospitals.models import Specialty

        # Get a list of general specialties.
        general_specialties = Specialty.objects.general()
        non_electives = filter(lambda rotation: not rotation.is_elective, self.rotations.all())
        electives = filter(lambda rotation: rotation.is_elective, self.rotations.all())

        # Check that the internship plan contains at most 2 non-elective months of each general specialty.
        for specialty in general_specialties:
            rotation_count = len(filter(lambda rotation: rotation.specialty.get_general_specialty() == specialty,
                                        non_electives))

            if rotation_count > specialty.required_months:
                errors.append(ValidationError("The internship plan should contain at most %d month(s) of %s.",
                                              params=(specialty.required_months, specialty.name)))

        # Check that the internship plan contains at most 2 months of electives.
        if len(electives) > 2:
            errors.append(ValidationError("The internship plan should contain at most %d month of %s.",
                                          params=(2, "electives")))

        if errors:
            raise ValidationError(errors)