# -*- coding: utf-8 -*-
import factory
from accounts.models import Profile, Intern
from django.contrib.auth.models import User
from months.models import Internship
from month import Month

class InternshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Internship
    
    start_month = Month(2017, 7)

class InternFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Intern

    student_number = factory.Sequence(lambda n: str(n))
    badge_number = factory.Sequence(lambda n: str(n))
    phone_number = factory.Sequence(lambda n: str(n))
    alt_email = factory.Sequence(lambda n: u"user%d@gmail.com" % n)
    mobile_number = factory.Sequence(lambda n: str(n))
    address = factory.Faker('address')

    saudi_id_number = factory.Sequence(lambda n: str(n))
    #saudi_id = models.ImageField(upload_to='saudi_ids')

    has_passport = True
    passport_number = factory.Sequence(lambda n: str(n))
    #passport_attachment = models.FileField(upload_to='passport_attachments', blank=True, null=True)
    medical_record_number = factory.Sequence(lambda n: str(n))

    contact_person_name = factory.Faker('name')
    contact_person_relation = "Father"
    contact_person_mobile = factory.Sequence(lambda n: str(n))
    contact_person_email = factory.LazyAttribute(lambda obj: "%s@example.com" % obj.contact_person_name.replace(" ", "").lower())

    gpa = 5.0

    internship = factory.RelatedFactory(InternshipFactory, 'intern')

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    role = Profile.INTERN
    ar_first_name = factory.Sequence(lambda n: u"تجربة%d" % n)
    ar_middle_name = factory.Sequence(lambda n: u"ابن%d" % n)
    ar_last_name = factory.Sequence(lambda n: u"التجارب%d" % n)
    en_first_name = factory.Sequence(lambda n: u"Test%d" % n)
    en_middle_name = factory.Sequence(lambda n: u"Bin%d" % n)
    en_last_name = factory.Sequence(lambda n: u"Tests%d" % n)
    # We pass in 'profile' to link the generated Profile to our just-generated Profile
    # This will call InternFactory(profile=our_new_profile), thus skipping the SubFactory.
    intern = factory.RelatedFactory(InternFactory, 'profile')

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "testuser%d" % n)
    email = factory.Sequence(lambda n: u"testuser%d@ksau-hs.edu.sa" % n)
    profile = factory.RelatedFactory(ProfileFactory, 'user')
    is_active = True
    password =  factory.PostGenerationMethodCall('set_password', '123')
