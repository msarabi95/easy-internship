from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist, NON_FIELD_ERRORS
from django.db import models
from django_nyt.utils import notify

from month.models import MonthField
from accounts.models import Intern, Profile
from months.managers import FreezeManager, FreezeRequestQuerySet


class InternshipMonth(object):
    def __init__(self, intern, month):
        self.intern = intern
        self.month = month
        self.internship = self.intern.profile.intern.internship

        self.label = month.first_day().strftime("%B %Y")  # TODO: Remove
        self.label_short = month.first_day().strftime("%b. %Y")  # TODO: Remove

        self.current_rotation = self.internship.rotations.current_for_month(month)
        self.current_rotation_request = self.internship.rotation_requests.non_cancellation().current_for_month(month)
        self.current_rotation_cancel_request = self.internship.rotation_requests.cancellation().current_for_month(month)
        self.rotation_request_history = self.internship.rotation_requests.non_cancellation().month(month).closed()
        self.rotation_cancel_request_history = self.internship.rotation_requests.cancellation().month(month).closed()

        self.current_freeze = self.intern.freezes.current_for_month(month)
        self.current_freeze_request = self.intern.freeze_requests.current_for_month(month)
        self.current_freeze_cancel_request = self.intern.freeze_cancel_requests.current_for_month(month)
        self.freeze_request_history = self.intern.freeze_requests.month(month).closed()
        self.freeze_cancel_request_history = self.intern.freeze_cancel_requests.month(month).closed()

        self.current_leaves = self.intern.leaves.current_for_month(month)
        self.current_leave_requests = self.intern.leave_requests.current_for_month(month)
        self.current_leave_cancel_requests = self.intern.leave_cancel_requests.current_for_month(month)
        self.leave_request_history = self.intern.leave_requests.month(month).closed()
        self.leave_cancel_request_history = self.intern.leave_cancel_requests.month(month).closed()

        self.occupied = self.current_rotation is not None
        self.disabled = self._is_disabled()
        self.frozen = self.current_freeze is not None
        self.empty = not (self.occupied or self.disabled or self.frozen)

        self.has_rotation_request = self.current_rotation_request is not None
        self.has_rotation_cancel_request = self.current_rotation_cancel_request is not None
        self.has_freeze_request = self.current_freeze_request is not None
        self.has_freeze_cancel_request = self.current_freeze_cancel_request is not None

    def request_rotation(self):
        pass

    def request_rotation_cancel(self):
        pass

    def request_leave(self):
        pass

    def request_leave_cancel(self):
        pass

    def request_freeze(self):
        pass

    def request_freeze_cancel(self):
        pass

    def _is_disabled(self):
        """
        The last 3 months in an internship plan are disabled by default, unless there is an active freeze.
        """
        start_month = self.internship.start_month
        freeze_count = self.intern.freezes.count()
        return self.month - start_month > (11 + freeze_count)


class Internship(models.Model):
    intern = models.OneToOneField(Intern)
    start_month = MonthField()

    def __unicode__(self):
        return "Internship of %s (%s)" % (self.intern.profile.get_en_full_name(), self.intern.profile.user.username)

    def get_months(self):
        months = []
        for add in range(15):
            month = self.start_month + add
            months.append(InternshipMonth(self.intern.profile.user, month))
        return months

    months = property(get_months)

    def validate_internship_plan(self):
        """
        Checks that:
        1- The internship plan doesn't exceed 12 months.
        2- Each specialty doesn't exceed its required months in non-elective rotations.
        3- Not more than 2 months are used for electives. (Electives can be any specialty)
        """
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
            rotations = filter(lambda rotation: rotation.specialty.get_general_specialty() == specialty,
                               non_electives)
            rotation_count = len(rotations)

            if rotation_count > specialty.required_months:
                errors.append(ValidationError("The internship plan should contain at most %d month(s) of %s.",
                                              params=(specialty.required_months, specialty.name)))

            general_rotations_count = len(filter(lambda rotation: rotation.specialty == specialty, rotations))
            if rotation_count > 1 and general_rotations_count == 0:
                errors.append(
                    ValidationError(
                        "The internship plan can't have 2 sub-specialty months of %s.",
                        params=(specialty.name, )
                    )
                )

        # Check that the internship plan contains at most 2 months of electives.
        if len(electives) > 2:
            errors.append(ValidationError("The internship plan should contain at most %d month of %s.",
                                          params=(2, "electives")))

        if errors:
            raise ValidationError({
                NON_FIELD_ERRORS: errors,
            })


class Freeze(models.Model):
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='freezes')
    month = MonthField()

    freeze_request = models.OneToOneField('FreezeRequest')

    objects = FreezeManager()

    def __unicode__(self):
        return "Freeze during %s" % self.month.first_day().strftime("%B %Y")


class FreezeRequest(models.Model):
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='freeze_requests')
    month = MonthField()
    justification = models.TextField()
    submission_datetime = models.DateTimeField(auto_now_add=True)

    objects = FreezeRequestQuerySet.as_manager()

    def respond(self, is_approved, comments=""):
        """
        Respond to the freeze request; raise an error if it's already responded to.
        """
        try:
            self.response
        except ObjectDoesNotExist:
            FreezeRequestResponse.objects.create(
                request=self,
                is_approved=is_approved,
                comments=comments,
            )

            if is_approved:
                self.intern.freezes.create(
                    month=self.month,
                    freeze_request=self,
                )

            # Notify intern
            if is_approved:
                # --notifications--
                notify(
                    "Freeze request for %s has been approved." % (self.month.first_day().strftime("%B %Y")),
                    "freeze_request_approved",
                    target_object=self,
                    url="/planner/%d/" % int(self.month),
                )
            else:
                # --notifications--
                notify(
                    "Freeze request for %s has been declined." % (self.month.first_day().strftime("%B %Y")),
                    "freeze_request_declined",
                    target_object=self,
                    url="/planner/%d/freezes/history/" % int(self.month),
                )
        else:
            raise Exception("This freeze request has already been responded to.")

    def __unicode__(self):
        return "Freeze request during %s" % self.month.first_day().strftime("%B %Y")


class FreezeRequestResponse(models.Model):
    request = models.OneToOneField('FreezeRequest', related_name='response')
    is_approved = models.BooleanField()
    comments = models.TextField()
    response_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Response to %s" % self.request.__unicode__()


class FreezeCancelRequest(models.Model):
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='freeze_cancel_requests')
    month = MonthField()
    submission_datetime = models.DateTimeField(auto_now_add=True)

    objects = FreezeRequestQuerySet.as_manager()

    def respond(self, is_approved, comments=""):
        """
        Respond to the freeze cancel request; raise an error if it's already responded to.
        """
        try:
            self.response
        except ObjectDoesNotExist:
            FreezeCancelRequestResponse.objects.create(
                request=self,
                is_approved=is_approved,
                comments=comments,
            )

            if is_approved:
                self.intern.freezes.current_for_month(self.month).delete()

            # Notify intern
            if is_approved:
                # --notifications--
                notify(
                    "Your freeze during %s has been cancelled." % ( self.month.first_day().strftime("%B %Y")),
                    "freeze_cancel_request_approved",
                    target_object=self,
                    url="/planner/%d/" % int(self.month),
                )
            else:
                # --notifications--
                notify(
                    "Your request to cancel your freeze during %s has been declined." % (self.month.first_day().strftime("%B %Y")),
                    "freeze_cancel_request_declined",
                    target_object=self,
                    url="/planner/%d/freezes/history/" % int(self.month),
                )
        else:
            raise Exception("This freeze cancel request has already been responded to.")

    def __unicode__(self):
        return "Freeze cancel request during %s" % self.month.first_day().strftime("%B %Y")


class FreezeCancelRequestResponse(models.Model):
    request = models.OneToOneField(FreezeCancelRequest, related_name='response')
    is_approved = models.BooleanField()
    comments = models.TextField()
    response_datetime = models.DateTimeField(auto_now_add=True)
