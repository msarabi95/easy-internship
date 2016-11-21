from leaves.models import LeaveType, LeaveSetting, LeaveRequest, LeaveRequestResponse, Leave, LeaveCancelRequest, \
    LeaveCancelRequestResponse
from easy_internship.serializers import MonthField
from rest_framework import serializers


class LeaveTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveType
        fields = ('id', 'codename', 'name', 'max_days')


class LeaveSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveSetting
        fields = ('id', 'intern', 'type', 'max_days')


class LeaveRequestSerializer(serializers.ModelSerializer):
    month = MonthField()

    class Meta:
        model = LeaveRequest
        fields = ('id', 'intern', 'month', 'type', 'rotation_request', 'start_date',
                  'end_date', 'submission_datetime', 'cancel_requests', 'response')


class LeaveRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveRequestResponse
        fields = ('id', 'request', 'is_approved', 'comments', 'response_datetime')


class LeaveSerializer(serializers.ModelSerializer):
    month = MonthField()

    class Meta:
        model = Leave
        fields = ('id', 'intern', 'month', 'type', 'start_date', 'end_date', 'request')


class LeaveCancelRequestSerializer(serializers.ModelSerializer):
    month = MonthField()

    class Meta:
        model = LeaveCancelRequest
        fields = ('id', 'intern', 'month', 'leave_request', 'submission_datetime', 'rotation_request')


class LeaveCancelRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveCancelRequestResponse
        fields = ('id', 'request', 'is_approved', 'comments', 'response_datetime')