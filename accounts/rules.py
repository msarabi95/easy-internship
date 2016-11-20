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
