from django.core import exceptions as django_exceptions

from rest_framework import serializers

from easy_internship.serializers import MonthField
from hospitals.models import Department, AcceptanceSetting
from hospitals.serializers import SpecialtySerializer, DepartmentSerializer2
from months.models import Internship
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
                  'status', 'response', 'forward', 'is_forwarded')


class UpdatedRotationRequestSerializer(serializers.Serializer):
    """
    This is used by the rotation request creation form.
    """
    internship = serializers.PrimaryKeyRelatedField(queryset=Internship.objects.all())
    month = MonthField()
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='requested_department.department'
    )
    is_elective = serializers.BooleanField(required=False)
    request_memo = serializers.FileField(required=False)

    def validate(self, data):
        """
        Check that a memo is supplied if the user is an outside intern
        """
        # Do some checks
        # (1) Check there isn't another open request already
        # (2) Check that submission is open
        # (3) Check that submitted request satisfies internship requirements

        internship = data['internship']
        department = data['requested_department']['department']
        month = data['month']
        acceptance_setting = AcceptanceSetting(department, month)

        errors = []

        if internship.rotation_requests.current_for_month(month):
            errors.append("There is a rotation request for this month already.")

        if not acceptance_setting.can_submit_requests():
            errors.append(
                "Submission is closed for %s during %s." % (department.name, month.first_day().strftime("%B %Y"))
            )

        requested_department = RequestedDepartment(is_in_database=True, department=department)
        rotation_request = RotationRequest(
            internship=internship,
            month=month,
            requested_department=requested_department,
            specialty=department.specialty,
            is_elective=data.get('is_elective', False),
            request_memo=data.get('request_memo'),
        )
        try:
            rotation_request.validate_request()
        except django_exceptions.ValidationError as e:
            for error in e.message_dict[django_exceptions.NON_FIELD_ERRORS]:
                errors.append(error)

        if internship.intern.is_outside_intern and data.get('request_memo') is None:
            # This error is raised immediately, rather than added to the `errors` list and raised with other errors
            # because otherwise it will be added to the "non_field_errors" list, which not correct
            raise serializers.ValidationError({'request_memo': ['This field is required.']})

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        requested_department = RequestedDepartment.objects.create(
            is_in_database=True,
            department=validated_data['requested_department']['department'],
        )

        rotation_request = RotationRequest.objects.create(
            internship=validated_data['internship'],
            month=validated_data['month'],
            requested_department=requested_department,
            specialty=requested_department.department.specialty,
            is_elective=validated_data.get('is_elective', False),
            request_memo=validated_data.get('request_memo'),
        )

        return rotation_request

    def update(self, instance, validated_data):
        pass


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
    id = serializers.IntegerField()
    internship_id = serializers.IntegerField(source='internship.id')
    intern_name = serializers.CharField(source='internship.intern.profile.get_en_full_name')
    intern_university = serializers.CharField(source='internship.intern.university.abbreviation')
    month = MonthField()
    specialty = serializers.CharField(source='specialty.name')
    requested_department_name = serializers.CharField(source='requested_department.get_department.name')
    requested_department_hospital_name = serializers.CharField(source='requested_department.get_department.hospital.name')
    requested_department_requires_memo = serializers.BooleanField(source='requested_department.get_department.requires_memo')
    gpa = serializers.FloatField(source='internship.intern.gpa')
    is_elective = serializers.BooleanField()
    is_delete = serializers.BooleanField()
    request_memo = serializers.FileField(read_only=True)
    response = ShortRotationRequestResponseSerializer(allow_null=True)

    class Meta:
        model = RotationRequest
        fields = ('id', 'internship_id', 'intern_name', 'intern_university', 'month', 'specialty', 'requested_department_name',
                  'requested_department_hospital_name', 'requested_department_requires_memo', 'request_memo',
                  'is_elective', 'submission_datetime', 'gpa', 'is_elective', 'is_delete', 'response')


class AcceptanceListSerializer(serializers.Serializer):
    department = ShortDepartmentSerializer()
    month = MonthField()
    type = serializers.CharField()
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
    possible_conflict = serializers.BooleanField(read_only=True)

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


class FullRotationSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(FullRotationSerializer, self).__init__(*args, **kwargs)
        from months.serializers import InternshipSerializer
        self.fields['internship'] = InternshipSerializer(details=False)

    request_datetime = serializers.DateTimeField(source='rotation_request.submission_datetime')
    approval_datetime = serializers.DateTimeField(source='rotation_request.response.response_datetime')

    class Meta:
        model = Rotation
        fields = '__all__'


#############################
# Plans summary serializers #
#############################


class RequestedDepartmentSerializer2(serializers.ModelSerializer):
    department = DepartmentSerializer2()

    class Meta:
        model = RequestedDepartment
        fields = '__all__'


class RotationRequestSerializer2(serializers.ModelSerializer):
    month = MonthField()
    specialty = SpecialtySerializer()
    requested_department = RequestedDepartmentSerializer2()
    is_forwarded = serializers.BooleanField(read_only=True)
    response = RotationRequestResponseSerializer()
    forward = RotationRequestForwardSerializer()

    class Meta:
        model = RotationRequest
        fields = '__all__'


class RotationSerializer2(serializers.ModelSerializer):
    specialty = SpecialtySerializer()
    department = DepartmentSerializer2()
    rotation_request = RotationRequestSerializer2()

    class Meta:
        model = Rotation
        fields = '__all__'
