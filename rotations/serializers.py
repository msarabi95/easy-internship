from rest_framework import serializers

from rotations.models import Rotation, RequestedDepartment, RotationRequest, RotationRequestResponse, \
    RotationRequestForward


class RotationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rotation
        fields = '__all__'


class RequestedDepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestedDepartment
        fields = '__all__'


class RotationRequestSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status', required=False)

    def get_month(self, obj):
        return int(obj.month)

    class Meta:
        model = RotationRequest
        fields = ('id', 'internship', 'month', 'specialty',
                  'requested_department', 'is_delete', 'is_elective', 'submission_datetime',
                  'status', 'response', 'forward')


class RotationRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = RotationRequestResponse
        fields = '__all__'


class RotationRequestForwardSerializer(serializers.ModelSerializer):

    class Meta:
        model = RotationRequestForward
        fields = '__all__'
