from django.contrib import admin
from planner.models import Hospital, Department, Specialty, Rotation, Internship


class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_kamc']


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'hospital']


class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'required_months']


class RotationInline(admin.TabularInline):
    model = Rotation
    extra = 0


class InternshipAdmin(admin.ModelAdmin):
    inlines = [RotationInline]


admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(Internship, InternshipAdmin)
