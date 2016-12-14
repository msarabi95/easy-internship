import factory

from hospitals.models import Hospital, Specialty


class HospitalFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Hospital %d" % n)
    abbreviation = factory.Sequence(lambda n: "HSP%d" % n)

    class Meta:
        model = Hospital


class SpecialtyFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Specialty %d" % n)
    abbreviation = factory.Sequence(lambda n: "SP%d" % n)
    required_months = 2

    class Meta:
        model = Specialty
