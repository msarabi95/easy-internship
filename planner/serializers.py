from django.core.exceptions import ObjectDoesNotExist
from planner.models import PlanRequest, Internship, RotationRequest, RotationRequestForward
from rest_framework import serializers


class PlanRequestSerializer(serializers.ModelSerializer):
    intern = serializers.CharField(source='internship.intern.profile.user.username')
    submission_datetime = serializers.DateTimeField(format="%-d %B %Y")
    closure_datetime = serializers.DateTimeField(format="%-d %B %Y")

    class Meta:
        model = PlanRequest
        fields = ('id', 'intern', 'rotation_requests', 'creation_datetime', 'is_submitted',
                  'submission_datetime', 'is_closed', 'closure_datetime',)


class RequestedDepartmentSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super(RequestedDepartmentSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    hospital = serializers.CharField(source='get_department.hospital.name')
    name = serializers.CharField(source='get_department.name')
    specialty = serializers.CharField(source='get_department.specialty')
    contact_name = serializers.CharField(source='get_department.contact_name')
    email = serializers.EmailField(source='get_department.email')
    phone = serializers.CharField(source='get_department.phone')
    extension = serializers.CharField(source='get_department.extension')


class RotationRequestSerializer(serializers.HyperlinkedModelSerializer):
    requested_department = RequestedDepartmentSerializer()
    month = serializers.DateTimeField(format="%B %Y", source="month.first_day")
    status = serializers.CharField(source='get_status')

    class Meta:
        model = RotationRequest
        fields = ('url', 'id', 'plan_request', 'month', 'requested_department', 'delete', 'status',)


class RotationRequestForwardSerializer(serializers.ModelSerializer):
    intern = serializers.CharField(source="rotation_request.plan_request.internship.intern.profile.get_en_full_name")
    rotation_request = RotationRequestSerializer()

    def has_response(self, instance):
        try:
            instance.response
            return True
        except ObjectDoesNotExist:
            return False

    class Meta:
        model = RotationRequestForward
        fields = ('intern', 'key', 'rotation_request', 'forward_datetime', 'response')
