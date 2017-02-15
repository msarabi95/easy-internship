from accounts.models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_nyt.models import Settings as NYTSettings
from django_nyt.utils import subscribe


@receiver(post_save, sender=Profile)
def set_up_notification_settings(sender, instance, created, **kwargs):
    if created:
        # Create a settings profile for notifications for the new user
        # Connecting the signal to `Profile` ensures this is only created
        # for "actual" users (interns and staff)
        profile = instance

        settings = NYTSettings(user=profile.user)
        settings.save()


@receiver(post_save, sender=Profile)
def set_up_staff_notification_subscriptions(sender, instance, **kwargs):
    if instance.role == Profile.STAFF:
        settings = instance.user.settings_set.first()

        subscribe(settings, "rotation_request_submitted")
        subscribe(settings, "rotation_cancel_request_submitted")
        subscribe(settings, "freeze_request_submitted")
        subscribe(settings, "freeze_cancel_request_submitted")
        subscribe(settings, "leave_request_submitted")
        subscribe(settings, "leave_cancel_request_submitted")
