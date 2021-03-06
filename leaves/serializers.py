from month import Month

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


class LeaveCancelRequestSerializer(serializers.ModelSerializer):
    month = MonthField()

    def validate(self, data):
        """
        Check that no other open request already exists for the same leave.
        """
        leave_request = data['leave_request']

        if leave_request.cancel_requests.open().exists():
            raise serializers.ValidationError("An open cancellation request already exists for this leave.")

        return data

    class Meta:
        model = LeaveCancelRequest
        fields = '__all__'


class LeaveCancelRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveCancelRequestResponse
        fields = '__all__'


class LeaveRequestResponseSerializer(serializers.ModelSerializer):
    comments = serializers.CharField(required=False)

    class Meta:
        model = LeaveRequestResponse
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    month = MonthField()
    type = LeaveTypeSerializer()
    attachment = serializers.FileField(required=False)
    cancel_requests = LeaveCancelRequestSerializer(read_only=True, many=True)
    response = LeaveRequestResponseSerializer(read_only=True)

    def validate(self, data):
        """
        Check that:
          (1) month has a rotation (?)
          (2) intern has enough remaining days of the selected leave type
          (3) start and end date are actually within the selected month
          (4) end date is after (or equal to) start date
        """
        intern = data['intern']
        internship = intern.profile.intern.internship

        leave_type = data['type']
        leave_setting = intern.leave_settings.get(type=leave_type)

        month = data['month']
        start_date = data['start_date']
        end_date = data['end_date']

        errors = []

        if not internship.rotations.current_for_month(month):
            errors.append("This month has no rotation.")

        leave_length = (end_date - start_date).days + 1
        remaining_days = leave_setting.remaining_days
        if leave_length > remaining_days:
            errors.append("You are requesting %d days of %s, but you only have %d days available." % (
                leave_length,
                leave_type.name.lower(),
                remaining_days,
            ))

        if Month.from_date(start_date) != month:
            errors.append("Start date should be within the selected month.")

        if Month.from_date(end_date) != month:
            errors.append("End date should be within the selected month.")

        if not end_date >= start_date:
            errors.append("End date should be after or equal to start date.")

        if errors:
            raise serializers.ValidationError(errors)

        return data

    class Meta:
        model = LeaveRequest
        fields = '__all__'


class LeaveRequestSerializer2(serializers.ModelSerializer):
    intern_name = serializers.CharField(source='intern.profile.get_en_full_name')
    internship_id = serializers.IntegerField(source='intern.profile.intern.internship.id')
    month = MonthField()
    type = LeaveTypeSerializer()
    setting = LeaveSettingSerializer()
    attachment = serializers.FileField(required=False)
    duration = serializers.IntegerField()

    class Meta:
        model = LeaveRequest
        fields = '__all__'


class LeaveSerializer(serializers.ModelSerializer):
    month = MonthField()
    type = LeaveTypeSerializer()
    request = LeaveRequestSerializer()

    class Meta:
        model = Leave
        fields = '__all__'