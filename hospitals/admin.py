from django.contrib import admin
from hospitals.models import Hospital, Specialty, Department, MonthSettings, DepartmentSettings, DepartmentMonthSettings, AcceptanceSetting


class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_kamc']


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'hospital']


class DepartmentMonthSettingsAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'month', 'department',
                    'total_seats', 'available_seats',
                    'acceptance_criterion', 'acceptance_start_date', 'acceptance_end_date']
    search_fields = ['department__name', 'department__specialty__name']
    list_filter = ['department__specialty', 'department__hospital', 'month']

    def available_seats(self, obj):
        settings = AcceptanceSetting(obj.department, obj.month)
        return settings.get_available_seats()


class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'required_months']


admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(MonthSettings)
admin.site.register(DepartmentSettings)
admin.site.register(DepartmentMonthSettings, DepartmentMonthSettingsAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
