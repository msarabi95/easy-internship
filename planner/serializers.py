from planner.models import RotationRequest, RotationRequestForward, Rotation, Hospital, Specialty, \
    Department, Internship, RequestedDepartment, RotationRequestResponse, RotationRequestForwardResponse, \
    SeatAvailability
from rest_framework import serializers


class HospitalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hospital
        fields = ('id', 'name', 'abbreviation', 'is_kamc')


class SpecialtySerializer(serializers.ModelSerializer):

    class Meta:
        model = Specialty
        fields = ('id', 'name', 'abbreviation', 'required_months', 'parent_specialty')


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id', 'hospital', 'parent_department', 'name', 'specialty', 'contact_name',
                  'email', 'phone', 'extension')


class SeatAvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = SeatAvailability
        fields = ('id', 'month', 'specialty', 'department', 'available_seat_count')


class InternshipMonthSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    label = serializers.CharField()
    current_rotation = serializers.PrimaryKeyRelatedField(read_only=True)
    current_request = serializers.PrimaryKeyRelatedField(read_only=True)
    request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class InternshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Internship
        fields = ('id', 'intern', 'start_month')


class RotationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rotation
        fields = ('id', 'internship', 'month', 'specialty', 'department')


class RequestedDepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestedDepartment
        fields = ('id', 'is_in_database', 'department', 'department_hospital',
                  'department_name', 'department_specialty', 'department_contact_name',
                  'department_email', 'department_phone', 'department_extension')


class RotationRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status')

    class Meta:
        model = RotationRequest
        fields = ('id', 'plan_request', 'month', 'specialty',
                  'requested_department', 'delete', 'status')


class RotationRequestResponseSerializer(serializers.ModelSerializer):

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
