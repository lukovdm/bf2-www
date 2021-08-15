import os

from website.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [".bfrisbee2s.nl", "bf2.luko.dev", "localhost"]

SESSION_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": int(os.environ.get("DATABASE_PORT", 5432)),
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    }
}

EMAIL_HOST = "smtp-relay.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "no-reply@bfrisbee2s.nl"

ADMINS = [("Webmasters", "webmaster@bfrisbee2s.nl")]

STATIC_ROOT = "/bf2-www/static/"
STATIC_URL = "/static/"

SASS_PROCESSOR_ROOT = STATIC_ROOT

MEDIA_ROOT = "/bf2-www/media"
MEDIA_URL = "/media/"
