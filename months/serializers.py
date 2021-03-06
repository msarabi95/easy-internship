from rest_framework import serializers
from rest_framework.fields import empty

from accounts.serializers import FullInternSerializer
from easy_internship.serializers import MonthField
from leaves.serializers import LeaveSerializer, LeaveRequestSerializer, LeaveCancelRequestSerializer
from months.models import Internship, Freeze, FreezeRequest, FreezeRequestResponse, FreezeCancelRequest, \
    FreezeCancelRequestResponse
from rotations.serializers import RotationSerializer2, RotationRequestSerializer2


class FreezeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freeze
        fields = '__all__'


class FreezeRequestSerializer(serializers.ModelSerializer):
    month = MonthField()
    intern_name = serializers.CharField(source='intern.profile.get_en_full_name')
    internship_id = serializers.IntegerField(source='intern.profile.intern.internship.id')
    gpa = serializers.FloatField(source='intern.profile.intern.gpa')
    response = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FreezeRequest
        fields = '__all__'


class FreezeRequestResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezeRequestResponse
        fields = '__all__'


class FreezeCancelRequestSerializer(serializers.ModelSerializer):
    month = MonthField()
    intern_name = serializers.CharField(source='intern.profile.get_en_full_name')
    internship_id = serializers.IntegerField(source='intern.profile.intern.internship.id')
    gpa = serializers.FloatField(source='intern.profile.intern.gpa')
    response = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FreezeCancelRequest
        fields = '__all__'


class FreezeCancelRequestResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezeCancelRequestResponse
        fields = '__all__'


class FreezeRequestSerializer2(FreezeRequestSerializer):
    response = FreezeRequestResponseSerializer()

    class Meta(FreezeRequestSerializer.Meta):
        pass


class FreezeCancelRequestSerializer2(FreezeCancelRequestSerializer):
    response = FreezeCancelRequestResponseSerializer()

    class Meta(FreezeCancelRequestSerializer.Meta):
        pass


class InternshipMonthSerializer(serializers.Serializer):
    intern = serializers.PrimaryKeyRelatedField(read_only=True)
    month = serializers.IntegerField(read_only=True)

    label = serializers.CharField(read_only=True)
    label_short = serializers.CharField(read_only=True)

    current_rotation = RotationSerializer2()
    current_rotation_request = RotationRequestSerializer2()
    current_rotation_cancel_request = RotationRequestSerializer2()
    rotation_request_history = RotationRequestSerializer2(many=True)
    rotation_cancel_request_history = RotationRequestSerializer2(many=True)

    current_freeze = FreezeSerializer()
    current_freeze_request = FreezeRequestSerializer2()
    current_freeze_cancel_request = FreezeCancelRequestSerializer2()
    freeze_request_history = FreezeRequestSerializer2(many=True)
    freeze_cancel_request_history = FreezeCancelRequestSerializer2(many=True)

    current_leaves = LeaveSerializer(many=True)
    current_leave_requests = LeaveRequestSerializer(many=True)
    current_leave_cancel_requests = LeaveCancelRequestSerializer(many=True)
    leave_request_history = LeaveRequestSerializer(many=True)
    leave_cancel_request_history = LeaveCancelRequestSerializer(many=True)

    empty = serializers.BooleanField(read_only=True)
    occupied = serializers.BooleanField(read_only=True)
    disabled = serializers.BooleanField(read_only=True)
    frozen = serializers.BooleanField(read_only=True)

    has_rotation_request = serializers.BooleanField(read_only=True)
    has_rotation_cancel_request = serializers.BooleanField(read_only=True)
    has_freeze_request = serializers.BooleanField(read_only=True)
    has_freeze_cancel_request = serializers.BooleanField(read_only=True)

    has_leaves = serializers.BooleanField(read_only=True)
    has_leave_requests = serializers.BooleanField(read_only=True)
    has_leave_cancel_requests = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class InternshipSerializer(serializers.ModelSerializer):

    def __init__(self, instance=None, data=empty, details=True, *args, **kwargs):
        super(InternshipSerializer, self).__init__(instance, data, *args, **kwargs)
        if details:
            self.fields['months'] = InternshipMonthSerializer(many=True)
            self.fields['rotation_requests'] = RotationRequestSerializer2(many=True)

    intern = FullInternSerializer()

    class Meta:
        model = Internship
        fields = '__all__'


class FullInternshipSerializer2(serializers.ModelSerializer):
    intern = FullInternSerializer()
    months = InternshipMonthSerializer(many=True)

    class Meta:
        model = Internship
