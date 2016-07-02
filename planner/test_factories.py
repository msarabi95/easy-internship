import factory
from accounts.models import Profile, Intern
from django.contrib.auth.models import User
from month import Month
from planner.models import Rotation, Internship, Hospital, Department, Specialty, PlanRequest, RotationRequest, \
    RequestedDepartment


class InternFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Intern

    # TODO: generate more sensible data
    student_number = factory.Sequence(lambda n: str(n))
    badge_number = factory.Sequence(lambda n: str(n))
    phone_number = factory.Sequence(lambda n: str(n))
    mobile_number = factory.Sequence(lambda n: str(n))
    address = factory.Faker('address')

    saudi_id_number = factory.Sequence(lambda n: str(n))
    passport_number = factory.Sequence(lambda n: str(n))
    medical_record_number = factory.Sequence(lambda n: str(n))

    contact_person_name = factory.Faker('name')
    contact_person_relation = "Father"
    contact_person_mobile = factory.Sequence(lambda n: str(n))
    contact_person_email = factory.LazyAttribute(lambda obj: "%s@example.com" % obj.contact_person_name.lower())

    gpa = 5.0

    profile = factory.SubFactory('planner.test_factories.ProfileFactory', intern=None)


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    # TODO: specify factory fields

    # We pass in profile=None to prevent UserFactory from creating another profile
    # (this disables the RelatedFactory)
    user = factory.SubFactory('planner.test_factories.UserFactory', profile=None)

    # We pass in 'profile' to link the generated Profile to our just-generated Profile
    # This will call InternFactory(profile=our_new_profile), thus skipping the SubFactory.
    intern = factory.RelatedFactory(InternFactory, 'profile')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "testuser%d" % n)

    # We pass in 'user' to link the generated Profile to our just-generated User
    # This will call ProfileFactory(user=our_new_user), thus skipping the SubFactory.
    profile = factory.RelatedFactory(ProfileFactory, 'user')


class InternshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Internship

    intern = factory.SubFactory("planner.test_factories.InternFactory")
    # Note: If a RelatedFactory is specified on `Intern`, then internship=None should be passed as an argument above

    start_month = Month(2016, 7)


class SpecialtyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Specialty

    name = "Internal Medicine"  # TODO: replace by a custom faker
    abbreviation = "MED"
    required_months = 2


class HospitalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hospital

    name = "King Abdulaziz Medical City"
    abbreviation = "KAMC"
    is_kamc = True


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    hospital = factory.SubFactory("planner.test_factories.HospitalFactory")
    specialty = factory.SubFactory("planner.test_factories.SpecialtyFactory")

    name = "Department of Internal Medicine"  # TODO: replace by a custom faker

    # TODO: complete fields


class RotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rotation

    internship = factory.SubFactory("planner.test_factories.InternshipFactory")
    month = factory.Sequence(lambda n: Month(2016, 6) + n)
    department = factory.SubFactory("planner.test_factories.DepartmentFactory")
    specialty = factory.LazyAttribute(
        lambda obj: obj.department.specialty
    )


class PlanRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlanRequest

    internship = factory.SubFactory("planner.test_factories.InternshipFactory")


class RotationRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RotationRequest

    plan_request = factory.SubFactory("planner.test_factories.PlanRequestFactory")
    month = factory.Sequence(lambda n: Month(2016, 6) + n)
    requested_department = factory.SubFactory("planner.test_factories.RequestedDepartmentFactory",
                                              rotation_request=None)
    specialty = factory.LazyAttribute(lambda obj: obj.requested_department.get_department().specialty)


class RequestedDepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RequestedDepartment

    rotation_request = factory.RelatedFactory(RotationRequestFactory, 'requested_department')
    is_in_database = True
    department = factory.SubFactory("planner.test_factories.DepartmentFactory")
