from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from filer.fields.file import FilerFileField


def user_directory_path(instance, filename):
    return 'profile_pic/user_{0}/{1}'.format(instance.user.id, filename)


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

    birthday = models.DateField(verbose_name=_("birth date"))

    MAN = "Man"
    WOMAN = "Woman"
    OTHER = "Other"
    UNSPECIFIED = "Unspecified"
    GENDER_CHOICES = [
        (MAN, _("man")),
        (WOMAN, _("woman")),
        (OTHER, _("other")),
        (UNSPECIFIED, _("unspecified")),
    ]

    gender = models.CharField(
        max_length=64, verbose_name=_("gender"), choices=GENDER_CHOICES
    )

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
        max_length=3, choices=TYPE_STUDENT, verbose_name=_("Where do you study?")
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

    other_club = models.BooleanField(verbose_name=_("other club"))

    preferred_language = models.CharField(
        choices=settings.LANGUAGES,
        default="nl",
        max_length=3,
        verbose_name=_("preferred language"),
    )

    google_email = models.EmailField(verbose_name=_("google email"))

    remarks = models.TextField(blank=True, null=True, verbose_name=_("remarks"))

    bio = models.TextField(
        blank=True, null=True, verbose_name=_("bio"), max_length=1000
    )
    profile_picture = models.ImageField(blank=True, null=True, upload_to=user_directory_path)

    FIRST_NAME = "Firstname"
    FULL_NAME = "Fullname"
    INITIALS = "Initials"
    NICK_NAME = "Nickname"
    FULL_NAME_NICKNAME = "FullnameNickname"
    FIRST_NAME_NICKNAME = "FirstnameNickname"
    DISPLAY_NAME_CHOICES = [
        (FIRST_NAME, _("First name")),
        (FULL_NAME, _("Full name")),
        (INITIALS, _("Initial with last name")),
        (NICK_NAME, _("Nickname")),
        (FULL_NAME_NICKNAME, _("Full name with nickname")),
        (FIRST_NAME_NICKNAME, _("First name with nickname")),
    ]

    display_name = models.CharField(
        max_length=64,
        verbose_name=_("display name"),
        choices=DISPLAY_NAME_CHOICES,
        default=FIRST_NAME,
    )
    nickname = models.CharField(
        max_length=64, verbose_name=_("nickname"), blank=True, null=True
    )

    def clean(self) -> None:
        if self.birthday and self.birthday > timezone.now().date():
            raise ValidationError({"birthday": _("Your birthday must lay in the past")})

    def save(self, *args, **kwargs):
        self.sports_card_number = self.sports_card_number.lower()
        super().save(*args, **kwargs)

    class Meta:
        permissions = (("can_accept_or_reject", _("can accept or reject")),)

    def name(self) -> str:
        if self.display_name == self.FIRST_NAME:
            return self.user.first_name
        elif self.display_name == self.FULL_NAME:
            return self.user.get_full_name()
        elif self.display_name == self.INITIALS:
            return self.user.first_name[0] + " " + self.user.last_name
        elif self.display_name == self.NICK_NAME:
            return f'"{self.nickname}"'
        elif self.display_name == self.FULL_NAME_NICKNAME:
            return f'{self.user.first_name} "{self.nickname}" {self.user.last_name}'
        elif self.display_name == self.FIRST_NAME_NICKNAME:
            return f'{self.user.first_name} "{self.nickname}"'

    def get_absolute_url(self):
        return reverse("members:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Member: {self.name()}"


class MemberSettings(models.Model):
    privacyFile = FilerFileField(null=True, blank=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if MemberSettings.objects.exists():
            raise ValueError("This model already has its record.")
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return "Settings"
