import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "abcdef"
DEBUG = True

ALLOWED_HOSTS = []

ADMINS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root/')
POST_OFFICE_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

EMAIL_USE_TLS = True
EMAIL_HOST = ""
EMAIL_PORT = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""

DEFAULT_FROM_EMAIL = "noreply@example.com"
SERVER_EMAIL = "noreply@example.com"

SITE_ID = 1
LOG_FILENAME = "./log.log"

NYT_EMAIL_SENDER = "noreply@example.com"
SUPPORT_EMAIL_ADDRESS = "support@example.com"

CKEDITOR_UPLOAD_PATH = ""
