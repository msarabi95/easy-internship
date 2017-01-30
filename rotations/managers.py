from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models


class RotationManager(models.Manager):
    def current_for_month(self, month):
        try:
            return self.get(month=month)
        except ObjectDoesNotExist:
            return None

    def non_electives(self):
        return self.filter(is_elective=False)

    def electives(self):
        return self.filter(is_elective=True)


class RotationRequestQuerySet(models.QuerySet):
    def month(self, month):
        """
        Return rotation requests for a particular month.
        """
        return self.filter(month=month)

    def unreviewed(self):
        """
        Return rotation requests that don't have a response nor forward.
        """
        return self.filter(response__isnull=True, forward__isnull=True)

    def forwarded_unreviewed(self):
        """
        Return rotation requests that have been forwarded but are awaiting response.
        """
        return self.filter(forward__isnull=False, response__isnull=True)

    def open(self):
        """
        Return rotation requests that don't yet have a response.
        Equivalent to `unreviewed` + `forwarded_unreviewed`.
        """
        return self.filter(response__isnull=True)

    def closed(self):
        """
        Return rotation requests that have received either a response or a forward response.
        """
        return self.exclude(response__isnull=True, forward__isnull=True)

    def current_for_month(self, month):
        """
        Return the current open request for a specific month.
        (There should only be one open request per month at a time.)
        """
        # This only has meaning when filtering requests for a specific internship
        open_requests = self.month(month).open()
        if open_requests.count() > 1:
            raise MultipleObjectsReturned(
                "Expected at most 1 open rotation request for the month %s, found %d!" % (
                    month.first_day().strftime("%B %Y"),
                    open_requests.count()
                )
            )
        try:
            return open_requests.latest("submission_datetime")
        except ObjectDoesNotExist:
            return None

    def memo_required(self):
        """
        Return rotation requests that require a memo.
        """
        pass  # TODO

    def no_memo_required(self):
        """
        Return rotation requests that don't require a memo.
        """
        pass  # TODO

    def kamc(self):
        """
        Return rotation requests for KAMC.
        """
        return self.filter(hospital__is_kamc=True)

    def outside(self):
        """
        Return rotation requests for outside hospitals.
        """
        return self.filter(hospital__is_kamc=False)
