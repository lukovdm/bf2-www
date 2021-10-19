from cms.models import PlaceholderField
from django.contrib.auth.models import User
from django.core.validators import URLValidator, RegexValidator
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    IntegerField,
    CASCADE,
    BooleanField,
    ForeignKey,
    ImageField,
    SET_NULL,
    DecimalField,
)
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from filer.fields.image import FilerImageField

from utils.translations import ModelTranslateMeta, MultilingualField


class Event(Model, metaclass=ModelTranslateMeta):
    """An event with no registrations in itself"""

    name = MultilingualField(CharField, max_length=255, verbose_name=_("name"))
    image = FilerImageField(
        verbose_name=_("image"), null=True, blank=True, on_delete=SET_NULL
    )
    start_date = DateTimeField(verbose_name=_("start date"))
    end_date = DateTimeField(verbose_name=_("end date"))
    location = CharField(max_length=255, verbose_name=_("location"))
    description = PlaceholderField("description", verbose_name=_("description"))

    limit = IntegerField(null=True, blank=True, verbose_name=_("participant limit"))
    cost = DecimalField(
        null=True, blank=True, verbose_name=_("cost"), max_digits=7, decimal_places=2
    )
    registration_start = DateTimeField(
        null=True, blank=True, verbose_name=_("registration start")
    )
    registration_end = DateTimeField(
        null=True, blank=True, verbose_name=_("registration end")
    )

    form_link = CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_("Google form link"),
        validators=[
            RegexValidator(
                regex="https:\/\/docs\.google\.com\/forms\/d\/e\/[\w\d_]*\/viewform\?",
                message=_("Please enter a google form share link"),
            ),
        ],
    )

    def save(self, *args, **kwargs):
        if self.form_link and not self.form_link.endswith("embedded=true"):
            embed_form_link = self.form_link.strip()
            embed_form_link = embed_form_link.removesuffix("usp=sf_link")
            self.form_link = embed_form_link + "embedded=true"

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.name} at {self.start_date}"


class Registration(Model):
    """Registration of a user to a registrable event"""

    event = ForeignKey(Event, CASCADE, verbose_name=_("event"))
    user = ForeignKey(User, CASCADE, verbose_name=_("user"))

    date = DateTimeField(default=now, verbose_name=_("registration date"))
    has_payed = BooleanField(null=True, blank=True, verbose_name=_("has paid"))
