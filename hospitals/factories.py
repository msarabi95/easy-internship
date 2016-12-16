import factory, random

from hospitals.models import Hospital, Specialty, Department, DepartmentMonthSettings


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


class DepartmentFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Department %d" % n)

    hospital = factory.SubFactory(HospitalFactory)
    specialty = factory.SubFactory(SpecialtyFactory)

    contact_name = factory.Faker('name')
    contact_position = "Chairman"
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    extension = '12345'

    class Meta:
        model = Department


class DepartmentMonthSettingsFactory(factory.django.DjangoModelFactory):
    total_seats = 50

    department = factory.SubFactory(DepartmentFactory)

    class Meta:
        model = DepartmentMonthSettings

