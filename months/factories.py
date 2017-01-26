import factory
from month import Month

from months.models import Internship


class InternshipFactory(factory.django.DjangoModelFactory):
    intern = factory.SubFactory('accounts.factories.InternFactory')
    start_month = Month(2017, 7)

    class Meta:
        model = Internship

