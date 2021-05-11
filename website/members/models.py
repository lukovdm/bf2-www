from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class OtherClub(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name=_("other club"),
        unique=True,
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Member(models.Model):
    """A model to hold all extra personal information about members."""

    RU = "RU"
    HAN = "HAN"
    NOSTUDENT = "NS"
    TYPE_STUDENT = [
        (RU, _("Radboud University")),
        (HAN, _("HAN")),
        (NOSTUDENT, _("Not a student")),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    birthday = models.DateField(verbose_name=_("birthday"))

    gender = models.CharField(max_length=64, verbose_name=_("gender"))
    
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    UNSPECIFIED = "Unspecified"
    GENDER_CHOICES = [
        (MALE, _("male")),
        (FEMALE, _("female")),
        (OTHER, _("other")),
        (UNSPECIFIED, _("unspecified")),
    ]

    phone_number = models.CharField(max_length=16, verbose_name=_("phone number"))

    street_address = models.CharField(
        max_length=255, verbose_name=_("street name and house number")
    )

    postcode = models.CharField(
        max_length=7,
        validators=[RegexValidator("^\\d{4} ?[A-Za-z]{2}$")],
        verbose_name=_("zipcode"),
    )

    city = models.CharField(max_length=52, verbose_name=_("city"))

    student_type = models.CharField(
        max_length=3,
        choices=TYPE_STUDENT,
    )

    sports_card_number = models.CharField(
        max_length=10, verbose_name=_("sports card number")
    )

    graduation_date = models.DateField(verbose_name=_("graduation date"))

    other_club = models.ForeignKey(
        OtherClub,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("other club"),
    )

    preferred_language = models.CharField(
        choices=settings.LANGUAGES, default="nl", max_length=3
    )

    YES = "Yes"
    NO = "No"
    BOOL_CHOICES = [
        (YES , _("Yes")),
        (NO, _("No")),
    ]
    picture_publication_acceptation = models.BooleanField(choices=BOOL_CHOICES)

    class Meta:
        permissions = (("can_accept_or_reject", _("can accept or reject")),)
