from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Member(models.Model):
    """A model to hold all extra personal information about members."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    birthday = models.DateField()

    phone_number = models.CharField(max_length=16)

    street_address = models.CharField(
        max_length=255, verbose_name=_("Street address and house number")
    )

    postcode = models.CharField(
        max_length=7, validators=[RegexValidator("^\\d{4} ?[A-Za-z]{2}$")]
    )

    city = models.CharField(max_length=52)

    is_student = models.BooleanField()

    sports_card_number = models.CharField(max_length=10)

    graduation_date = models.DateField()
