from __future__ import unicode_literals

from django.apps import AppConfig


class HospitalsConfig(AppConfig):
    name = 'hospitals'

    def ready(self):
        from . import signals