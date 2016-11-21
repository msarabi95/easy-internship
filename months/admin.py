from django.contrib import admin
from rotations.models import Rotation
from months.models import Internship


class RotationInline(admin.TabularInline):
    model = Rotation
    extra = 0


class InternshipAdmin(admin.ModelAdmin):
    inlines = [RotationInline]

admin.site.register(Internship, InternshipAdmin)