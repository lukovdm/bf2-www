from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from filer.fields.file import FilerFileField
from django.utils import timezone
from django.core.exceptions import ValidationError


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

    pronouns = models.CharField(
        blank=True, null=True, max_length=256, verbose_name=_("pronouns")
    )

    phone_number = models.CharField(max_length=16, verbose_name=_("phone number"))

    street_address = models.CharField(
        max_length=255, verbose_name=_("street name and house number")
    )

    postcode = models.CharField(
        max_length=64,
        validators=[
            RegexValidator(
                regex="^[\\s\\da-zA-Z]+$",
                message=_("postcode can only contain spaces, digits and letters"),
                code="invalid_postcode",
            )
        ],
        verbose_name=_("zipcode"),
    )

    city = models.CharField(max_length=52, verbose_name=_("city"))

    student_type = models.CharField(
        max_length=3, choices=TYPE_STUDENT, verbose_name=_("type of student")
    )

    sports_card_number = models.CharField(
        max_length=10,
        verbose_name=_("sports card number"),
        validators=[
            RegexValidator(
                regex="^[sueSUE]?\\d{6,8}$",
                message=_("sports card number has invalid form"),
                code="invalid_sports_card_number",
            ),
        ],
    )

    graduation_date = models.DateField(
        verbose_name=_("graduation date"), blank=True, null=True
    )

    other_club = models.ForeignKey(
        OtherClub,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("other club"),
    )

    preferred_language = models.CharField(
        choices=settings.LANGUAGES,
        default="nl",
        max_length=3,
        verbose_name=_("preferred_language"),
    )

    google_email = models.EmailField(verbose_name=_("google email"))

    picture_publication_acceptation = models.BooleanField(
        verbose_name=_("allowed to publish pictures of")
    )

    def clean(self) -> None:
        if self.birthday and self.birthday > timezone.now().date():
            raise ValidationError({"birthday": _("Your birthday must lay in the past")})

    def save(self, *args, **kwargs):
        self.sports_card_number = self.sports_card_number.lower()
        super().save(*args, **kwargs)

    class Meta:
        permissions = (("can_accept_or_reject", _("can accept or reject")),)

    def __str__(self):
        return "Member: {}".format(self.user.first_name)


class MemberSettings(models.Model):
    privacyFile = FilerFileField(null=True, blank=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if MemberSettings.objects.exists():
            raise ValueError("This model already has its record.")
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return "Settings"
