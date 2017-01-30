from rest_framework import serializers

from easy_internship.serializers import MonthField
from rotations.models import Rotation, RotationRequest, RotationRequestResponse, \
    RotationRequestForward


class RotationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rotation
        fields = '__all__'


class RotationRequestSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status', required=False)

    def get_month(self, obj):
        return int(obj.month)

    class Meta:
        model = RotationRequest
        fields = ('id', 'internship', 'month', 'hospital', 'specialty', 'location',
                  'is_delete', 'is_elective', 'submission_datetime',
                  'status', 'response', 'forward')


class RotationRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = RotationRequestResponse
        fields = '__all__'


class RotationRequestForwardSerializer(serializers.ModelSerializer):

    class Meta:
        model = RotationRequestForward
        fields = '__all__'


# class ShortDepartmentSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Department
#         fields = ('id', 'name')


class ShortRotationRequestResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = RotationRequestResponse
        fields = ('comments', )


class ShortRotationRequestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    internship_id = serializers.IntegerField(source='internship.id')
    intern_name = serializers.CharField(source='internship.intern.profile.get_en_full_name')
    month = MonthField()
    specialty = serializers.CharField(source='specialty.name')
    requested_department_name = serializers.CharField(source='requested_department.get_department.name')
    requested_department_hospital_name = serializers.CharField(source='requested_department.get_department.hospital.name')
    requested_department_requires_memo = serializers.BooleanField(source='requested_department.get_department.requires_memo')
    gpa = serializers.FloatField(source='internship.intern.gpa')
    is_elective = serializers.BooleanField()
    is_delete = serializers.BooleanField()
    response = ShortRotationRequestResponseSerializer(allow_null=True)

    class Meta:
        model = RotationRequest
        fields = ('id', 'internship_id', 'intern_name', 'month', 'specialty', 'requested_department_name',
                  'requested_department_hospital_name', 'requested_department_requires_memo',
                  'is_elective', 'submission_datetime', 'gpa', 'is_elective', 'is_delete', 'response')


class AcceptanceListSerializer(serializers.Serializer):
    # department = ShortDepartmentSerializer()  # FIXME
    month = MonthField()
    acceptance_criterion = serializers.CharField()
    acceptance_is_open = serializers.BooleanField()
    acceptance_start_or_end_date = serializers.DateTimeField()
    total_seats = serializers.IntegerField()
    unoccupied_seats = serializers.IntegerField()
    booked_seats = serializers.IntegerField()
    auto_accepted = ShortRotationRequestSerializer(many=True)
    auto_declined = ShortRotationRequestSerializer(many=True)
    manual_accepted = ShortRotationRequestSerializer(many=True)
    manual_declined = ShortRotationRequestSerializer(many=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        acceptance_list = instance

        for x in ('auto_accepted', 'auto_declined', 'manual_accepted', 'manual_declined',):
            request_list = list()
            for request_data in validated_data.pop(x):

                rr = RotationRequest.objects.get(id=request_data['id'])  # ? performance
                if request_data.get('response'):
                    rr.response = RotationRequestResponse(rotation_request=rr, comments=request_data.get('response').get('comments'))
                request_list.append(rr)
            setattr(acceptance_list, x, request_list)

        return acceptance_list


class ShortRotationRequestForwardSerializer(serializers.ModelSerializer):
    rotation_request = ShortRotationRequestSerializer()
    memo_file = serializers.URLField(source='memo_file.url')

    class Meta:
        model = RotationRequestForward
        fields = ('id', 'forward_datetime', 'memo_file', 'rotation_request', )