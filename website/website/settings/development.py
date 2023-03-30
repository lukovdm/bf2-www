import os

from website.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "x%ts1gsfjnb&2-s4567^*$82ukdr-!%c)3t3yf&&wa3o9636uq"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "../../db.sqlite3"),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

SASS_PROCESSOR_ROOT = STATIC_ROOT

MEDIA_URL = "/media/"
# MEDIA_ROOT = os.path.join(BASE_DIR, "media")
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_REGION_NAME = "eu-central-003"
AWS_STORAGE_BUCKET_NAME = "BFrisBee2s-Media"
AWS_S3_ENDPOINT_URL = "https://s3.eu-central-003.backblazeb2.com"
AWS_PRELOAD_METADATA = False

# Email settings
# https://docs.djangoproject.com/en/3.1/topics/email/
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
