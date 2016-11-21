from django.core.exceptions import ImproperlyConfigured
from hospitals.models import GlobalSettings


# Global settings getter
def get_global_settings():
    if GlobalSettings.objects.count() > 1:
        raise ImproperlyConfigured
    elif GlobalSettings.objects.count() < 1:
        return GlobalSettings.objects.create()
    else:
        return GlobalSettings.objects.first()


# Acceptance settings getters
def get_global_acceptance_criterion():
    settings = get_global_settings()
    return settings.acceptance_criterion


def get_global_acceptance_start_date_interval():
    settings = get_global_settings()
    return settings.acceptance_start_date_interval


def get_global_acceptance_end_date_interval():
    settings = get_global_settings()
    return settings.acceptance_end_date_interval


# Acceptance settings getters
def set_global_acceptance_criterion(value):
    settings = get_global_settings()
    settings.acceptance_criterion = value
    settings.save()
    return settings.acceptance_criterion


def set_global_acceptance_start_date_interval(value):
    settings = get_global_settings()
    settings.acceptance_start_date_interval = value
    settings.save()
    return settings.acceptance_start_date_interval


def set_global_acceptance_end_date_interval(value):
    settings = get_global_settings()
    settings.acceptance_end_date_interval = value
    settings.save()
    return settings.acceptance_end_date_interval
