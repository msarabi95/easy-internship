from django.contrib import admin
from .models import RequestedDepartment

class RequestedDepartmentAdmin(admin.ModelAdmin):
    pass

admin.site.register(RequestedDepartment)
