from django.core.exceptions import ObjectDoesNotExist
from planner.models import RotationRequest, RotationRequestForward, Rotation, Hospital, Specialty, \
    Department, Internship, RequestedDepartment, RotationRequestResponse, RotationRequestForwardResponse, \
    SeatAvailability
from rest_framework import serializers


class HospitalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hospital
        fields = ('id', 'name', 'abbreviation', 'is_kamc', 'departments')


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
    label_short = serializers.CharField()
    current_rotation = serializers.PrimaryKeyRelatedField(read_only=True)
    current_request = serializers.PrimaryKeyRelatedField(read_only=True)
    request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class InternshipSerializer(serializers.ModelSerializer):
    months = serializers.SerializerMethodField()
    unreviewed_rotation_requests = serializers.SerializerMethodField()
    forwarded_unreviewed_rotation_requests = serializers.SerializerMethodField()
    closed_rotation_requests = serializers.SerializerMethodField()
    unreviewed_request_count = serializers.SerializerMethodField()
    latest_request_datetime = serializers.SerializerMethodField()
    latest_response_datetime = serializers.SerializerMethodField()

    def get_months(self, obj):
        return map(lambda internship_month: int(internship_month.month), obj.months)

    def get_unreviewed_rotation_requests(self, obj):
        return obj.rotation_requests.unreviewed().values_list("id", flat=True)

    def get_forwarded_unreviewed_rotation_requests(self, obj):
        return obj.rotation_requests.forwarded_unreviewed().values_list("id", flat=True)

    def get_closed_rotation_requests(self, obj):
        return obj.rotation_requests.closed().values_list("id", flat=True)

    def get_unreviewed_request_count(self, obj):
        return obj.rotation_requests.unreviewed().count()

    def get_latest_request_datetime(self, obj):
        try:
            return obj.rotation_requests.latest("submission_datetime")\
                .submission_datetime.strftime("%A, %-d %B %Y, %-I:%M %p")
        except ObjectDoesNotExist:
            return None

    def get_latest_response_datetime(self, obj):
        try:
            return obj.rotation_requests.closed().latest("response__response_datetime")\
                .response.response_datetime.strftime("%A, %-d %B %Y, %-I:%M %p")
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = Internship
        fields = ('id', 'intern', 'start_month', 'months', 'unreviewed_rotation_requests',
                  'forwarded_unreviewed_rotation_requests', 'closed_rotation_requests',
                  'unreviewed_request_count', 'latest_request_datetime', 'latest_response_datetime')


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
