from rest_framework import serializers

from hospitals.models import Hospital, Specialty, Department, GlobalSettings, MonthSettings, DepartmentSettings, \
    DepartmentMonthSettings
from easy_internship.serializers import MonthField


class HospitalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hospital
        fields = '__all__'


class SpecialtySerializer(serializers.ModelSerializer):

    class Meta:
        model = Specialty
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class GlobalSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = GlobalSettings
        fields = ('acceptance_criterion', 'acceptance_start_date_interval', 'acceptance_end_date_interval')


class MonthSettingsSerializer(serializers.ModelSerializer):
    month = MonthField()
    acceptance_start_date = serializers.DateTimeField(required=False, allow_null=True)
    acceptance_end_date = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = MonthSettings
        fields = ('id', 'month', 'acceptance_criterion', 'acceptance_start_date', 'acceptance_end_date')


class DepartmentSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentSettings
        fields = ('id', 'department', 'acceptance_criterion',
                  'acceptance_start_date_interval', 'acceptance_end_date_interval')


class DepartmentMonthSettingsSerializer(serializers.ModelSerializer):
    month = MonthField()
    acceptance_start_date = serializers.DateTimeField(required=False, allow_null=True)
    acceptance_end_date = serializers.DateTimeField(required=False, allow_null=True)

    booked_seats = serializers.SerializerMethodField()
    occupied_seats = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    def get_booked_seats(self, obj):
        return 0  # TODO

    def get_occupied_seats(self, obj):
        return 0  # TODO

    def get_available_seats(self, obj):
        return 0  # TODO

    class Meta:
        model = DepartmentMonthSettings
        fields = ('id', 'month', 'department',
                  'total_seats', 'booked_seats', 'occupied_seats', 'available_seats',
                  'acceptance_criterion', 'acceptance_start_date', 'acceptance_end_date')


class AcceptanceSettingSerializer(serializers.Serializer):
    type = serializers.CharField()
    criterion = serializers.CharField()
    start_or_end_date = serializers.DateTimeField()
    total_seats = serializers.IntegerField(allow_null=True)
    booked_seats = serializers.IntegerField(allow_null=True, source='get_booked_seats')
    occupied_seats = serializers.IntegerField(allow_null=True, source='get_occupied_seats')
    unoccupied_seats = serializers.IntegerField(allow_null=True, source='get_unoccupied_seats')
    available_seats = serializers.IntegerField(allow_null=True, source='get_available_seats')
    can_submit_requests = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass