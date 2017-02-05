import factory

from hospitals.factories import HospitalFactory, SpecialtyFactory
from months.factories import InternshipFactory
from rotations.models import Rotation, RotationRequest, RotationRequestResponse


class RotationFactory(factory.DjangoModelFactory):
    internship = factory.SubFactory(InternshipFactory)
    # month
    hospital = factory.SubFactory(HospitalFactory)
    specialty = factory.SubFactory(SpecialtyFactory)
    location = None
    # is_elective
    rotation_request = factory.SubFactory('rotations.factories.RotationRequestFactory')

    class Meta:
        model = Rotation


class RotationRequestFactory(factory.DjangoModelFactory):
    internship = factory.SubFactory(InternshipFactory)
    # month
    hospital = factory.SubFactory(HospitalFactory)
    specialty = factory.SubFactory(SpecialtyFactory)
    location = None
    # is_delete
    # is_elective
    # submission_datetime

    class Meta:
        model = RotationRequest


class RotationRequestResponseFactory(factory.django.DjangoModelFactory):
    rotation_request = factory.SubFactory(RotationRequestFactory)
    is_approved = True
    comments = ""
    # response_datetime

    class Meta:
        model = RotationRequestResponse
