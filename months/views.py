from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django_nyt.utils import subscribe, notify
from month import Month
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from accounts.models import Profile
from planner.models import Internship, RotationRequest
from months.serializers import InternshipMonthSerializer, InternshipSerializer


class InternshipMonthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternshipMonthSerializer
    lookup_field = 'month'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated() and user.profile.role == Profile.INTERN:
            internship = user.profile.intern.internship
            return internship.months
        else:
            return []

    def get_object(self):
        queryset = self.get_queryset()
        month = Month.from_int(int(self.kwargs[self.lookup_field]))
        return filter(lambda m: m.month == month, queryset)[0]

    @detail_route(methods=["post"])
    def cancel_rotation(self, request, month=None):
        internship = request.user.profile.intern.internship
        month = Month.from_int(int(month))
        current_rotation = internship.rotations.current_for_month(month)

        if not current_rotation:
            raise ObjectDoesNotExist("This month has no rotation to cancel.")

        if internship.rotation_requests.current_for_month(month):
            raise PermissionDenied("There is a pending rotation request for this month already.")

        requested_department = current_rotation.rotation_request.requested_department
        requested_department.id = None
        requested_department.save()

        rr = internship.rotation_requests.create(
            month=month,
            specialty=requested_department.department_specialty,
            requested_department=requested_department,
            delete=True,
        )

        # --notifications--

        # Subscribe user to receive update notifications on the request
        subscribe(request.user.settings_set.first(), "rotation_request_approved", object_id=rr.id)
        subscribe(request.user.settings_set.first(), "rotation_request_declined", object_id=rr.id)

        # Notify medical internship unit of the request
        notify(
            "A cancellation request has been submitted by %s" % (request.user.profile.get_en_full_name()),
            "rotation_request_submitted",
            url="/planner/%d/" % rr.internship.id,
            )  # FIXME: avoid sending a lot of simultaneous notifications

        messages.success(request._request, "Your cancellation request has been submitted successfully.")

        return Response(status=HTTP_201_CREATED)


class InternshipMonthByInternshipAndId(viewsets.ViewSet):
    serializer_class = InternshipMonthSerializer

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_object(self):
        internship = get_object_or_404(Internship, pk=int(self.kwargs['internship_id']))
        month_id = int(self.kwargs['month_id'])
        return filter(lambda month: int(month.month) == month_id, internship.months)[0]


class InternshipViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternshipSerializer
    queryset = Internship.objects.all()

    @list_route(methods=['get'])
    def with_unreviewed_requests(self, request):
        internships = Internship.objects.all()
        unreviewed_requests = RotationRequest.objects.unreviewed()
        filtered = filter(lambda i: any([r in unreviewed_requests for r in i.rotation_requests.all()]), internships)
        return Response(self.get_serializer(filtered, many=True).data)