from rest_framework import serializers

from planner.models import Rotation, RequestedDepartment, RotationRequest, RotationRequestResponse, \
    RotationRequestForward, RotationRequestForwardResponse


class RotationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rotation
        fields = ('id', 'internship', 'month', 'specialty', 'department', 'is_elective', 'rotation_request')


class RequestedDepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestedDepartment
        fields = ('id', 'is_in_database', 'department', 'department_hospital',
                  'department_name', 'department_specialty', 'department_contact_name',
                  'department_email', 'department_phone', 'department_extension')


class RotationRequestSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    submission_datetime = serializers.DateTimeField(format="%A, %-d %B %Y, %-I:%M %p")
    status = serializers.CharField(source='get_status', required=False)

    def get_month(self, obj):
        return int(obj.month)

    class Meta:
        model = RotationRequest
        fields = ('id', 'internship', 'month', 'specialty',
                  'requested_department', 'delete', 'is_elective', 'submission_datetime',
                  'status', 'response', 'forward')


class RotationRequestResponseSerializer(serializers.ModelSerializer):
    response_datetime = serializers.DateTimeField(format="%A, %-d %B %Y, %-I:%M %p")

    class Meta:
        model = RotationRequestResponse
        fields = ('id', 'rotation_request', 'is_approved', 'comments', 'response_datetime')


class RotationRequestForwardSerializer(serializers.ModelSerializer):

    class Meta:
        model = RotationRequestForward
        fields = ('id', 'key', 'rotation_request', 'forward_datetime', 'response')


class RotationRequestForwardResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = RotationRequestForwardResponse
        fields = ('id', 'forward', 'is_approved', 'response_memo', 'comments',
                  'respondent_name', 'response_datetime')