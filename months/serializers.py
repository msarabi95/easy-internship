from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from months.models import Internship, Freeze, FreezeRequest, FreezeRequestResponse, FreezeCancelRequest, \
    FreezeCancelRequestResponse


class InternshipMonthSerializer(serializers.Serializer):
    intern = serializers.PrimaryKeyRelatedField(read_only=True)
    month = serializers.IntegerField(read_only=True)

    label = serializers.CharField(read_only=True)
    label_short = serializers.CharField(read_only=True)

    current_rotation = serializers.PrimaryKeyRelatedField(read_only=True)
    current_request = serializers.PrimaryKeyRelatedField(read_only=True)
    request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

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

    occupied = serializers.BooleanField(read_only=True)
    requested = serializers.BooleanField(read_only=True)
    disabled = serializers.BooleanField(read_only=True)
    frozen = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class InternshipSerializer(serializers.ModelSerializer):
    #months = serializers.SerializerMethodField()
    #unreviewed_rotation_requests = serializers.SerializerMethodField()
    #forwarded_unreviewed_rotation_requests = serializers.SerializerMethodField()
    #closed_rotation_requests = serializers.SerializerMethodField()
    #unreviewed_request_count = serializers.SerializerMethodField()
    #latest_request_datetime = serializers.SerializerMethodField()
    #latest_response_datetime = serializers.SerializerMethodField()

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

    def validate(self, data):
        """
        Checks that:
        1- The internship plan doesn't exceed 12 months.
        2- Each specialty doesn't exceed its required months in non-elective rotations.
        3- Not more than 2 months are used for electives. (Electives can be any specialty)
        """
        errors = []
        if self.instance.rotations.count() > 12:
            errors.append(ValidationError("The internship plan should contain no more than 12 months."))

        from hospitals.models import Specialty

        # Get a list of general specialties.
        general_specialties = Specialty.objects.general()
        non_electives = filter(lambda rotation: not rotation.is_elective, self.instance.rotations.all())
        electives = filter(lambda rotation: rotation.is_elective, self.instance.rotations.all())

        # Check that the internship plan contains at most 2 non-elective months of each general specialty.
        for specialty in general_specialties:
            rotation_count = len(filter(lambda rotation: rotation.specialty.get_general_specialty() == specialty,
                                        non_electives))

            if rotation_count > specialty.required_months:
                errors.append(ValidationError("The internship plan should contain at most %d month(s) of %s.",
                                              params=(specialty.required_months, specialty.name)))

        # Check that the internship plan contains at most 2 months of electives.
        if len(electives) > 2:
            errors.append(ValidationError("The internship plan should contain at most %d month of %s.",
                                          params=(2, "electives")))

        if errors:
            raise ValidationError(errors)

    class Meta:
        model = Internship
        fields = ('id', 'intern', 'start_month', 'rotation_requests', )
# 'unreviewed_rotation_requests',
#                  'forwarded_unreviewed_rotation_requests', 'closed_rotation_requests',
#                  'unreviewed_request_count', 'latest_request_datetime', 'latest_response_datetime')


class FreezeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Freeze
        fields = '__all__'


class FreezeRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FreezeRequest
        fields = '__all__'


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
