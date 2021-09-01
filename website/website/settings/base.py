"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 3.0.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_ID = 1

X_FRAME_OPTIONS = "SAMEORIGIN"

LOGIN_URL = "/user/login/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/"

# about 3 months
ACCOUNT_ACTIVATION_TIMEOUT = 60 * 60 * 24 * 30 * 3

CMS_PAGE_CACHE = False

CMS_PERMISSION = True

CMS_TEMPLATES = [
    ("page_cms.html", "Page"),
    ("fullpage_cms.html", "Page full page header"),
]

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)

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
    "django.contrib.sitemaps",
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
    # installed libraries
    "import_export",
    "ckeditor",
    "django_mail_template",
    "bootstrap5",
    "sass_processor",
    # custom applications
    "website",
    "members",
    "events",
    "boards",
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


def add_wow_context(request):
    return {"wow": "wowowo"}


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
                "website.settings.add_wow_context",
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

# Django sass processor
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]

SASS_PRECISION = 8

# TODO remove when no longer needed in future update
SASS_OUTPUT_STYLE = "compact"

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("nl", "Dutch"),
]

CMS_LANGUAGES = {
    1: [
        {
            "code": "en",
            "name": _("English"),
            "fallbacks": ["nl"],
            "hide_untranslated": True,
        },
        {
            "code": "nl",
            "name": _("Dutch"),
            "fallbacks": ["en"],
            "hide_untranslated": True,
        },
    ]
}

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
