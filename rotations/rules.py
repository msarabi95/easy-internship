from __future__ import absolute_import

import rules
from rotations.models import Rotation, RotationRequest, RotationRequestResponse, RotationRequestForward, \
    RotationRequestForwardResponse


@rules.predicate
def is_owner(user, object):
    """
    Check if the user owns the passed object, which may be one of: Rotation, RotationRequest,
     RotationRequestResponse, RotationRequestForward, RotationRequestForwardResponse.
    """
    if isinstance(object, Rotation):
        return user == object.internship.intern.profile.user
    elif isinstance(object, RotationRequest):
        return user == object.plan_request.internship.intern.profile.user
    elif isinstance(object, RotationRequestResponse) or isinstance(object, RotationRequestForward):
        return user == object.rotation_request.plan_request.internship.intern.profile.user
    elif isinstance(object, RotationRequestForwardResponse):
        return user == object.forward.rotation_request.plan_request.internship.intern.profile.user
    else:
        return False