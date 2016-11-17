from leaves.models import LeaveType, LeaveSetting, LeaveRequest, LeaveRequestResponse, LeaveCancelRequest, \
    LeaveCancelRequestResponse, Leave
from leaves.serializers import LeaveTypeSerializer, LeaveSettingSerializer, LeaveRequestSerializer, \
    LeaveRequestResponseSerializer, LeaveCancelRequestSerializer, LeaveCancelRequestResponseSerializer, LeaveSerializer
from rest_framework import viewsets


class LeaveTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveTypeSerializer
    queryset = LeaveType.objects.all()


class LeaveSettingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveSettingSerializer
    queryset = LeaveSetting.objects.all()


class LeaveRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.all()


class LeaveRequestResponseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveRequestResponseSerializer
    queryset = LeaveRequestResponse.objects.all()


class LeaveViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveSerializer
    queryset = Leave.objects.all()


class LeaveCancelRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveCancelRequestSerializer
    queryset = LeaveCancelRequest.objects.all()


class LeaveCancelRequestResponseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveCancelRequestResponseSerializer
    queryset = LeaveCancelRequestResponse.objects.all()


