from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from cms.models import PlaceholderRelationField
from cms.utils.placeholder import get_placeholder_from_slot
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    IntegerField,
    CASCADE,
    BooleanField,
    ForeignKey,
    SET_NULL,
)
from django.urls import reverse
from django.utils.functional import cached_property
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
    description = PlaceholderRelationField()

    limit = IntegerField(null=True, blank=True, verbose_name=_("participant limit"))
    private_registrations = BooleanField(
        default=False, verbose_name=_("Don't show who is registered")
    )
    cost = MultilingualField(
        CharField, null=True, max_length=255, verbose_name=_("cost")
    )

    registration_start = DateTimeField(
        null=True, blank=True, verbose_name=_("registration start")
    )
    registration_end = DateTimeField(
        null=True, blank=True, verbose_name=_("registration end")
    )
    show_end_date = BooleanField(default=True, verbose_name=_("Show end date"))

    form_link = CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name=_("Google form link"),
        validators=[
            RegexValidator(
                regex="https:\/\/docs\.google\.com\/forms\/d\/e\/[\w\d_-]*\/viewform\?",
                message=_("Please enter a google form share link"),
            ),
        ],
    )

    @cached_property
    def description_placeholder(self):
        return get_placeholder_from_slot(self.description, "description")

    def get_template(self):
        return "events/event_structure.html"

    def clean(self) -> None:
        if (self.registration_start is None) != (self.registration_end is None):
            raise ValidationError(
                {
                    "registration_start": _(
                        "Either both registration start and end need to be set, or neither."
                    ),
                    "registration_end": _(
                        "Either both registration start and end need to be set, or neither."
                    ),
                }
            )

        if (
            self.registration_start is not None
            and self.registration_start > self.registration_end
        ):
            raise ValidationError(
                {
                    "registration_start": _(
                        "Registration start must be before registration end."
                    ),
                    "registration_end": _(
                        "Registration start must be before registration end."
                    ),
                }
            )

        if self.start_date > self.end_date:
            raise ValidationError(
                {
                    "start_date": _("Start date must be before the end date."),
                    "end_date": _("Start date must be before the end date."),
                }
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
