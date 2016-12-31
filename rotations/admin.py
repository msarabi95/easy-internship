from django.contrib import admin

from rotations.models import RotationRequest, RotationRequestForward
from .models import RequestedDepartment


class RotationRequestAdmin(admin.ModelAdmin):
    list_filter = ['requested_department__department__hospital']


admin.site.register(RequestedDepartment)
admin.site.register(RotationRequest, RotationRequestAdmin)
admin.site.register(RotationRequestForward)