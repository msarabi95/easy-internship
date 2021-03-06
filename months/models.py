from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist, NON_FIELD_ERRORS, MultipleObjectsReturned
from django.db import models
from django_nyt.utils import notify

from month.models import MonthField
from accounts.models import Intern, Profile
from months.managers import FreezeManager, FreezeRequestQuerySet


class InternshipMonth(object):
    def __init__(self, internship, month):
        self.intern = internship.intern.profile.user
        self.month = month
        self.internship = internship

        self.label = month.first_day().strftime("%B %Y")  # TODO: Remove
        self.label_short = month.first_day().strftime("%b. %Y")  # TODO: Remove

        self.current_rotation = self._current_for_month(self.internship.rotations.all())
        self.current_rotation_request = self._current_for_month(self._is_delete(self.internship.rotation_requests.all(), False))
        self.current_rotation_cancel_request = self._current_for_month(self._is_delete(self.internship.rotation_requests.all(), True))
        self.rotation_request_history = self._closed(self._month(self._is_delete(self.internship.rotation_requests.all(), False)))
        self.rotation_cancel_request_history = self._closed(self._month(self._is_delete(self.internship.rotation_requests.all(), True)))

        self.current_freeze = self._current_for_month(self.intern.freezes.all())
        self.current_freeze_request = self._current_for_month(self.intern.freeze_requests.all())
        self.current_freeze_cancel_request = self._current_for_month(self.intern.freeze_cancel_requests.all())
        self.freeze_request_history = self._closed(self._month(self.intern.freeze_requests.all()))
        self.freeze_cancel_request_history = self._closed(self._month(self.intern.freeze_cancel_requests.all()))

        self.current_leaves = self._current_for_month(self.intern.leaves.all(), allow_many=True)
        self.current_leave_requests = self._current_for_month(self.intern.leave_requests.all(), allow_many=True)
        self.current_leave_cancel_requests = self._current_for_month(self.intern.leave_cancel_requests.all(), allow_many=True)
        self.leave_request_history = self._closed(self._month(self.intern.leave_requests.all()))
        self.leave_cancel_request_history = self._closed(self._month(self.intern.leave_cancel_requests.all()))

        self.has_rotation_request = self.current_rotation_request is not None
        self.has_rotation_cancel_request = self.current_rotation_cancel_request is not None
        self.has_freeze_request = self.current_freeze_request is not None
        self.has_freeze_cancel_request = self.current_freeze_cancel_request is not None

        self.occupied = self.current_rotation is not None
        self.disabled = self._is_disabled()
        self.frozen = self.current_freeze is not None
        self.empty = not (self.occupied or self.disabled or self.frozen)

        self.has_leaves = bool(self.current_leaves)
        self.has_leave_requests = bool(self.current_leave_requests)
        self.has_leave_cancel_requests = bool(self.current_leave_cancel_requests)

    def _current_for_month(self, items, allow_many=False):
        """
        Return the instance(s) of the iterable corresponding to the current month.
        Return `None` if it doesn't exist.
        `allow_many` flag determines if only one instance is allowed per month, or if multiple instances are OK.
        """
        filtered = self._open(self._month(items))
        count = len(filtered)
        if allow_many:
            return filtered
        elif count > 1:
            raise MultipleObjectsReturned(
                "Expected at most 1 item for the month %s, found %d!" % (
                    self.month.first_day().strftime("%B %Y"),
                    count,
                )
            )
        elif count == 1:
            return filtered[0]
        else:
            return None

    def _open(self, items):
        """
        Filter out open requests from a list of requests and return them.
        """
        return filter(
            lambda request: not hasattr(request, 'response'),
            items,
        )

    def _closed(self, items):
        """
        Filter out closed requests from a list of requests and return them.
        """
        return filter(
            lambda request: hasattr(request, 'response'),
            items,
        )

    def _month(self, items):
        """
        Filter out items related to the current month and return them.
        """
        return filter(
            lambda item: item.month == self.month,
            items,
        )

    def _is_delete(self, items, is_delete):
        """
        Filter out rotation requests according to the `is_delete` flag.
        """
        return filter(
            lambda request: request.is_delete == is_delete,
            items,
        )

    def _is_disabled(self):
        """
        The last 3 months in an internship plan are disabled by default, unless there is an active freeze.
        """
        start_month = self.internship.start_month
        freeze_count = self.intern.freezes.count()
        if self.month - start_month > (11 + freeze_count):
            return True
        elif self.intern.profile.intern.is_outside_intern and not self.occupied and not (self.has_rotation_request or self.has_rotation_cancel_request):
            rotation_count = self.internship.rotations.count()
            request_count = self.internship.rotation_requests.open().count()
            return rotation_count + request_count >= 6
        return False  # FIXME: Investigate why this actually works!


class Internship(models.Model):
    intern = models.OneToOneField(Intern)
    start_month = MonthField()

    def __unicode__(self):
        return "Internship of %s (%s)" % (self.intern.profile.get_en_full_name(), self.intern.profile.user.username)

    def get_months(self):
        months = []
        for add in range(15):
            month = self.start_month + add
            months.append(InternshipMonth(self, month))
        return months

    months = property(get_months)

    def validate_internship_plan(self):
        """
        For KSAU-HS and AGU interns, checks that:
        1- The internship plan doesn't exceed 12 months.
        2- Each specialty doesn't exceed its required months in non-elective rotations.
        3- Not more than 2 months are used for electives. (Electives can be any specialty)

        For outside interns, checks that rotation count does not exceed 6 months.
        """
        errors = []

        if self.intern.is_ksauhs_intern or self.intern.is_agu_intern:
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

        elif self.intern.is_outside_intern:
            if self.rotations.count() > 6:
                errors.append(ValidationError("You can have up to 6 months of rotations only."))

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
    comments = models.TextField(blank=True)
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
    comments = models.TextField(blank=True)
    response_datetime = models.DateTimeField(auto_now_add=True)
