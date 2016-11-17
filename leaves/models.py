from __future__ import unicode_literals

from accounts.models import Profile
from django.contrib.auth.models import User
from django.db import models
from month.models import MonthField
from planner.models import RotationRequest


class LeaveType(models.Model):
    """
    A global leave setting which functions as a template for intern leave settings.
    """
    codename = models.CharField(max_length=16)
    name = models.CharField(max_length=32)
    max_days = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name


class LeaveSetting(models.Model):
    """
    A leave setting for a particular intern.
    """
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='leave_settings')
    type = models.ForeignKey(LeaveType, related_name='leave_settings')
    max_days = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s setting for %s" % (self.type.name, self.user.profile.get_en_full_name())


class LeaveRequest(models.Model):
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='leave_requests')
    month = MonthField()
    type = models.ForeignKey(LeaveType, related_name='leave_requests')
    rotation_request = models.ForeignKey(RotationRequest, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    submission_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s request during %s" % (self.type.name, self.month.first_day().strftime("%B %Y"))


class LeaveRequestResponse(models.Model):
    request = models.OneToOneField(LeaveRequest, related_name='response')
    is_approved = models.BooleanField()
    comments = models.TextField()
    response_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Response to %s" % self.request.__unicode__()


class Leave(models.Model):
    intern = models.ForeignKey(User, limit_choices_to={'profile__role': Profile.INTERN}, related_name='leaves')
    month = MonthField()
    type = models.ForeignKey(LeaveType, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    request = models.OneToOneField(LeaveRequest, related_name='leave')

    def __unicode__(self):
        return "%s during %s" % (self.type.name, self.month.first_day().strftime("%B %Y"))


class LeaveCancelRequest(models.Model):
    original_request = models.ForeignKey(LeaveRequest, related_name='cancel_requests')
    submission_datetime = models.DateTimeField(auto_now_add=True)
    rotation_request = models.ForeignKey(RotationRequest, related_name='leave_cancel_requests', null=True, blank=True)

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
