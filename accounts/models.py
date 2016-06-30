from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile")

    STAFF = "staff"
    INTERN = "intern"

    ROLE_CHOICES = (
        (STAFF, "Staff member"),
        (INTERN, "Intern"),
    )

    role = models.CharField(max_length=8, choices=ROLE_CHOICES)
    ar_first_name = models.CharField(max_length=32)
    ar_middle_name = models.CharField(max_length=32)
    ar_last_name = models.CharField(max_length=32)
    en_first_name = models.CharField(max_length=32)
    en_middle_name = models.CharField(max_length=32)
    en_last_name = models.CharField(max_length=32)

    def get_ar_full_name(self):
        return " ".join([self.ar_first_name, self.ar_middle_name, self.ar_last_name])

    def get_en_full_name(self):
        return " ".join([self.en_first_name, self.en_middle_name, self.en_last_name])

    def clean(self):
        # TODO: Force having an intern profile when role=intern (Perhaps overriding the save method would be better)
        pass

    def __unicode__(self):
        return "Profile of user: %s" % self.user.username


class Intern(models.Model):
    profile = models.OneToOneField(Profile, related_name="intern")
    student_number = models.CharField(max_length=9)
    badge_number = models.CharField(max_length=9)
    phone_number = models.CharField(max_length=16)
    mobile_number = models.CharField(max_length=16)
    address = models.CharField(max_length=128)

    saudi_id_number = models.CharField(max_length=10)
    passport_number = models.CharField(max_length=10)
    medical_record_number = models.CharField(max_length=10)

    contact_person_name = models.CharField(max_length=64)
    contact_person_relation = models.CharField(max_length=32)
    contact_person_mobile = models.CharField(max_length=16)
    contact_person_email = models.EmailField(max_length=64)

    gpa = models.FloatField(validators=[MaxValueValidator(5.0), MinValueValidator(0.0)])

    def __unicode__(self):
        return "Intern profile of user: %s" % self.profile.user.username
