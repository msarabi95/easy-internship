from django.db import models


class UniversityManager(models.Manager):
    def ksauhs(self):
        """
        Return a queryset containing King Saud bin Abdulaziz University for Health Sciences.
        """
        return self.filter(is_ksauhs=True)

    def agu(self):
        """
        Return a queryset containing Arabian Gulf University.
        """
        return self.filter(is_agu=True)

    def outside(self):
        """
        Return a queryset containing all universities other than KSAU-HS and AGU.
        """
        return self.filter(is_ksauhs=False, is_agu=False)


class BatchQuerySet(models.QuerySet):
    def ksauhs(self):
        """
        Return a queryset containing King Saud bin Abdulaziz University for Health Sciences batches.
        """
        return self.filter(is_ksauhs=True)

    def agu(self):
        """
        Return a queryset containing Arabian Gulf University batches.
        """
        return self.filter(is_agu=True)

    def outside(self):
        """
        Return a queryset containing all universities' batches other than KSAU-HS and AGU.
        """
        return self.filter(is_ksauhs=False, is_agu=False)

    def for_user(self, start_month, university):
        """
        Return a queryset containing the batches whose start months occur at the same month as the intern's
        start month, or up to 11 months back; in addition to matching the intern's university type.
        """
        intern_start = start_month
        intern_university = university
        return self.filter(
            is_ksauhs=intern_university.is_ksauhs,
            is_agu=intern_university.is_agu,
            start_month__range=(intern_start - 11, intern_start)
        )
