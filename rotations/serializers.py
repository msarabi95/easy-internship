from rest_framework import serializers

from easy_internship.serializers import MonthField
from hospitals.models import Department
from hospitals.serializers import DepartmentSerializer
from months.serializers import InternshipMonthSerializer
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


class ShortDepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id', 'name')


class ShortRotationRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = RotationRequestResponse
        fields = ('comments', )


class ShortRotationRequestSerializer(serializers.ModelSerializer):
    internship_id = serializers.IntegerField(source='internship.id')
    intern_name = serializers.CharField(source='internship.intern.profile.get_en_full_name')
    gpa = serializers.FloatField(source='internship.intern.gpa')
    response = ShortRotationRequestResponseSerializer()

    class Meta:
        model = RotationRequest
        fields = ('id', 'internship_id', 'intern_name', 'submission_datetime', 'gpa', 'response')


class AcceptanceListSerializer(serializers.Serializer):
    department = ShortDepartmentSerializer()
    month = MonthField()
    # requests = ShortRotationRequestSerializer(many=True)
    acceptance_criterion = serializers.CharField(source='acceptance_setting.criterion')
    acceptance_start_or_end_date = serializers.CharField(source='acceptance_setting.start_or_end_date')
    total_seats = serializers.IntegerField(source='acceptance_setting.total_seats')
    unoccupied_seats = serializers.IntegerField(source='acceptance_setting.get_unoccupied_seats')
    auto_accepted = ShortRotationRequestSerializer(many=True)
    auto_declined = ShortRotationRequestSerializer(many=True)
    manual_accepted = ShortRotationRequestSerializer(many=True)
    manual_declined = ShortRotationRequestSerializer(many=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass