from accounts.models import Profile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_nyt.models import Settings as NYTSettings
from django_nyt.utils import subscribe
from planner.models import Internship


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

        subscribe(settings, "plan_request_submitted")


@receiver(post_save, sender=Internship)
def set_up_intern_notification_subscriptions(sender, instance, created, **kwargs):
    if created:
        settings = instance.intern.profile.user.settings_set.first()

        subscribe(settings, "rotation_request_approved", object_id=instance.id)
        subscribe(settings, "rotation_request_declined", object_id=instance.id)


@receiver(post_delete, sender=Profile)
def clean_up_notifications(sender, instance, **kwargs):
    # Delete all notification settings and subscriptions
    settings = instance.user.settings_set.all()
    settings.delete()
