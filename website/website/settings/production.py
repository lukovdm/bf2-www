from website.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [".bfrisbee2s.nl", "bf2.luko.dev", "localhost"]

CSRF_TRUSTED_ORIGINS = [
    "https://bfrisbee2s.nl",
    "http://localhost",
    "https://bf2.luko.dev",
]

SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

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

DJANGOCMS_GOOGLEMAP_API_KEY = os.environ.get("GOOGLE_MAPS_KEY")

EMAIL_HOST = "smtp-relay.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "no-reply@bfrisbee2s.nl"

SERVER_EMAIL = "ohnee@bfrisbee2s.nl"

ADMINS = [("Webmasters", "webmaster@bfrisbee2s.nl")]

STATIC_ROOT = "/bf2-www/static/"
STATIC_URL = "/static/"

SASS_PROCESSOR_ROOT = STATIC_ROOT

MEDIA_ROOT = "/bf2-www/media"
MEDIA_URL = "/media/"
