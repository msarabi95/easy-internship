import factory

from rotations.models import Rotation, RequestedDepartment, RotationRequest, RotationRequestResponse, \
    RotationRequestForward


class RotationFactory(factory.DjangoModelFactory):
    internship = factory.SubFactory("months.factories.InternshipFactory")
    # month
    specialty = factory.SubFactory("hospitals.factories.SpecialtyFactory")
    department = factory.SubFactory("hospitals.factories.DepartmentFactory")
    # is_elective
    rotation_request = factory.SubFactory("rotations.factories.RotationRequestFactory")

    class Meta:
        model = Rotation


class RequestedDepartmentFactory(factory.DjangoModelFactory):
    is_in_database = True
    department = factory.SubFactory("hospitals.factories.DepartmentFactory")

    class Meta:
        model = RequestedDepartment


class RotationRequestFactory(factory.DjangoModelFactory):
    internship = factory.SubFactory("months.factories.InternshipFactory")
    # month
    specialty = factory.SubFactory("hospitals.factories.SpecialtyFactory")
    requested_department = factory.SubFactory("rotations.factories.RequestedDepartmentFactory")
    # is_delete
    # is_elective

    class Meta:
        model = RotationRequest


class RotationRequestResponseFactory(factory.DjangoModelFactory):
    rotation_request = factory.SubFactory("rotations.factories.RotationRequestFactory")
    is_approved = True
    comments = ""

    class Meta:
        model = RotationRequestResponse


class RotationRequestForwardFactory(factory.DjangoModelFactory):
    rotation_request = factory.SubFactory("rotations.factories.RotationRequestFactory")
    memo_file = factory.django.FileField(filename="memo.pdf")

    class Meta:
        model = RotationRequestForward
