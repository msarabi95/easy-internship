from django.contrib import admin
from hospitals.models import Hospital, Specialty, MonthSettings, DepartmentSettings, DepartmentMonthSettings, AcceptanceSetting


class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_kamc']


class DepartmentMonthSettingsAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'month', 'hospital', 'specialty', 'location',
                    'total_seats', 'available_seats',
                    'acceptance_criterion', 'acceptance_start_date', 'acceptance_end_date']
    search_fields = ['hospital__name', 'specialty__name', 'location__name']
    list_filter = ['specialty', 'hospital', 'month']

    def available_seats(self, obj):
        settings = AcceptanceSetting(obj.department, obj.month)  # FIXME
        return settings.get_available_seats()


class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'required_months']


admin.site.register(Hospital, HospitalAdmin)
admin.site.register(MonthSettings)
admin.site.register(DepartmentSettings)
admin.site.register(DepartmentMonthSettings, DepartmentMonthSettingsAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
