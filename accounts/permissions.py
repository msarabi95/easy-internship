from rest_framework.permissions import BasePermission
from rest_framework import permissions
from accounts.rules import is_staff, is_intern


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return is_staff(request.user)


class IsIntern(BasePermission):
    def has_permission(self, request, view):
        return is_intern(request.user)


class IsStaffOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return is_staff(request.user)