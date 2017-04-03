from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from month.models import MonthField
from userena.models import UserenaBaseProfile

from accounts.managers import UniversityManager, BatchQuerySet


class Profile(UserenaBaseProfile):
    user = models.OneToOneField(User, related_name="profile")

    STAFF = "staff"
    INTERN = "intern"

    ROLE_CHOICES = (
        (STAFF, "Staff member"),
        (INTERN, "Intern"),
    )

    role = models.CharField(max_length=8, choices=ROLE_CHOICES)
    ar_first_name = models.CharField(max_length=32)
    ar_father_name = models.CharField(max_length=32)
    ar_grandfather_name = models.CharField(max_length=32)
    ar_last_name = models.CharField(max_length=32)
    en_first_name = models.CharField(max_length=32)
    en_father_name = models.CharField(max_length=32)
    en_grandfather_name = models.CharField(max_length=32)
    en_last_name = models.CharField(max_length=32)

    def get_ar_full_name(self):
        return " ".join([self.ar_first_name, self.ar_father_name, self.ar_grandfather_name[0], self.ar_last_name])

    def get_en_full_name(self):
        return " ".join([self.en_first_name, self.en_father_name, self.en_grandfather_name[0], self.en_last_name])

    def clean(self):
        # TODO: Force having an intern profile when role=intern (Perhaps overriding the save method would be better)
        pass

    def __unicode__(self):
        return "Profile of user: %s" % self.user.username


class Intern(models.Model):
    profile = models.OneToOneField(Profile, related_name="intern")

    batch = models.ForeignKey("Batch", related_name='interns')
    university = models.ForeignKey("University", related_name='interns')

    student_number = models.CharField(max_length=9, blank=True, null=True)
    badge_number = models.CharField(max_length=9, blank=True, null=True)
    alt_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True)
    mobile_number = models.CharField(max_length=16)
    address = models.CharField(max_length=128)

    id_number = models.CharField(max_length=10)
    id_image = models.ImageField(upload_to='saudi_ids')

    has_passport = models.NullBooleanField(default=True)
    passport_number = models.CharField(max_length=10, blank=True, null=True)
    passport_image = models.ImageField(upload_to='passports', blank=True, null=True)
    passport_attachment = models.FileField(upload_to='passport_attachments', blank=True, null=True)

    medical_record_number = models.CharField(max_length=10, blank=True, null=True)
    medical_checklist = models.FileField(upload_to='medical_checklists', blank=True, null=True)

    contact_person_name = models.CharField(max_length=64)
    contact_person_relation = models.CharField(max_length=32)
    contact_person_mobile = models.CharField(max_length=16)
    contact_person_email = models.EmailField(max_length=64)

    gpa = models.FloatField(validators=[MaxValueValidator(5.0), MinValueValidator(0.0)])
    academic_transcript = models.FileField(upload_to='academic_transcripts', blank=True, null=True)
    graduation_date = MonthField(blank=True, null=True)

    @property
    def is_ksauhs_intern(self):
        return self.university.is_ksauhs

    @property
    def is_agu_intern(self):
        return self.university.is_agu

    @property
    def is_outside_intern(self):
        return self.university.is_outside

    def __unicode__(self):
        return "Intern profile of user: %s" % self.profile.user.username


class University(models.Model):
    name = models.CharField(max_length=60)
    abbreviation = models.CharField(max_length=10)
    city = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    internship_phone = models.CharField(max_length=16)
    internship_fax = models.CharField(max_length=16)
    internship_email = models.EmailField()
    is_ksauhs = models.BooleanField(default=False)
    is_agu = models.BooleanField(default=False)

    objects = UniversityManager()

    @property
    def is_outside(self):
        return not (self.is_ksauhs or self.is_agu)

    def clean(self):
        """
        A university can't have both `is_ksauhs` and `is_agu` flags True at the same time.
        """
        if self.is_ksauhs and self.is_agu:
            raise ValidationError(
                "A university can't be both KSAU-HS and AGU at the same time."
            )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Universities"


class Batch(models.Model):
    name = models.CharField(max_length=20)
    abbreviation = models.CharField(max_length=10)
    is_ksauhs = models.BooleanField(default=False)
    is_agu = models.BooleanField(default=False)
    start_month = MonthField(help_text="The month on which the batch is expected to start their medical internship")

    objects = BatchQuerySet.as_manager()

    @property
    def is_outside(self):
        return not (self.is_ksauhs or self.is_agu)

    def clean(self):
        """
        (1)
        A batch can't have both `is_ksauhs` and `is_agu` flags True at the same time.

        (2)
        Batches of the same kind (ksauhs, agu, outside) shouldn't overlap; i.e. each batch has a 12-month period
        beginning at the start_month that should not intersect with that of any other batches of the same kind.

        This is particularly important when sorting interns into batches upon sign-up, since each intern is sorted
        into the correct batch based his/her internship start_month. Having overlapping batches will result in
        failure to locate the intern into the right batch.
        """
        errors = []

        # (1)
        if self.is_ksauhs and self.is_agu:
            errors.append(
                ValidationError(
                    "A batch can't be both a KSAU-HS batch and an AGU batch at the same time."
                )
            )

        # (2)
        # Get a list of the months already reserved by existing batches of the same kind
        if self.is_ksauhs:
            batches = self.__class__.objects.ksauhs()
        elif self.is_agu:
            batches = self.__class__.objects.agu()
        else:
            batches = self.__class__.objects.outside()

        # Exclude self if it's in the db
        if self.id:
            batches = batches.exclude(id=self.id)

        start_months = batches.values_list('start_month', flat=True)
        all_months = list()

        for month in start_months:
            for add in range(12):
                all_months.append(month + add)

        # Check that the current batch's start month doesn't exist in `all_months`
        if self.start_month in all_months:
            errors.append(
                ValidationError(
                    "Can't have two overlapping batches of the same type. Please change the batch's start "
                    "month so it's within 12 months of any other batch's start month."
                )
            )
        if errors:
            raise ValidationError(errors)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Batches"
        ordering = ('-start_month',)
