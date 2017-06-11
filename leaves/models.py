from __future__ import unicode_literals

from accounts.models import Profile
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django_nyt.utils import notify
from month.models import MonthField
from rotations.models import RotationRequest


class LeaveType(models.Model):
    """
    A global leave setting which functions as a template for intern leave settings.
    """
    codename = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=32)
    max_days = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class LeaveSetting(models.Model):
    """
    A leave setting for a particular intern.
    """
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='leave_settings')
    type = models.ForeignKey(LeaveType, related_name='leave_settings')
    max_days = models.PositiveIntegerField(blank=True, null=True)

    @property
    def confirmed_days(self):
        if self.max_days is None:
            return None
        return self.intern.leaves.filter(type=self.type).count()

    @property
    def pending_days(self):
        if self.max_days is None:
            return None
        return self.intern.leave_requests.open().filter(type=self.type).count()

    @property
    def remaining_days(self):
        if self.max_days is None:
            return None
        return self.max_days - (self.confirmed_days + self.pending_days)

    def __unicode__(self):
        return "%s setting for %s" % (self.type.name, self.intern.profile.get_en_full_name())


class LeaveRequestQuerySet(models.QuerySet):
    def month(self, month):
        """
        Return leave requests for a particular month.
        """
        return self.filter(month=month)

    def open(self):
        """
        Return leave requests that don't have a response.
        """
        return self.filter(response__isnull=True)

    def closed(self):
        """
        Return leave requests that have received response.
        """
        return self.filter(response__isnull=False)

    def current_for_month(self, month):
        """
        Return the current open requests for a specific month.
        """
        # This only has meaning when filtering requests for a specific internship
        return self.month(month).open()


class LeaveRequest(models.Model):
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='leave_requests')
    month = MonthField()
    type = models.ForeignKey(LeaveType, related_name='leave_requests')
    rotation_request = models.ForeignKey(RotationRequest, related_name='leave_requests', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    submission_datetime = models.DateTimeField(auto_now_add=True)

    objects = LeaveRequestQuerySet.as_manager()

    def respond(self, is_approved, comments=""):
        """
        Respond to the leave request; raise an error if it's already responded to.
        """
        try:
            self.response
        except ObjectDoesNotExist:
            LeaveRequestResponse.objects.create(
                request=self,
                is_approved=is_approved,
                comments=comments,
            )

            # TODO: Test
            if is_approved:
                self.intern.leaves.create(
                    month=self.month,
                    type=self.type,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    request=self,
                )

            # Notify intern
            if is_approved:
                # --notifications--
                notify(
                    "%s request #%d for %s has been approved." % (self.type.name, self.id, self.month.first_day().strftime("%B %Y")),
                    "leave_request_approved",
                    target_object=self,
                    url="/planner/%d/" % int(self.month),
                )
            else:
                # --notifications--
                notify(
                    "%s request #%d for %s has been declined." % (self.type.name, self.id, self.month.first_day().strftime("%B %Y")),
                    "leave_request_declined",
                    target_object=self,
                    url="/planner/%d/leaves/history/" % int(self.month),
                )
        else:
            raise Exception("This leave request has already been responded to.")

    def __unicode__(self):
        return "%s request during %s" % (self.type.name, self.month.first_day().strftime("%B %Y"))


class LeaveRequestResponse(models.Model):
    request = models.OneToOneField(LeaveRequest, related_name='response')
    is_approved = models.BooleanField()
    comments = models.TextField()
    response_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Response to %s" % self.request.__unicode__()


class LeaveManager(models.Manager):
    def current_for_month(self, month):
        """
        Return all the current leaves for a particular month.
        """
        # This only has meaning when filtering requests for a specific internship
        try:
            return self.filter(month=month)
        except ObjectDoesNotExist:
            return None


class Leave(models.Model):
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='leaves')
    month = MonthField()
    type = models.ForeignKey(LeaveType, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    request = models.OneToOneField(LeaveRequest, related_name='leave')

    objects = LeaveManager()

    def __unicode__(self):
        return "%s during %s" % (self.type.name, self.month.first_day().strftime("%B %Y"))


class LeaveCancelRequest(models.Model):
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='leave_cancel_requests')
    month = MonthField()
    leave_request = models.ForeignKey(LeaveRequest, related_name='cancel_requests')
    rotation_request = models.ForeignKey(RotationRequest, related_name='leave_cancel_requests', null=True, blank=True)
    submission_datetime = models.DateTimeField(auto_now_add=True)

    objects = LeaveRequestQuerySet.as_manager()

    def respond(self, is_approved, comments=""):
        """
        Respond to the leave cancel request; raise an error if it's already responded to.
        """
        try:
            self.response
        except ObjectDoesNotExist:
            LeaveCancelRequestResponse.objects.create(
                request=self,
                is_approved=is_approved,
                comments=comments,
            )

            if is_approved:
                self.leave_request.leave.delete()

            # Notify intern
            if is_approved:
                # --notifications--
                notify(
                    "Your %s during %s has been cancelled." % (self.type.name, self.month.first_day().strftime("%B %Y")),
                    "leave_cancel_request_approved",
                    target_object=self,
                    url="/planner/%d/" % int(self.month),
                )
            else:
                # --notifications--
                notify(
                    "Your request to cancel your %s during %s has been declined." % (self.type.name, self.month.first_day().strftime("%B %Y")),
                    "leave_cancel_request_declined",
                    target_object=self,
                    url="/planner/%d/leaves/history/" % int(self.month),
                )
        else:
            raise Exception("This leave cancel request has already been responded to.")

    def __unicode__(self):
        return "Cancellation request for %s during %s" % (
            self.original_request.type.name,
            self.original_request.month.first_day().strftime("%B %Y")
        )


class LeaveCancelRequestResponse(models.Model):
    request = models.OneToOneField(LeaveCancelRequest, related_name='response')
    is_approved = models.BooleanField()
    comments = models.TextField()
    response_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Response to cancellation request for %s during %s" % (
            self.request.original_request.type.name,
            self.request.original_request.month.first_day().strftime("%B %Y")
        )
