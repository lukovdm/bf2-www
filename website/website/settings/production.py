import dj_database_url

from website.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["bf2-website.fly.dev", ".bfrisbee2s.nl", "bf2.luko.dev", "localhost"]

CSRF_TRUSTED_ORIGINS = [
    "https://bfrisbee2s.nl",
    "http://localhost",
    "https://bf2.luko.dev",
    "https://bf2-website.fly.dev",
]

SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    ),
}

DJANGOCMS_GOOGLEMAP_API_KEY = os.environ.get("GOOGLE_MAPS_KEY")

EMAIL_HOST = "smtp-relay.gmail.com"
EMAIL_HOST_USER = "support@bfrisbee2s.nl"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "no-reply@bfrisbee2s.nl"

SERVER_EMAIL = "support@bfrisbee2s.nl"

ADMINS = [("Webmasters", "webmasters@bfrisbee2s.nl")]

# Static files
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_REGION_NAME = "us-west-000"
AWS_STORAGE_BUCKET_NAME = "BFrisBee2s-Media"
AWS_S3_ENDPOINT_URL = "https://s3.us-west-000.backblazeb2.com"
AWS_PRELOAD_METADATA = False

STATIC_ROOT = "/bf2-www/static/"
STATIC_URL = "/static/"

SASS_PROCESSOR_ROOT = STATIC_ROOT

MEDIA_URL = "/media/"

# Logging
INSTALLED_APPS += ["django_prometheus"]
MIDDLEWARE.insert(0, "django_prometheus.middleware.PrometheusBeforeMiddleware")
MIDDLEWARE.append("django_prometheus.middleware.PrometheusAfterMiddleware")

PROMETHEUS_METRICS_EXPORT_PORT = 9091
PROMETHEUS_METRICS_EXPORT_ADDRESS = "0.0.0.0"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "applogfile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join("/APPNAME.log"),
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "APPNAME": {
            "handlers": [
                "applogfile",
            ],
            "level": "DEBUG",
        },
    },
}
