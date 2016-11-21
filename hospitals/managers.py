from django.db import models


class SpecialtyManager(models.Manager):
    def general(self):
        return self.filter(parent_specialty__isnull=True)