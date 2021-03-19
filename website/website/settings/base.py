"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 3.0.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_ID = 1

X_FRAME_OPTIONS = "SAMEORIGIN"

LOGIN_URL = "/user/login/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/"

# about 3 months
ACCOUNT_ACTIVATION_TIMEOUT = 60 * 60 * 24 * 30 * 3

CMS_PERMISSION = True

CMS_TEMPLATES = [
    ("page.html", "Page"),
    ("feature.html", "Page with Feature"),
]

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)

MESSAGE_TAGS = {
    message_constants.DEBUG: "dark",
    message_constants.INFO: "info",
    message_constants.SUCCESS: "success",
    message_constants.WARNING: "warning",
    message_constants.ERROR: "danger",
}

# Application definition

INSTALLED_APPS = [
    "djangocms_admin_style",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Django cms
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    "djangocms_text_ckeditor",
    "filer",
    "easy_thumbnails",
    "mptt",
    "djangocms_link",
    "djangocms_file",
    "djangocms_picture",
    "djangocms_video",
    "djangocms_googlemap",
    "djangocms_snippet",
    "djangocms_style",
    "djangocms_column",
    "djangocms_icon",
    "djangocms_bootstrap4",
    "djangocms_bootstrap4.contrib.bootstrap4_alerts",
    "djangocms_bootstrap4.contrib.bootstrap4_badge",
    "djangocms_bootstrap4.contrib.bootstrap4_card",
    "djangocms_bootstrap4.contrib.bootstrap4_carousel",
    "djangocms_bootstrap4.contrib.bootstrap4_collapse",
    "djangocms_bootstrap4.contrib.bootstrap4_content",
    "djangocms_bootstrap4.contrib.bootstrap4_grid",
    "djangocms_bootstrap4.contrib.bootstrap4_jumbotron",
    "djangocms_bootstrap4.contrib.bootstrap4_link",
    "djangocms_bootstrap4.contrib.bootstrap4_listgroup",
    "djangocms_bootstrap4.contrib.bootstrap4_media",
    "djangocms_bootstrap4.contrib.bootstrap4_picture",
    "djangocms_bootstrap4.contrib.bootstrap4_tabs",
    "djangocms_bootstrap4.contrib.bootstrap4_utilities",
    # custom applications
    "members",
    "events",
    "boards",
    # installed libraries
    "import_export",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
    "cms.middleware.utils.ApphookReloadMiddleware",
]

ROOT_URLCONF = "website.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["website/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "website.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Django Import Export
# https://django-import-export.readthedocs.io/en/stable/installation.html#settings
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_IMPORT_PERMISSION_CODE = ("add",)
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = ("view",)

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("nl", "Dutch"),
]

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True
