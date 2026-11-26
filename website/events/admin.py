import csv

from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.contrib import messages
from django.contrib.admin import TabularInline, action, display, register
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.text import slugify
from django.db.models import Count
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from events import google_forms
from events.form_sync import connect_form, form_status_text, sync_form
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
    fields = ("user", "date", "has_payed", "form_status", "form_completed_at", "code")
    readonly_fields = ("form_completed_at", "code")


def form_link_help_text():
    """How to add a form, with the address to share it with when configured."""
    text = _(
        'Paste the share link of the form, in Google Forms under "Send" > link icon.'
    )
    email = google_forms.service_account_email()
    if not email:
        return text
    return format_html(
        "{} {}<br><strong>{}</strong>",
        text,
        _(
            'Then share the form as editor with the address below ("..." > '
            '"Add collaborators"), so the website can check who filled it in:'
        ),
        email,
    )


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
    readonly_fields = ("google_form_status",)
    actions = ["export_registrations"]
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

    def get_urls(self):
        return [
            path(
                "<int:pk>/registrations.csv",
                self.admin_site.admin_view(self.registrations_csv_view),
                name="events_event_registrations_csv",
            ),
        ] + super().get_urls()

    def registrations_csv_view(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not self.has_view_permission(request, event):
            raise PermissionDenied
        return registrations_csv([event], f"registrations-{slugify(event.name)}.csv")

    @action(description=_("Export the registrations of the selected events"))
    def export_registrations(self, request, queryset):
        return registrations_csv(queryset, "registrations.csv")

    def get_fields(self, request, obj=None):
        # Show the connection status right below the form link
        fields = [
            f for f in super().get_fields(request, obj) if f != "google_form_status"
        ]
        if "form_link" in fields:
            fields.insert(fields.index("form_link") + 1, "google_form_status")
        else:
            fields.append("google_form_status")
        return fields

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        if "form_link" in form.base_fields:
            form.base_fields["form_link"].help_text = form_link_help_text()
        return form

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("registration_start", timezone.localtime())
        return initial

    @display(description=_("Google Form connection"))
    def google_form_status(self, event):
        return form_status_text(event)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if "form_link" in form.changed_data or (
            obj.form_link and not obj.form_connected
        ):
            connect_form(obj)
            if obj.form_link:
                level = messages.SUCCESS if obj.form_connected else messages.WARNING
                self.message_user(request, form_status_text(obj), level)

    def save_related(self, request, form, formsets, change):
        # Registrations marked as filled in by hand
        for formset in formsets:
            if formset.model is Registration:
                for inline_form in formset.forms:
                    registration = inline_form.instance
                    if "form_status" in inline_form.changed_data:
                        registration.form_completed_at = (
                            timezone.now() if registration.form_status else None
                        )
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


def registrations_csv(events, filename):
    """A csv file with the registrations of the given events."""
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    # Excel needs the byte order mark to read utf-8
    response.write("\ufeff")
    writer = csv.writer(response)
    for event in events:
        sync_form(event, force=True)
    writer.writerow(
        [
            _("event"),
            _("first name"),
            _("last name"),
            _("email"),
            _("phone number"),
            _("registration date"),
            _("has paid"),
            _("form"),
            _("registration code"),
        ]
    )
    registrations = (
        Registration.objects.filter(event__in=events)
        .select_related("event", "user__member")
        .order_by("event__pk", "date")
    )
    for registration in registrations:
        user = registration.user
        member = getattr(user, "member", None)
        if registration.has_payed is None:
            paid = ""
        else:
            paid = _("yes") if registration.has_payed else _("no")
        writer.writerow(
            [
                registration.event.name,
                user.first_name,
                user.last_name,
                user.email,
                member.phone_number if member else "",
                timezone.localtime(registration.date).strftime("%Y-%m-%d %H:%M"),
                paid,
                (
                    registration.get_form_status_display()
                    if registration.event.form_link
                    else ""
                ),
                registration.code,
            ]
        )
    return response
