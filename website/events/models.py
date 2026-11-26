import secrets

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
    Manager,
    Max,
    Min,
    Q,
    QuerySet,
)
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from filer.fields.image import FilerImageField

from utils.translations import ModelTranslateMeta, MultilingualField


class EventQuerySet(QuerySet):
    def with_dates(self):
        """Annotate the first start, the last end and the next start of the dates.

        The next start is the start of the first date that has not ended yet.
        """
        return self.annotate(
            first_start=Min("dates__start"),
            last_end=Max("dates__end"),
            next_start=Min("dates__start", filter=Q(dates__end__gt=now())),
        )

    def visible(self):
        """Events that are shown on the website."""
        return self.filter(hidden=False)

    def upcoming(self):
        """Events with a date that has not ended yet, sorted by that date."""
        return self.with_dates().filter(last_end__gt=now()).order_by("next_start", "pk")


class Event(Model, metaclass=ModelTranslateMeta):
    """An event with one or more dates and optionally registrations"""

    objects = Manager.from_queryset(EventQuerySet)()

    name = MultilingualField(CharField, max_length=255, verbose_name=_("name"))
    image = FilerImageField(
        verbose_name=_("image"), null=True, blank=True, on_delete=SET_NULL
    )
    location = CharField(max_length=255, verbose_name=_("location"))
    hidden = BooleanField(
        default=False,
        verbose_name=_("hidden"),
        help_text=_(
            "Hidden events are not shown anywhere on the website, only in the admin."
        ),
    )
    description = PlaceholderRelationField()

    limit = IntegerField(null=True, blank=True, verbose_name=_("participant limit"))
    private_registrations = BooleanField(
        default=False, verbose_name=_("Don't show who is registered")
    )
    cost = MultilingualField(
        CharField,
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("cost"),
        help_text=_("Leave empty for a free event."),
    )

    registration_start = DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("registration start"),
        help_text=_(
            "When the registration opens, by default now. Leave the registration "
            "start and end empty for an event without registration."
        ),
    )
    registration_end = DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("registration end"),
        help_text=_(
            "When the registration closes. Leave empty to close the registration "
            "when the event starts."
        ),
    )

    form_link = CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name=_("Google form link"),
        validators=[
            RegexValidator(
                regex=r"https:\/\/docs\.google\.com\/forms\/d\/e\/[\w\d_-]*\/viewform\?",
                message=_("Please enter a google form share link"),
            ),
        ],
    )

    # Filled in by the website when the form is connected, see google_forms.py
    google_form_id = CharField(max_length=128, blank=True, default="", editable=False)
    google_form_question = CharField(
        max_length=64, blank=True, default="", editable=False
    )
    google_form_checked_at = DateTimeField(null=True, blank=True, editable=False)
    google_form_error = CharField(
        max_length=500, blank=True, default="", editable=False
    )

    @property
    def form_connected(self):
        return bool(
            self.form_link and self.google_form_id and self.google_form_question
        )

    def form_link_for(self, registration):
        """The form link for a registration, with its code filled in if possible."""
        from events.google_forms import entry_id, prefilled_link

        if self.form_connected and registration is not None:
            return prefilled_link(
                self.form_link, entry_id(self.google_form_question), registration.code
            )
        return self.form_link

    @cached_property
    def description_placeholder(self):
        return get_placeholder_from_slot(self.description, "description")

    def get_template(self):
        return "events/event_structure.html"

    @property
    def sorted_dates(self):
        # Uses the prefetched dates if available, they are ordered by start
        return list(self.dates.all())

    @property
    def start_date(self):
        """Start of the first date."""
        dates = self.sorted_dates
        return dates[0].start if dates else None

    @property
    def end_date(self):
        """End of the last date."""
        return max((date.end for date in self.sorted_dates), default=None)

    @property
    def next_date(self):
        """The first date that has not ended yet, or the last date if all ended."""
        dates = self.sorted_dates
        current = now()
        return next(
            (date for date in dates if date.end > current), dates[-1] if dates else None
        )

    @property
    def upcoming_date_count(self):
        current = now()
        return sum(1 for date in self.sorted_dates if date.end > current)

    @property
    def has_registrations(self):
        return self.registration_start is not None

    def fill_default_registration_end(self):
        """Close the registration when the event starts, if no end is given."""
        if self.registration_start and not self.registration_end and self.start_date:
            self.registration_end = self.start_date
            return True
        return False

    def clean(self) -> None:
        # Django calls clean() even when individual fields failed validation, in
        # which case those fields are left as None. Every comparison below must
        # therefore guard against missing values, otherwise the admin crashes
        # with a TypeError instead of showing the field errors (see #277).
        errors = {}

        def add_error(fields, message):
            for field in fields:
                errors.setdefault(field, []).append(message)

        if self.registration_end is not None and self.registration_start is None:
            add_error(
                ("registration_start",),
                _("A registration end requires a registration start."),
            )
        elif (
            self.registration_start is not None
            and self.registration_end is not None
            and self.registration_start > self.registration_end
        ):
            add_error(
                ("registration_start", "registration_end"),
                _("Registration start must be before registration end."),
            )

        if self.limit is not None and self.limit < 1:
            add_error(
                ("limit",),
                _(
                    "The participant limit must be at least 1, leave it empty for no limit."
                ),
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pk:
            self.fill_default_registration_end()
        if self.form_link and not self.form_link.endswith("embedded=true"):
            embed_form_link = self.form_link.strip()
            embed_form_link = embed_form_link.removesuffix("usp=sf_link")
            self.form_link = embed_form_link + "embedded=true"

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.name} at {self.start_date}"


class EventDate(Model, metaclass=ModelTranslateMeta):
    """A date (with start and end time) on which an event takes place"""

    event = ForeignKey(Event, CASCADE, related_name="dates", verbose_name=_("event"))
    start = DateTimeField(verbose_name=_("start"))
    end = DateTimeField(verbose_name=_("end"))
    show_end = BooleanField(default=True, verbose_name=_("show end"))
    label = MultilingualField(
        CharField,
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("label"),
        help_text=_("Optional, e.g. 'Day 1' or 'Finals'."),
    )
    location = CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("location"),
        help_text=_("Leave empty to use the location of the event."),
    )

    class Meta:
        ordering = ["start", "pk"]
        verbose_name = _("date")
        verbose_name_plural = _("dates")

    @property
    def location_or_default(self):
        return self.location or self.event.location

    @property
    def has_ended(self):
        return self.end <= now()

    def clean(self):
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValidationError(
                {
                    "start": _("The start must be before the end."),
                    "end": _("The start must be before the end."),
                }
            )

    def __str__(self):
        return f"{self.start:%Y-%m-%d %H:%M} - {self.end:%Y-%m-%d %H:%M}"


def make_registration_code():
    """A short code that is easy to read and type, e.g. K7M2-XQ4P."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    code = "".join(secrets.choice(alphabet) for _ in range(8))
    return f"{code[:4]}-{code[4:]}"


class Registration(Model):
    """Registration of a user to a registrable event"""

    event = ForeignKey(Event, CASCADE, verbose_name=_("event"))
    user = ForeignKey(User, CASCADE, verbose_name=_("user"))

    date = DateTimeField(default=now, verbose_name=_("registration date"))
    has_payed = BooleanField(null=True, blank=True, verbose_name=_("has paid"))

    FORM_NOT_DONE = ""
    FORM_VERIFIED = "verified"
    FORM_SELF_REPORTED = "self_reported"
    FORM_MANUAL = "manual"
    FORM_NOT_FOUND = "not_found"
    FORM_STATUSES = [
        (FORM_NOT_DONE, _("not filled in")),
        (FORM_VERIFIED, _("filled in (checked with Google)")),
        (FORM_SELF_REPORTED, _("filled in (according to the member)")),
        (FORM_MANUAL, _("filled in (marked by an admin)")),
        (
            FORM_NOT_FOUND,
            _("filled in according to the member, but not found at Google"),
        ),
    ]

    code = CharField(
        max_length=12,
        unique=True,
        default=make_registration_code,
        editable=False,
        verbose_name=_("registration code"),
    )
    form_status = CharField(
        max_length=16,
        choices=FORM_STATUSES,
        blank=True,
        default=FORM_NOT_DONE,
        verbose_name=_("form"),
    )
    form_completed_at = DateTimeField(
        null=True, blank=True, verbose_name=_("form filled in at")
    )

    @property
    def form_pending(self):
        """The event has a form and the member did not fill it in yet."""
        return bool(self.event.form_link) and not self.form_status

    @property
    def form_not_found(self):
        """The member says they submitted the form, but Google does not have it."""
        return self.form_status == self.FORM_NOT_FOUND

    def mark_form_completed(self, status):
        self.form_status = status
        self.form_completed_at = now()
        self.save(update_fields=["form_status", "form_completed_at"])
