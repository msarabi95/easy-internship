from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from month.models import MonthField

from hospitals.managers import SpecialtyManager
from rotations.models import Rotation, RotationRequest


class Hospital(models.Model):
    name = models.CharField(max_length=128)
    abbreviation = models.CharField(max_length=16)
    is_kamc = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Specialty(models.Model):
    name = models.CharField(max_length=128)
    abbreviation = models.CharField(max_length=4)
    required_months = models.PositiveIntegerField()
    parent_specialty = models.ForeignKey("Specialty", related_name="subspecialties", null=True,
                                         blank=True)

    objects = SpecialtyManager()

    def is_subspecialty(self):
        """
        Return True if the specialty has a parent_specialty.
        """
        if self.parent_specialty is not None:
            return True
        else:
            return False

    def get_general_specialty(self):
        """
        Return `self` if already a general specialty (no parent specialty).
        Return parent specialty otherwise.
        """
        if not self.is_subspecialty():
            return self
        else:
            return self.parent_specialty

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Specialties"


#
# General Specialties, General Departments
# ========================================
#
#     Specialty 1 ----- * Department
#         1                   1
#         |                   |
#         |                   |
#         |                   |
#         *                   *
#     Specialty 1 ----- * Department
#
# ========================================
# Subspecialties, Sub-departments (Sections)
#


class Department(models.Model):
    hospital = models.ForeignKey(Hospital, related_name="departments")
    parent_department = models.ForeignKey("Department", related_name="sections", null=True,
                                          blank=True)
    name = models.CharField(max_length=128)
    specialty = models.ForeignKey(Specialty, related_name="departments")
    contact_name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    phone = models.CharField(max_length=128)
    extension = models.CharField(max_length=16)

    def get_available_seats(self, month):
        """
        Return the number of available seats for a specific month.
        """
        try:
            return self.seats.get(month=month).total_seats
        except DepartmentMonthSettings.DoesNotExist:
            return None

    def get_contact_details(self):
        """
        Return the contact details of the department if saved.
        If no details are supplied, return the details of the parent department.
        """
        if self.email != "":
            return {
                "contact_name": self.contact_name,
                "email": self.email,
                "phone": self.phone,
                "extension": self.extension,
            }
        elif self.parent_department is not None:
            return self.parent_department.get_contact_details()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.hospital.abbreviation)


FCFS_ACCEPTANCE = "FCFS"
GPA_ACCEPTANCE = "GPA"
ACCEPTANCE_CRITERION_CHOICES = (
    (FCFS_ACCEPTANCE, "First-come, First-serve"),
    (GPA_ACCEPTANCE, "GPA"),
)


class NonMonthSettingsMixin(object):
    """
    A mixin containing a `save` method common to `GlobalSettings` and `DepartmentSettings`
    """
    def save(self, *args, **kwargs):
        # If saving for the first time, make sure either start date interval or end date interval
        # is specified, based on selected criterion
        if not self.id:
            if self.acceptance_criterion == FCFS_ACCEPTANCE and self.acceptance_start_date_interval is None:
                self.acceptance_start_date_interval = 30
            elif self.acceptance_criterion == GPA_ACCEPTANCE and self.acceptance_end_date_interval is None:
                self.acceptance_end_date_interval = 30

        # Validate consistency
        if (self.acceptance_criterion == FCFS_ACCEPTANCE and self.acceptance_start_date_interval is None) \
           or (self.acceptance_criterion == GPA_ACCEPTANCE and self.acceptance_end_date_interval is None):
            raise ValidationError("Either a start or an end date interval should be specified.")

        super(NonMonthSettingsMixin, self).save(*args, **kwargs)

    def get_acceptance_start_or_end_date(self, month):
        """

        Args:
            month: `Month` instance.

        Returns: Depending on the acceptance criterion, the start or end date is calculated and returned.

        """
        month_as_date = month.first_day()  # this returns an instance of datetime.date
        month_first_day = timezone.make_aware(datetime(
            year=month_as_date.year,
            month=month_as_date.month,
            day=month_as_date.day,
            hour=0, minute=0, second=0, microsecond=0
        ))
        if self.acceptance_criterion == FCFS_ACCEPTANCE:
            start_date = month_first_day - timedelta(days=self.acceptance_start_date_interval)
            return start_date
        elif self.acceptance_criterion == GPA_ACCEPTANCE:
            end_date = month_first_day - timedelta(days=self.acceptance_end_date_interval)
            return end_date


class MonthSettingsMixin(object):
    """
    A mixin containing a `save` method common to `MonthSettings` and `DepartmentMonthSettings`
    """
    def save(self, *args, **kwargs):
        # If saving for the first time, make sure either start date or end date is specified
        # based on selected criterion
        if not self.id:
            if self.acceptance_criterion == FCFS_ACCEPTANCE and self.acceptance_start_date is None:
                self.acceptance_start_date = self.month.first_day() - timedelta(days=30)
            elif self.acceptance_criterion == GPA_ACCEPTANCE and self.acceptance_end_date is None:
                self.acceptance_end_date = self.month.first_day() - timedelta(days=30)

        # Validate consistency
        if (self.acceptance_criterion == FCFS_ACCEPTANCE and self.acceptance_start_date is None) \
           or (self.acceptance_criterion == GPA_ACCEPTANCE and self.acceptance_end_date is None):
            raise ValidationError("Either a start or an end date should be specified.")

        super(MonthSettingsMixin, self).save(*args, **kwargs)

    def get_acceptance_start_or_end_date(self, month=None):
        """

        Args:
            month: `Month` instance. Optional.

        Returns: Depending on the acceptance criterion, either the start date or end date is returned.

        """
        if self.acceptance_criterion == FCFS_ACCEPTANCE:
            return self.acceptance_start_date
        elif self.acceptance_criterion == GPA_ACCEPTANCE:
            return self.acceptance_end_date


class GlobalSettings(NonMonthSettingsMixin, models.Model):
    """
    A model that saves global acceptance settings.
    Only ONE instance of this model should be saved to the database.
    """
    acceptance_criterion = models.CharField(
        max_length=4,
        choices=ACCEPTANCE_CRITERION_CHOICES,
        default=FCFS_ACCEPTANCE
    )
    acceptance_start_date_interval = models.PositiveIntegerField(blank=True, null=True)
    acceptance_end_date_interval = models.PositiveIntegerField(blank=True, null=True)


class MonthSettings(MonthSettingsMixin, models.Model):
    """
    Acceptance settings for a particular month.
    """
    month = MonthField(unique=True)
    acceptance_criterion = models.CharField(
        max_length=4,
        choices=ACCEPTANCE_CRITERION_CHOICES,
        default=FCFS_ACCEPTANCE
    )
    acceptance_start_date = models.DateTimeField(blank=True, null=True)
    acceptance_end_date = models.DateTimeField(blank=True, null=True)


class DepartmentSettings(NonMonthSettingsMixin, models.Model):
    """
    Acceptance settings for a particular department.
    """
    department = models.OneToOneField(Department, related_name="acceptance_settings")
    acceptance_criterion = models.CharField(
        max_length=4,
        choices=ACCEPTANCE_CRITERION_CHOICES,
        default=FCFS_ACCEPTANCE
    )
    acceptance_start_date_interval = models.PositiveIntegerField(blank=True, null=True)
    acceptance_end_date_interval = models.PositiveIntegerField(blank=True, null=True)


class DepartmentMonthSettings(MonthSettingsMixin, models.Model):
    """
    Acceptance settings for a particular department during a particular month
    """
    month = MonthField()
    department = models.ForeignKey(Department, related_name="monthly_settings")
    total_seats = models.PositiveIntegerField()
    acceptance_criterion = models.CharField(
        max_length=4,
        choices=ACCEPTANCE_CRITERION_CHOICES,
        blank=True, null=True
    )
    acceptance_start_date = models.DateTimeField(blank=True, null=True)
    acceptance_end_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "Acceptance settings in %s during %s" % (self.department.__unicode__(),
                                                        self.month)

    class Meta:
        unique_together = ("month", "department")


class AcceptanceSetting(object):
    """
    Acceptance setting for a particular department in a particular month.
    """
    def __init__(self, department, month):
        """

        Get settings for a month-department pair using the following sequence:
        (1) If there's a DepartmentMonthSetting, use it.
        (2) If not, look for a DepartmentSetting.
        (3) If there isn't one, look for a MonthSetting.
        (4) If there isn't one, use global settings.

        Args:
            department: A `Department` instance.
            month: A `Month` instance.

        """
        total_seats = None
        try:
            settings_object = DepartmentMonthSettings.objects.get(department=department, month=month)
            total_seats = settings_object.total_seats
            if not settings_object.acceptance_criterion:
                raise ObjectDoesNotExist
            setting_type = 'DM'
        except ObjectDoesNotExist:
            try:
                settings_object = DepartmentSettings.objects.get(department=department)
                setting_type = 'D'
            except ObjectDoesNotExist:
                try:
                    settings_object = MonthSettings.objects.get(month=month)
                    setting_type = 'M'
                except ObjectDoesNotExist:
                    # Import is local to avoid cyclic import issues
                    from hospitals.utils import get_global_settings

                    settings_object = get_global_settings()
                    setting_type = 'G'

        self.month = month
        self.department = department

        self.type = setting_type
        self.criterion = settings_object.acceptance_criterion
        self.start_or_end_date = settings_object.get_acceptance_start_or_end_date(month)
        self.total_seats = total_seats

    # TODO: Implement as properties
    def get_booked_seats(self):
        if self.total_seats is None:
            return None
        return RotationRequest.objects.open().month(self.month).\
            filter(requested_department__department=self.department).count()
        # FIXME: what about departments not in db?
        # FIXME: Exclude declined requests
        # FIXME: Exclude cancellation requests

    def get_occupied_seats(self):
        if self.total_seats is None:
            return None
        return Rotation.objects.filter(department=self.department, month=self.month).count()

    def get_unoccupied_seats(self):
        if self.total_seats is None:
            return None
        return self.total_seats - self.get_occupied_seats()

    def get_available_seats(self):
        if self.total_seats is None:
            return None
        return self.total_seats - (self.get_booked_seats() + self.get_occupied_seats())

    def can_submit_requests(self):
        """

        Returns: True or False, depending on whether it's possible to submit requests for this department-month pair.

        """
        if self.total_seats is None:
            # If no seat count is specified, then requests can be submitted any time
            return True
        else:
            # If a seat count is specified, check acceptance criterion
            if self.criterion == GPA_ACCEPTANCE:
                # When the criterion is GPA, the only factor to permit submissions is whether the end date has been
                # reached or not (Available seat count isn't a factor)
                return timezone.now() < self.start_or_end_date
            elif self.criterion == FCFS_ACCEPTANCE:
                # A sanity check
                if self.get_available_seats() >= 0:
                    if self.get_available_seats() > 0 and timezone.now() >= self.start_or_end_date:
                        # Requests can be submitted when start date has passed, AND there is at least 1
                        # available seat
                        return True
                    else:
                        # If available seats equals 0, or start date hasn't passed yet,
                        # then no requests can be submitted
                        return False
                else:
                    raise ValueError("Unexpected value of available seats.")