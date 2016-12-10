import factory
from month import Month

from months.models import Internship


class InternshipFactory(factory.django.DjangoModelFactory):
    start_month = Month(2017, 7)

    class Meta:
        model = Internship

