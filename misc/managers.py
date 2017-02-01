from django.db import models


class AnnouncementManager(models.Manager):
    def published(self):
        return self.filter(is_published=True)

    def draft(self):
        return self.filter(is_published=False)
