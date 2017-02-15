from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from months.models import Internship, Freeze, FreezeRequest, FreezeRequestResponse, FreezeCancelRequest, \
    FreezeCancelRequestResponse


class InternshipMonthSerializer(serializers.Serializer):
    intern = serializers.PrimaryKeyRelatedField(read_only=True)
    month = serializers.IntegerField(read_only=True)
    internship = serializers.PrimaryKeyRelatedField(read_only=True)

    label = serializers.CharField(read_only=True)
    label_short = serializers.CharField(read_only=True)

    current_rotation = serializers.PrimaryKeyRelatedField(read_only=True)
    current_rotation_request = serializers.PrimaryKeyRelatedField(read_only=True)
    current_rotation_cancel_request = serializers.PrimaryKeyRelatedField(read_only=True)
    rotation_request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    rotation_cancel_request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    current_leaves = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    current_leave_requests = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    current_leave_cancel_requests = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    leave_request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    leave_cancel_request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    current_freeze = serializers.PrimaryKeyRelatedField(read_only=True)
    current_freeze_request = serializers.PrimaryKeyRelatedField(read_only=True)
    current_freeze_cancel_request = serializers.PrimaryKeyRelatedField(read_only=True)
    freeze_request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    freeze_cancel_request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    empty = serializers.BooleanField(read_only=True)
    occupied = serializers.BooleanField(read_only=True)
    disabled = serializers.BooleanField(read_only=True)
    frozen = serializers.BooleanField(read_only=True)

    has_rotation_request = serializers.BooleanField(read_only=True)
    has_rotation_cancel_request = serializers.BooleanField(read_only=True)
    has_freeze_request = serializers.BooleanField(read_only=True)
    has_freeze_cancel_request = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class InternshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Internship
        fields = ('id', 'intern', 'start_month', 'rotation_requests', )


class FreezeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Freeze
        fields = '__all__'


class FreezeRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FreezeRequest
        fields = ('id', 'intern', 'month', 'justification', 'submission_datetime', 'response')


class FreezeRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = FreezeRequestResponse
        fields = '__all__'


class FreezeCancelRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FreezeCancelRequest
        fields = '__all__'


class FreezeCancelRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = FreezeCancelRequestResponse
        fields = '__all__'
