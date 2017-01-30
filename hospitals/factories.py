import factory

from hospitals.models import Hospital, Specialty, DepartmentMonthSettings, CustomDepartmentDetail, Location


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


class LocationFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Location %d" % n)
    abbreviation = factory.Sequence(lambda n: "L%d" % n)

    class Meta:
        model = Location


class CustomDepartmentDetailFactory(factory.django.DjangoModelFactory):
    hospital = factory.SubFactory(HospitalFactory)
    specialty = factory.SubFactory(SpecialtyFactory)
    location = factory.SubFactory(LocationFactory)

    contact_name = factory.Faker('name')
    contact_position = "Chairman"
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    extension = "12345"

    requires_memo = True
    memo_handed_by_intern = True

    class Meta:
        model = CustomDepartmentDetail


class DepartmentMonthSettingsFactory(factory.django.DjangoModelFactory):
    total_seats = 50

    hospital = factory.SubFactory(HospitalFactory)
    specialty = factory.SubFactory(SpecialtyFactory)
    location = factory.SubFactory(LocationFactory)

    class Meta:
        model = DepartmentMonthSettings
