import factory

from leaves.models import LeaveType, LeaveSetting, LeaveRequest, LeaveRequestResponse, LeaveCancelRequest, \
    LeaveCancelRequestResponse


class LeaveTypeFactory(factory.DjangoModelFactory):
    codename = factory.Sequence(lambda n: "leavetype%d" % n)
    name = factory.Sequence(lambda n: "Leave Type %d" % n)
    max_days = 10

    class Meta:
        model = LeaveType


class LeaveSettingFactory(factory.DjangoModelFactory):
    intern = factory.SubFactory("accounts.factories.UserFactory")
    type = factory.SubFactory("leaves.factories.LeaveTypeFactory")
    max_days = 10

    class Meta:
        model = LeaveSetting


class LeaveRequestFactory(factory.DjangoModelFactory):
    intern = factory.SubFactory("accounts.factories.UserFactory")
    # month
    type = factory.SubFactory("leaves.factories.LeaveTypeFactory")
    rotation_request = factory.SubFactory("rotations.factories.RotationRequestFactory")
    # start_date
    # end_date

    class Meta:
        model = LeaveRequest


class LeaveRequestResponseFactory(factory.DjangoModelFactory):
    request = factory.SubFactory("leaves.factories.LeaveRequestFactory")
    is_approved = True
    comments = ""

    class Meta:
        model = LeaveRequestResponse


class LeaveFactory(factory.DjangoModelFactory):
    intern = factory.SubFactory("accounts.factories.UserFactory")
    # month
    type = factory.SubFactory("leaves.factories.LeaveTypeFactory")
    # start_date
    # end_date
    request = factory.SubFactory("leaves.factories.LeaveRequestFactory")


class LeaveCancelRequestFactory(factory.DjangoModelFactory):
    intern = factory.SubFactory("accounts.factories.UserFactory")
    # month
    leave_request = factory.SubFactory("leaves.factories.LeaveRequestFactory")
    rotation_request = factory.SubFactory("rotations.factories.RotationRequestFactory")

    class Meta:
        model = LeaveCancelRequest


class LeaveCancelRequestResponseFactory(factory.DjangoModelFactory):
    request = factory.SubFactory("leaves.factories.LeaveCancelRequestFactory")
    is_approved = True
    comments = ""

    class Meta:
        model = LeaveCancelRequestResponse
