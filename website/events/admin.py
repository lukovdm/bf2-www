from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.contrib.admin import TabularInline, display, register
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from events.models import Event, EventDate, Registration
from utils.translations import TranslatedModelAdmin


class EventDateInline(TabularInline):
    """The dates of an event, at least one is required"""

    model = EventDate
    min_num = 1
    validate_min = True
    extra = 0
    fields = ("start", "end", "show_end", "label_en", "label_nl", "location")

    def get_formset(self, request, obj=None, **kwargs):
        # The admin ignores validate_min on the inline, pass it to the formset
        kwargs["validate_min"] = True
        return super().get_formset(request, obj, **kwargs)


class RegistrationInline(TabularInline):
    """Inline to display registrations"""

    model = Registration
    extra = 0


@register(Event)
class EventAdmin(FrontendEditableAdminMixin, TranslatedModelAdmin):
    """The admin of events"""

    # Renders the dates above the other fields
    change_form_template = "admin/events/event/change_form.html"
    inlines = [EventDateInline, RegistrationInline]

    list_display = (
        "name",
        "first_start",
        "last_end",
        "date_count",
        "registrations_count",
        "hidden",
    )
    list_filter = ("hidden",)
    search_fields = ("name_en", "name_nl", "location")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .with_dates()
            .annotate(
                date_count=Count("dates", distinct=True),
                registration_count=Count("registration", distinct=True),
            )
        )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("registration_start", timezone.localtime())
        return initial

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # The dates are saved now, so the default registration end can be set
        event = form.instance
        if event.fill_default_registration_end():
            event.save(update_fields=["registration_end"])

    @display(description=_("start"), ordering="first_start")
    def first_start(self, event):
        return event.first_start

    @display(description=_("end"), ordering="last_end")
    def last_end(self, event):
        return event.last_end

    @display(description=_("dates"), ordering="date_count")
    def date_count(self, event):
        return event.date_count

    @display(description=_("registrations"), ordering="registration_count")
    def registrations_count(self, event):
        if event.limit:
            return f"{event.registration_count}/{event.limit}"
        return str(event.registration_count)
