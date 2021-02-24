from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class OtherClub(models.Model):
    name = models.CharField(max_length=64, verbose_name=_("other club"),
    )
    class Meta:
        ordering = ('name',)

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
        (NOSTUDENT,_("Not a student")),
    ]


    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    birthday = models.DateField(verbose_name=_("birthday"))

    phone_number = models.CharField(max_length=16, verbose_name=_("phone number"))

    street_address = models.CharField(
        max_length=255, verbose_name=_("street name and house number")
    )

    postcode = models.CharField(
        max_length=7,
        validators=[RegexValidator("^\\d{4} ?[A-Za-z]{2}$")],
        verbose_name=_("postcode"),
    )

    city = models.CharField(max_length=52, verbose_name=_("city"))


    student_type = models.CharField(
        max_length=3,
        choices=TYPE_STUDENT,
        verbose_name=_("student type"),
    )

    sports_card_number = models.CharField(
        max_length=10, verbose_name=_("sports card number")
    )

    graduation_date = models.DateField(verbose_name=_("graduation date"))

    other_club = models.ForeignKey(
        OtherClub,
        blank = True, 
        null = True,
        on_delete=models.CASCADE,
        verbose_name = _("other club"),
    )

    def clean(self):
        if self.is_student and self.student_type is None:
            raise ValidationError(
                _("You are a student so please indicate your student type")
            )


