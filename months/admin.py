from django.contrib import admin
from planner.models import Rotation, Internship


class RotationInline(admin.TabularInline):
    model = Rotation
    extra = 0


class InternshipAdmin(admin.ModelAdmin):
    inlines = [RotationInline]

admin.site.register(Internship, InternshipAdmin)