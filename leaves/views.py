from django.contrib import messages
from django_nyt.utils import subscribe, notify
from leaves.models import LeaveType, LeaveSetting, LeaveRequest, LeaveRequestResponse, LeaveCancelRequest, \
    LeaveCancelRequestResponse, Leave
from leaves.serializers import LeaveTypeSerializer, LeaveSettingSerializer, LeaveRequestSerializer, \
    LeaveRequestResponseSerializer, LeaveCancelRequestSerializer, LeaveCancelRequestResponseSerializer, LeaveSerializer, \
    LeaveRequestSerializer2
from rest_framework import viewsets, mixins, permissions


class LeaveTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveTypeSerializer
    queryset = LeaveType.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class LeaveSettingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveSettingSerializer
    queryset = LeaveSetting.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("leaves.leave_setting.view_all"):
            return self.queryset.all()
        return self.queryset.filter(intern=self.request.user)


class LeaveRequestViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.open()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return LeaveRequestSerializer2
        return LeaveRequestSerializer

    def get_queryset(self):
        if self.request.user.has_perm("leaves.leave_request.view_all"):
            return self.queryset.all()
        return self.queryset.filter(intern=self.request.user)

    def perform_create(self, serializer):
        leave_request = serializer.save()
        self.notify_and_message(self.request, leave_request)

    def notify_and_message(self, request, leave_request):
        # Subscribe user to receive update notifications on the request
        subscribe(request.user.settings_set.first(), "leave_request_approved", object_id=leave_request.id)
        subscribe(request.user.settings_set.first(), "leave_request_declined", object_id=leave_request.id)

        # Notify medical internship unit of the request
        notify(
            "A new leave request has been submitted by %s" % (request.user.profile.get_en_full_name()),
            "rotation_request_submitted",
            url="/interns/%d/" % leave_request.intern.profile.intern.internship.id,
        )  # FIXME: avoid sending a lot of simultaneous notifications

        # Display success message to user
        messages.success(request._request, "Your request has been submitted successfully.")


class LeaveRequestResponseViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    serializer_class = LeaveRequestResponseSerializer
    queryset = LeaveRequestResponse.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("leaves.leave_request_response.view_all"):
            return self.queryset.all()
        return self.queryset.filter(request__intern=self.request.user)


class LeaveViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveSerializer
    queryset = Leave.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("leaves.leave.view_all"):
            return self.queryset.all()
        return self.queryset.filter(intern=self.request.user)


class LeaveCancelRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveCancelRequestSerializer
    queryset = LeaveCancelRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("leaves.leave_cancel_request.view_all"):
            return self.queryset.all()
        return self.queryset.filter(intern=self.request.user)


class LeaveCancelRequestResponseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveCancelRequestResponseSerializer
    queryset = LeaveCancelRequestResponse.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("leaves.leave_cancel_request_response.view_all"):
            return self.queryset.all()
        return self.queryset.filter(request__intern=self.request.user)
