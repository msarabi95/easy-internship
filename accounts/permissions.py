from rest_framework.permissions import BasePermission

from accounts.rules import is_staff, is_intern


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return is_staff(request.user)


class IsIntern(BasePermission):
    def has_permission(self, request, view):
        return is_intern(request.user)