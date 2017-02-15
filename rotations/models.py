from __future__ import unicode_literals

from copy import copy

import itertools
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django_nyt.utils import notify
from month.models import MonthField

from months.models import Internship
from rotations.managers import RotationManager, RotationRequestQuerySet


class Rotation(models.Model):
    internship = models.ForeignKey(Internship, related_name="rotations")
    month = MonthField()
    hospital = models.ForeignKey('hospitals.Hospital', related_name="rotations")
    specialty = models.ForeignKey('hospitals.Specialty', related_name="rotations")
    location = models.ForeignKey('hospitals.Location', related_name="rotations", null=True, blank=True)
    is_elective = models.BooleanField(default=False)
    rotation_request = models.OneToOneField("RotationRequest")

    objects = RotationManager()

    def __unicode__(self):
        return "%s rotation in %s (%s)" % (self.specialty, self.department, self.month)


class RotationRequest(models.Model):
    internship = models.ForeignKey(Internship, related_name="rotation_requests")
    month = MonthField()
    hospital = models.ForeignKey('hospitals.Hospital', related_name="rotation_requests")
    specialty = models.ForeignKey('hospitals.Specialty', related_name="rotation_requests")
    location = models.ForeignKey('hospitals.Location', related_name="rotation_requests", null=True, blank=True)
    is_delete = models.BooleanField(default=False)  # Flag to determine if this is a "delete" request
    is_elective = models.BooleanField(default=False)
    submission_datetime = models.DateTimeField(auto_now_add=True)

    objects = RotationRequestQuerySet().as_manager()

    PENDING_STATUS = "P"
    FORWARDED_STATUS = "F"
    REVIEWED_STATUS = "R"

    def validate_request(self):
        """
        Checks that:
        1- The rotation request alters the internship plan in a way that keeps it at 12 rotations or less.
        2- The rotation request alters the internship plan in a way that doesn't exceed the maximum number of months
         for each required specialty.
        """
        predicted_plan = self.get_predicted_plan()
        predicted_plan.validate_internship_plan()

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

            for request in self.internship.rotation_requests.open().filter(is_delete=False)
        ]

        # Don't forget this rotation request (self), since it's not yet saved when this is running
        if not self.is_delete:
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
        (3) Reviewed: if the request has received a response
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

        except ObjectDoesNotExist:
            has_forward = False

        # Return the appropriate status based on the presence/absence of the response,
        # forward, and forward response
        if not has_response and not has_forward:
            return self.PENDING_STATUS

        elif has_forward and not has_response:
            return self.FORWARDED_STATUS

        elif has_response:
            return self.REVIEWED_STATUS

    def __unicode__(self):
        return "Request for %s rotation at %s (%s)" % (self.specialty.name,
                                                       self.hospital.name,
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
    rotation_request = models.OneToOneField(RotationRequest, related_name="forward", limit_choices_to={'is_delete': False})
    forward_datetime = models.DateTimeField(auto_now_add=True)
    memo_file = models.FileField(upload_to='forward_memos')  # TODO: validate file extension
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Forward of request #%d" % self.rotation_request.id


class AcceptanceList(object):
    def __init__(self, department, month,
                 auto_accepted=None, auto_declined=None, manual_accepted=None, manual_declined=None,
                 rotation_requests_cache=None, acceptance_settings_cache=None):
        self.department = department
        self.month = month

        self.rotation_requests_cache = rotation_requests_cache
        self.acceptance_settings_cache = acceptance_settings_cache

        acceptance_setting = self.get_acceptance_setting()

        self.acceptance_criterion = acceptance_setting.criterion
        self.acceptance_is_open = acceptance_setting.can_submit_requests()
        self.acceptance_start_or_end_date = acceptance_setting.start_or_end_date

        self.total_seats = acceptance_setting.total_seats
        self.unoccupied_seats = acceptance_setting.get_unoccupied_seats()

        requests = self.get_sorted_rotation_requests()
        self.booked_seats = len(requests)

        self.default_auto_accepted = requests[:self.unoccupied_seats]
        self.default_auto_declined = requests[self.unoccupied_seats:]

        self.auto_accepted = self.default_auto_accepted if not auto_accepted else auto_accepted
        self.auto_declined = self.default_auto_declined if not auto_declined else auto_declined

        self.manual_accepted = manual_accepted or []
        self.manual_declined = manual_declined or []

        self.verify()
    
    def verify(self):
        # Verification
        # (1) All contents should be instances of RotationRequest
        # (2) No one request should be duplicated in any part
        # (3) No one request is found in any place except default or opposite list
        #     (e.g. `auto_accepted` or `manual_decline`)
        request_lists = [self.auto_accepted, self.auto_declined, self.manual_accepted, self.manual_declined]
        opposites = [
            {'lists': [self.auto_accepted, self.manual_declined], 'reference': self.default_auto_accepted},
            {'lists': [self.auto_declined, self.manual_accepted], 'reference': self.default_auto_declined},
        ]
        for request_list in request_lists:
            for request in request_list:
                assert isinstance(request, RotationRequest), \
                    "Members of an AcceptanceList should be instances of `RotationRequest`."
                assert not any([request in rl for rl in request_lists if rl != request_list]),\
                    "A rotation request can't be present in more than one branch of an acceptance list."
        for combination in opposites:
            combined = itertools.chain(*combination['lists'])
            assert all([request in combination['reference'] for request in combined]),\
                "Requests should only be positioned in their default or opposite lists."

    def get_acceptance_setting(self):
        if self.acceptance_settings_cache:
            filtered = filter(
                lambda setting: setting.department == self.department and setting.month == self.month,
                self.acceptance_settings_cache
            )
            assert len(filtered) == 1, "Unexpected number of filtered cached acceptance settings."
            assert filtered[0].total_seats is not None,\
                "A number of seats should be specified in order to make an acceptance list."
            return filtered[0]
        else:
            from hospitals.models import AcceptanceSetting
            return AcceptanceSetting(self.department, self.month)

    def get_sorted_rotation_requests(self):
        from hospitals.models import FCFS_ACCEPTANCE, GPA_ACCEPTANCE
        assert self.acceptance_criterion == FCFS_ACCEPTANCE or self.acceptance_criterion == GPA_ACCEPTANCE

        if self.rotation_requests_cache:
            rotation_requests = filter(
                lambda rr: rr.requested_department.department == self.department and rr.month == self.month,
                self.rotation_requests_cache,
            )
            rotation_requests = sorted(
                rotation_requests,
                key=lambda rr: rr.submission_datetime if self.acceptance_criterion == FCFS_ACCEPTANCE else -rr.internship.intern.gpa,
            )
            return rotation_requests
        else:
            order_field = \
                "submission_datetime" if self.acceptance_criterion == FCFS_ACCEPTANCE else "-internship__intern__gpa"
            return RotationRequest.objects.unreviewed().filter(is_delete=False)\
                        .filter(requested_department__department=self.department, month=self.month)\
                        .order_by(order_field)

    def respond_all(self):
        """
        Respond to all the requests in the Acceptance List appropriately.
        """
        # Verifications
        # (1) Redo general verifications to account for updates to the lists
        self.verify()
        # (2) All manually determined requests should have comments attached to them
        all_requests = self.auto_accepted + self.auto_declined + self.manual_accepted + self.manual_declined
        manual_requests = self.manual_accepted + self.manual_declined
        for request in manual_requests:
            assert hasattr(request, 'response'), "A manually determined request should have a comment attached."
            assert request.response.comments.strip(), "Comment can't be empty."

        responses = list()
        rotations = list()
        for request in self.auto_accepted:
            if hasattr(request, 'response'):
                response = request.response
                response.is_approved = True
            else:
                response = RotationRequestResponse(
                    rotation_request=request,
                    is_approved=True,
                    comments="",
                )
            responses.append(response)

            rotations.append(Rotation(
                internship=request.internship,
                month=request.month,
                department=request.requested_department.department,
                specialty=request.specialty,
                is_elective=request.is_elective,
                rotation_request=request,
            ))

        for request in self.auto_declined:
            if hasattr(request, 'response'):
                response = request.response
                response.is_approved = False
            else:
                response = RotationRequestResponse(
                    rotation_request=request,
                    is_approved=False,
                    comments="",
                )
            responses.append(response)

        for request in self.manual_accepted:
            response = request.response
            response.is_approved = True
            responses.append(response)

            rotations.append(Rotation(
                internship=request.internship,
                month=request.month,
                department=request.requested_department.department,
                specialty=request.specialty,
                is_elective=request.is_elective,
                rotation_request=request,
            ))

        for request in self.manual_declined:
            response = request.response
            response.is_approved = False
            responses.append(response)

        RotationRequestResponse.objects.bulk_create(responses)
        Rotation.objects.bulk_create(rotations)

        for rotation_request in all_requests:
            if rotation_request.response.is_approved:
                notify(
                    "Rotation request %d for %s has been approved." % (rotation_request.id, rotation_request.month.first_day().strftime("%B %Y")),
                    "rotation_request_approved",
                    target_object=rotation_request,
                    url="/planner/%d/" % int(rotation_request.month),
                )
            else:
                notify(
                    "Rotation request %d for %s has been declined." % (rotation_request.id, rotation_request.month.first_day().strftime("%B %Y")),
                    "rotation_request_declined",
                    target_object=rotation_request,
                    url="/planner/%d/history/" % int(rotation_request.month),
                )

    def __repr__(self):
        return "<%s: Acceptance List for %s during %s>" % \
               (self.__class__.__name__, self.department.__unicode__(), self.month.first_day().strftime("%B %Y"))
