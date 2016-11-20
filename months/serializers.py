from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from planner.models import Internship


class InternshipMonthSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    label = serializers.CharField()
    label_short = serializers.CharField()

    current_rotation = serializers.PrimaryKeyRelatedField(read_only=True)
    current_request = serializers.PrimaryKeyRelatedField(read_only=True)
    request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    current_leaves = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    current_leave_requests = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    current_leave_cancel_requests = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    leave_request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    leave_cancel_request_history = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

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