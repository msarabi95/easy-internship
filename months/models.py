from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
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
        self.current_request = self.internship.rotation_requests.current_for_month(month)
        self.request_history = self.internship.rotation_requests.month(month).closed()

        self.current_leaves = self.intern.leaves.current_for_month(month)
        self.current_leave_requests = self.intern.leave_requests.current_for_month(month)
        self.current_leave_cancel_requests = self.intern.leave_cancel_requests.current_for_month(month)
        self.leave_request_history = self.intern.leave_requests.month(month).closed()
        self.leave_cancel_request_history = self.intern.leave_cancel_requests.month(month).closed()

        self.current_freeze = self.intern.freezes.current_for_month(month)
        self.current_freeze_request = self.intern.freeze_requests.current_for_month(month)
        self.current_freeze_cancel_request = self.intern.freeze_cancel_requests.current_for_month(month)
        self.freeze_request_history = self.intern.freeze_requests.month(month).closed()
        self.freeze_cancel_request_history = self.intern.freeze_cancel_requests.month(month).closed()

        self.occupied = self.current_rotation is not None
        self.requested = self.current_request is not None
        self.disabled = self._is_disabled()
        self.frozen = self.current_freeze is not None

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
