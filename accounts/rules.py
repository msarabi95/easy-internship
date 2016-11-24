from __future__ import absolute_import

import rules
from accounts.models import Profile
from django.core.exceptions import ObjectDoesNotExist


@rules.predicate
def is_intern(user):
    try:
        profile = user.profile
        return profile.role == Profile.INTERN
    except (ObjectDoesNotExist, AttributeError):
        return False


@rules.predicate
def is_staff(user):
    try:
        profile = user.profile
        return profile.role == Profile.STAFF
    except (ObjectDoesNotExist, AttributeError):
        return False


rules.add_perm("planner.view_intern_site", is_intern)

rules.add_perm("planner.view_staff_site", is_staff)

rules.add_perm("accounts.user.view_all", is_staff)
rules.add_perm("accounts.profile.view_all", is_staff)
rules.add_perm("accounts.intern.view_all", is_staff)

rules.add_perm("rotations.rotation.view_all", is_staff)
rules.add_perm("rotations.requested_department.view_all", is_staff)
rules.add_perm("rotations.rotation_request.view_all", is_staff)
rules.add_perm("rotations.rotation_request_response.view_all", is_staff)
rules.add_perm("rotations.rotation_request_forward.view_all", is_staff)
rules.add_perm("rotations.rotation_request_forward_response.view_all", is_staff)

rules.add_perm("months.internship.view_all", is_staff)

rules.add_perm("leaves.leave_setting.view_all", is_staff)
rules.add_perm("leaves.leave_request.view_all", is_staff)
rules.add_perm("leaves.leave_request_response.view_all", is_staff)
rules.add_perm("leaves.leave.view_all", is_staff)
rules.add_perm("leaves.leave_cancel_request.view_all", is_staff)
rules.add_perm("leaves.leave_cancel_request_response.view_all", is_staff)
