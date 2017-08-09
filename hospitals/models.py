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

    contact_name = models.CharField(max_length=128, blank=True)
    contact_position = models.CharField(max_length=128, blank=True)
    email = models.EmailField(max_length=128, blank=True)
    phone = models.CharField(max_length=128, blank=True)
    extension = models.CharField(max_length=16, blank=True)

    has_requirement = models.BooleanField("Has special requirements?", default=False)
    requirement_description = models.TextField(blank=True, null=True)
    requirement_file = models.FileField(upload_to='hospital_requirements', blank=True, null=True)

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
    contact_position = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    phone = models.CharField(max_length=128)
    extension = models.CharField(max_length=16)

    requires_memo = models.BooleanField(default=True)
    memo_handed_by_intern = models.BooleanField(default=True)

    has_requirement = models.BooleanField("Has special requirements?", default=False)
    requirement_description = models.TextField(blank=True, null=True)
    requirement_file = models.FileField(upload_to='hospital_requirements', blank=True, null=True)

    @property
    def display_label(self):
        """
        A little hack to display specialty name with location name if needed.
        """
        expected_dept_name = "Department of %s" % self.specialty.name
        if expected_dept_name != self.name:
            try:
                return "%s @ %s" % (
                    self.specialty.name,
                    self.name.split(expected_dept_name + " - ")[1],
                )
            except IndexError:
                pass
        return self.specialty.name

    @property
    def display_label_short(self):
        """
        Another little hack to shorten the specialty name while preserving the name of the subspecialty & location.
        This is used to save some space when displaying the name.
        
        E.g. 'Internal Medicine' => 'MED'
        E.g. 'Obstetrics & Gynecology - General' => 'OBGY (General)'
        E.g. 'Family Medicine @ Ummalhamam' => 'FM @ Ummalhamam'
        E.g. 'Surgery - Orthopedics @ Surgical Tower' => 'SURG (Orthopedics) @ Surgical Tower'
        """
        display_label = self.display_label
        short_label = [self.specialty.abbreviation]

        if " - " in display_label:
            specialty_name = display_label.split(" @ ")[0] if " @ " in display_label else display_label
            subspecialty = specialty_name.split(" - ")[1]
            short_label.append("(%s)" % subspecialty)

        if " @ " in display_label:
            location = display_label.split(" @ ")[1]
            short_label.append("@ %s" % location)

        return " ".join(short_label)

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
                "contact_position": self.contact_position,
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
    def __init__(self, department, month, department_month_settings=None, month_settings=None,
                                   department_settings=None, global_settings=None):
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
            if not department_month_settings:
                settings_object = DepartmentMonthSettings.objects.get(department=department, month=month)
            else:
                settings_object = filter(lambda dms: dms.department == department and dms.month == month, department_month_settings)[0]
            total_seats = settings_object.total_seats
            if not settings_object.acceptance_criterion:
                raise ObjectDoesNotExist
            setting_type = 'DM'
        except (ObjectDoesNotExist, IndexError):
            try:
                if not department_settings:
                    settings_object = DepartmentSettings.objects.get(department=department)
                else:
                    settings_object = filter(lambda ds: ds.department == department, department_settings)[0]
                setting_type = 'D'
            except (ObjectDoesNotExist, IndexError):
                try:
                    if not month_settings:
                        settings_object = MonthSettings.objects.get(month=month)
                    else:
                        settings_object = filter(lambda ms: ms.month == month, month_settings)[0]
                    setting_type = 'M'
                except (ObjectDoesNotExist, IndexError):
                    if not global_settings:
                        # Import is local to avoid cyclic import issues
                        from hospitals.utils import get_global_settings
                        settings_object = get_global_settings()
                    else:
                        settings_object = global_settings
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
        seats = self.total_seats - (self.get_booked_seats() + self.get_occupied_seats())
        return seats if seats >= 0 else 0

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
                    return False
                    #raise ValueError("Unexpected value of available seats.")


class SeatSetting(object):
    """
    An object that contains the seat counts for a particular month and department.
    This class is optimized to minimize database calls when seat counts are required in bulk (e.g. when
     display a list of all seat counts for all departments). The passed department should have
     its `monthly_settings`, `rotations`, and `department_requests__rotationrequest__response` prefetched
     for optimal performance.
    """
    def __init__(self, department, month):
        self.department = department
        self.month = month

        department_month_settings = \
            filter(lambda dms: dms.month == self.month, self.department.monthly_settings.all())
        self.dms = department_month_settings[0] if len(department_month_settings) > 0 else None
        # Is it better to raise an exception rather than set self.dms to None?

    def get_total_seats(self):
        if self.dms is None:
            return None
        return self.dms.total_seats

    def get_occupied_seats(self):
        if self.dms is None:
            return None
        rotas = filter(lambda r: r.month == self.month, self.department.rotations.all())
        return len(rotas)

    def get_booked_seats(self):
        if self.dms is None:
            return None
        requests = filter(
            lambda rd: hasattr(rd, 'rotationrequest')
                       and rd.rotationrequest.month == self.month
                       and rd.rotationrequest.is_delete == False
                       and not hasattr(rd.rotationrequest, 'response'),
            self.department.department_requests.all()
        )
        return len(requests)

    def get_available_seats(self):
        if self.dms is None:
            return None
        seats = self.total_seats - (self.occupied_seats + self.booked_seats)
        return seats if seats >= 0 else 0

    total_seats = property(get_total_seats)
    occupied_seats = property(get_occupied_seats)
    booked_seats = property(get_booked_seats)
    available_seats = property(get_available_seats)


class SeatAvailability(DepartmentMonthSettings):
    """
    Currently this is just a proxy for `DepartmentMonthSettings` model in order to customize the admin interface; but
    later all the information related to seat availabilities should be moved here instead.
    """
    class Meta:
        proxy = True
        verbose_name_plural = "Seat availabilities"
