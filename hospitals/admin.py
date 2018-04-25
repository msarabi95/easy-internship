from django.contrib import admin
from hospitals.models import Hospital, Specialty, Department, MonthSettings, \
    AcceptanceSetting, SeatAvailability


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(HospitalAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_kamc=False)

    list_display = ['name', 'abbreviation', 'is_kamc']


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'required_months']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(DepartmentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(hospital__is_kamc=True)

    def get_queryset(self, request):
        qs = super(DepartmentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(hospital__is_kamc=True)

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ['hospital', 'specialty']
        return ['specialty']

    list_display = ['name', 'specialty', 'hospital']
    list_filter = ['hospital', 'specialty']


@admin.register(SeatAvailability)
class SeatAvailabilityAdmin(admin.ModelAdmin):
    list_display = [
        'specialty_name', 'hospital_abbrev', 'month',
        'total_seats', 'available_seats',
    ]
    list_editable = ['total_seats']
    search_fields = ['department__name', 'department__specialty__name', 'department__hospital__name']
    list_filter = ['department__specialty', 'department__hospital', 'month']

    def get_queryset(self, request):
        """
        Preload department, hospital, and specialty information for better performance.
        """
        return super(SeatAvailabilityAdmin, self).get_queryset(request).prefetch_related(
            'department__specialty',
            'department__hospital',
        )

    def specialty_name(self, obj):
        return obj.department.specialty.name
    specialty_name.short_description = "Specialty"

    def hospital_abbrev(self, obj):
        return obj.department.hospital.abbreviation
    hospital_abbrev.short_description = "Hospital"

    def available_seats(self, obj):
        settings = AcceptanceSetting(obj.department, obj.month)
        return settings.get_available_seats()


@admin.register(MonthSettings)
class MonthSettingsAdmin(admin.ModelAdmin):
    list_display = ['month', 'acceptance_criterion', 'acceptance_start_date', 'acceptance_end_date']
