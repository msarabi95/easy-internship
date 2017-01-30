from django.contrib import admin

from rotations.models import RotationRequest, RotationRequestForward


class RotationRequestAdmin(admin.ModelAdmin):
    list_filter = ['hospital']


admin.site.register(RotationRequest, RotationRequestAdmin)
admin.site.register(RotationRequestForward)