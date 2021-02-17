from cms.models import PlaceholderField
from django.contrib.auth.models import User
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    IntegerField,
    CASCADE,
    BooleanField,
    ForeignKey,
)
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from utils.translations import ModelTranslateMeta, MultilingualField


class Event(Model, metaclass=ModelTranslateMeta):
    """An event with no registrations in itself"""

    name = MultilingualField(CharField, max_length=255, verbose_name=_("name"))
    date = DateTimeField(verbose_name=_("date"))
    location = CharField(max_length=255, verbose_name=_("location"))
    description = PlaceholderField("description", verbose_name=_("description"))

    limit = IntegerField(null=True, blank=True, verbose_name=_("participant limit"))
    cost = IntegerField(null=True, blank=True, verbose_name=_("cost"))
    registration_start = DateTimeField(
        null=True, blank=True, verbose_name=_("registration start")
    )
    registration_end = DateTimeField(
        null=True, blank=True, verbose_name=_("registration end")
    )

    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"pk": self.pk})


class Registration(Model):
    """Registration of a user to a registrable event"""

    event = ForeignKey(Event, CASCADE, verbose_name=_("event"))
    user = ForeignKey(User, CASCADE, verbose_name=_("user"))

    date = DateTimeField(default=now, verbose_name=_("registration date"))
    has_payed = BooleanField(null=True, blank=True, verbose_name=_("has paid"))
