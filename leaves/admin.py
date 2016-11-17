from django.contrib import admin
from leaves.models import LeaveType, LeaveRequest


class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'max_days')

admin.site.register(LeaveType, LeaveTypeAdmin)
admin.site.register(LeaveRequest)