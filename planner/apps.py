from __future__ import unicode_literals

from django.apps import AppConfig


class PlannerConfig(AppConfig):
    name = 'planner'

    def ready(self):
        from django_nyt.models import NotificationType

        # Create a `NotificationType` for each type of notification

        ##############################
        # (1) Staff Notification Types
        ##############################

        NotificationType.objects.get_or_create(key="plan_request_submitted",
                                               label="Plan Request Submitted")

        ###############################
        # (2) Intern Notification Types
        ###############################

        NotificationType.objects.get_or_create(key="rotation_request_approved",
                                               label="Rotation Request Approved")

        NotificationType.objects.get_or_create(key="rotation_request_declined",
                                               label="Rotation Request Declined")
