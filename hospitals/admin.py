from django.contrib import admin
from hospitals.models import Hospital, Specialty, Department, MonthSettings, DepartmentSettings, DepartmentMonthSettings


class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_kamc']


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'hospital']


class DepartmentMonthSettingsAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'month', 'department',
                    'total_seats', 'available_seats',
                    'acceptance_criterion', 'acceptance_start_date', 'acceptance_end_date']

    def available_seats(self, obj):
        return 0  # TODO


class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'required_months']


admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(MonthSettings)
admin.site.register(DepartmentSettings)
admin.site.register(DepartmentMonthSettings, DepartmentMonthSettingsAdmin)
admin.site.register(Specialty, SpecialtyAdmin)