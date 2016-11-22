from django.conf import settings


def settings_processor(request):
    return {
        'SUPPORT_EMAIL_ADDRESS': settings.SUPPORT_EMAIL_ADDRESS
    }
