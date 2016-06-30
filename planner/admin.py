from django.contrib import admin
from planner.models import Hospital, Department, Specialty, Rotation, Internship


class RotationInline(admin.TabularInline):
    model = Rotation
    extra = 0


class InternshipAdmin(admin.ModelAdmin):
    inlines = [RotationInline]

admin.site.register(Hospital)
admin.site.register(Specialty)
admin.site.register(Department)
admin.site.register(Internship, InternshipAdmin)
