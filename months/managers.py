from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models


class FreezeRequestQuerySet(models.QuerySet):
    def month(self, month):
        """
        Return freeze requests for a particular month.
        """
        return self.filter(month=month)

    def open(self):
        """
        Return freeze requests that don't have a response.
        """
        return self.filter(response__isnull=True)

    def closed(self):
        """
        Return freeze requests that have received response.
        """
        return self.filter(response__isnull=False)

    def current_for_month(self, month):
        """
        Return the current open request for a specific month.
        """
        # This only has meaning when filtering requests for a specific internship
        open_requests = self.month(month).open()
        if open_requests.count() > 1:
            raise MultipleObjectsReturned(
                "Expected at most 1 open freeze request for the month %s, found %d!" % (
                    month.first_day().strftime("%B %Y"),
                    open_requests.count()
                )
            )
        try:
            return open_requests.latest("submission_datetime")
        except ObjectDoesNotExist:
            return None
    
    
class FreezeManager(models.Manager):
    def current_for_month(self, month):
        """
        Return the current freeze for a particular month.
        """
        # This only has meaning when filtering requests for a specific internship
        try:
            return self.get(month=month)
        except ObjectDoesNotExist:
            return None
