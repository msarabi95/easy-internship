from leaves.models import LeaveType, LeaveSetting, LeaveRequest, LeaveRequestResponse, Leave, LeaveCancelRequest, \
    LeaveCancelRequestResponse
from easy_internship.serializers import MonthField
from rest_framework import serializers


class LeaveTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveSettingSerializer(serializers.ModelSerializer):
    type = LeaveTypeSerializer()
    confirmed_days = serializers.IntegerField()
    pending_days = serializers.IntegerField()
    remaining_days = serializers.IntegerField()

    class Meta:
        model = LeaveSetting
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    month = MonthField()

    class Meta:
        model = LeaveRequest
        fields = ('id', 'intern', 'month', 'type', 'rotation_request', 'start_date',
                  'end_date', 'submission_datetime', 'cancel_requests', 'response')


class LeaveRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveRequestResponse
        fields = '__all__'


class LeaveSerializer(serializers.ModelSerializer):
    month = MonthField()

    class Meta:
        model = Leave
        fields = '__all__'


class LeaveCancelRequestSerializer(serializers.ModelSerializer):
    month = MonthField()

    class Meta:
        model = LeaveCancelRequest
        fields = '__all__'


class LeaveCancelRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveCancelRequestResponse
        fields = '__all__'