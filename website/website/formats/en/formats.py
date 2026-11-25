# Since Django 5.0 localized formats always take precedence over the
# DATE_INPUT_FORMATS and DATETIME_INPUT_FORMATS settings. Use the formats from
# the settings for every language, so e.g. 01/02/2001 is always parsed as
# 1 February and not as January 2 in English.
from django.conf import settings

DATE_INPUT_FORMATS = settings.DATE_INPUT_FORMATS
DATETIME_INPUT_FORMATS = settings.DATETIME_INPUT_FORMATS
