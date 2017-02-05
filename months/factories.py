import factory
from month import Month

from accounts.factories import InternFactory, UserFactory
from months.models import Internship, Freeze, FreezeRequest, FreezeRequestResponse, FreezeCancelRequest, \
    FreezeCancelRequestResponse


class InternshipFactory(factory.django.DjangoModelFactory):
    intern = factory.SubFactory(InternFactory, internship=None)
    start_month = Month(2017, 7)

    class Meta:
        model = Internship


class FreezeFactory(factory.django.DjangoModelFactory):
    intern = factory.SubFactory(UserFactory)
    # month
    freeze_request = factory.SubFactory("months.factories.FreezeRequestFactory")

    class Meta:
        model = Freeze


class FreezeRequestFactory(factory.django.DjangoModelFactory):
    intern = factory.SubFactory(UserFactory)
    # month
    justification = factory.Faker('text')
    # submission_datetime

    class Meta:
        model = FreezeRequest


class FreezeRequestResponseFactory(factory.django.DjangoModelFactory):
    request = factory.SubFactory(FreezeRequestFactory)
    is_approved = True
    comments = ""
    # response_datetime

    class Meta:
        model = FreezeRequestResponse


class FreezeCancelRequestFactory(factory.django.DjangoModelFactory):
    intern = factory.SubFactory(UserFactory)
    # month
    # submission_datetime

    class Meta:
        model = FreezeCancelRequest


class FreezeCancelRequestResponseFactory(factory.django.DjangoModelFactory):
    request = factory.SubFactory(FreezeCancelRequestFactory)
    is_approved = True
    comments = ""
    # response_datetime

    class Meta:
        model = FreezeCancelRequestResponse
