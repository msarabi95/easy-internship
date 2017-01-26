# coding=utf-8
import factory
from django.contrib.auth.models import User

from accounts.models import Profile, Intern


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "testuser%d" % n)
    email = factory.Sequence(lambda n: u"testuser%d@ksau-hs.edu.sa" % n)
    profile = factory.RelatedFactory('accounts.factories.ProfileFactory', 'user')
    is_active = True
    password = factory.PostGenerationMethodCall('set_password', '123')

    class Meta:
        model = User


class ProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory('accounts.factories.UserFactory')

    role = Profile.INTERN
    ar_first_name = factory.Sequence(lambda n: u"تجربة%d" % n)
    ar_middle_name = factory.Sequence(lambda n: u"ابن%d" % n)
    ar_last_name = factory.Sequence(lambda n: u"التجارب%d" % n)
    en_first_name = factory.Sequence(lambda n: u"Test%d" % n)
    en_middle_name = factory.Sequence(lambda n: u"Bin%d" % n)
    en_last_name = factory.Sequence(lambda n: u"Tests%d" % n)

    intern = factory.RelatedFactory('accounts.factories.InternFactory', 'profile')

    class Meta:
        model = Profile


class InternFactory(factory.django.DjangoModelFactory):
    profile = factory.SubFactory('accounts.factories.ProfileFactory')

    student_number = factory.Sequence(lambda n: str(n))
    badge_number = factory.Sequence(lambda n: str(n))
    phone_number = factory.Sequence(lambda n: str(n))
    alt_email = factory.Sequence(lambda n: "user%d@example.com" % n)
    mobile_number = factory.Sequence(lambda n: str(n))
    address = factory.Faker('address')

    saudi_id_number = factory.Sequence(lambda n: str(n))
    # saudi_id = models.ImageField(upload_to='saudi_ids')  # FIXME

    has_passport = True
    passport_number = factory.Sequence(lambda n: str(n))
    # passport = factory.django.ImageField()  # FIXME
    # passport_attachment = models.FileField(upload_to='passport_attachments', blank=True, null=True)  # FIXME
    medical_record_number = factory.Sequence(lambda n: str(n))

    contact_person_name = factory.Faker('name')
    contact_person_relation = "Father"
    contact_person_mobile = factory.Sequence(lambda n: str(n))
    contact_person_email = factory.LazyAttribute(lambda obj: "%s@example.com" % obj.contact_person_name.replace(" ", "").lower())

    gpa = 5.0

    internship = factory.RelatedFactory('months.factories.InternshipFactory', 'intern')

    class Meta:
        model = Intern
