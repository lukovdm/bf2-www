import ics
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from ics import Calendar, Organizer

from events.form_sync import sync_form
from events.models import Event, EventDate, Registration


def events_for(user):
    """The events a user may see on the website.

    Hidden events are only shown to people with access to events in the admin.
    """
    events = Event.objects.all()
    if not user.has_perm("events.view_event"):
        events = events.visible()
    return events


class EventListView(ListView):
    """View to render a list of events still to come. The template event_list.html will be used."""

    model = Event
    template_name = "events/event_list.html"

    def get_queryset(self):
        events = list(
            events_for(self.request.user)
            .upcoming()
            .annotate(registration_count=Count("registration", distinct=True))
            .prefetch_related("dates")
        )

        if self.request.user.is_authenticated:
            registrations = {
                registration.event_id: registration
                for registration in Registration.objects.filter(
                    user=self.request.user, event__in=events
                )
            }
            for event in events:
                event.registration = registrations.get(event.pk)
                if event.registration and event.registration.form_pending:
                    sync_form(event)
                    event.registration.refresh_from_db()

        return events


class EventDetailView(DetailView):
    """View to render a details about one event, specified in the url."""

    model = Event

    def get_queryset(self):
        return events_for(self.request.user).prefetch_related("dates")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request, "toolbar"):
            self.request.toolbar.set_object(self.object)

        context["now"] = timezone.now()
        context["dates"] = self.object.sorted_dates

        if self.request.user.is_authenticated:
            registration = Registration.objects.filter(
                user=self.request.user, event=self.object
            ).first()
            if registration and registration.form_pending:
                sync_form(self.object)
                registration.refresh_from_db()
            context["registration"] = registration

        return context


def event_detail_endpoint_view(request, event):
    return EventDetailView.as_view()(request, pk=event.pk)


class EventRegisterView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(events_for(request.user), pk=kwargs["pk"])
        now = timezone.now()

        if event.registration_start is None or event.registration_end is None:
            messages.error(request, _("This event does not have registrations."))
        elif event.registration_start > now:
            messages.error(
                request,
                _("The registrations for this event have not opened yet."),
            )
        elif event.registration_end < now:
            messages.error(
                request,
                _("The registrations for this event have already closed."),
            )
        elif event.registration_set.filter(user=request.user).exists():
            messages.error(request, _("You have already registered for this event."))
        elif event.limit and event.registration_set.count() >= event.limit:
            messages.error(request, _("This event is already full."))
        else:
            Registration.objects.create(
                event=event, user=request.user, has_payed=False if event.cost else None
            )
            if event.form_link:
                # The form page explains that the registration is not complete
                return redirect("events:form", pk=event.pk)
            messages.success(request, _("You successfully registered."))

        return redirect(event)


class EventFormView(LoginRequiredMixin, TemplateView):
    """The form of an event, embedded in the website."""

    template_name = "events/event_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.event = get_object_or_404(events_for(request.user), pk=kwargs["pk"])
        if not self.event.form_link:
            raise Http404("Event has no form")
        self.registration = Registration.objects.filter(
            event=self.event, user=request.user
        ).first()
        if self.registration is None:
            messages.error(
                request, _("Register for the event before filling in the form.")
            )
            return redirect(self.event)
        # Connects the form if needed, so the registration code can be prefilled
        sync_form(self.event)
        self.registration.refresh_from_db()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.event
        context["registration"] = self.registration
        context["form_url"] = self.event.form_link_for(self.registration)
        context["next"] = self.event.get_absolute_url()
        return context


class EventFormDoneView(LoginRequiredMixin, View):
    """The member says they submitted the form.

    For connected forms the website checks this with Google, otherwise the
    member is trusted.
    """

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(events_for(request.user), pk=kwargs["pk"])
        registration = get_object_or_404(Registration, event=event, user=request.user)

        if not registration.form_pending:
            return redirect(event)

        if event.form_connected:
            sync_form(event, force=True)
            registration.refresh_from_db()
            if registration.form_pending:
                messages.error(
                    request,
                    _(
                        "We have not received your form yet. Fill in all questions "
                        "and press the submit button at the end of the form, then try "
                        "again. If it still does not work, contact the committee."
                    ),
                )
                return redirect("events:form", pk=event.pk)
        else:
            registration.mark_form_completed(Registration.FORM_SELF_REPORTED)

        messages.success(request, _("Thank you, your registration is complete."))
        return redirect(event)


class EventUnregisterView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(events_for(request.user), pk=kwargs["pk"])
        registration = Registration.objects.filter(
            event=event, user=request.user
        ).first()

        if registration is None:
            messages.error(request, _("You are not registered for this event."))
        elif event.registration_end and event.registration_end < timezone.now():
            messages.error(
                request,
                _(
                    "The registrations for this event have already closed, "
                    "if you still want to deregister contact the committee."
                ),
            )
        else:
            registration.delete()
            messages.success(request, _("You successfully unregistered."))

        return redirect(event)


class EventICSView(View):
    """Calendar feed with one calendar event per upcoming date."""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        dates = (
            EventDate.objects.filter(event__hidden=False, end__gt=timezone.now())
            .select_related("event")
            .order_by("start")
        )

        c = Calendar(creator="BFrisBee2's")
        for date in dates:
            event = date.event
            url = request.build_absolute_uri(event.get_absolute_url())
            name = f"{event.name} ({date.label})" if date.label else event.name
            c.events.add(
                ics.Event(
                    uid=f"event-{event.pk}-date-{date.pk}@bfrisbee2s.nl",
                    name=name,
                    begin=date.start,
                    end=date.end,
                    location=date.location_or_default,
                    url=url,
                    organizer=Organizer(
                        email="info@bfrisbee2s.nl", common_name="BFrisBee2's"
                    ),
                    description=_("For more details, see the website: ") + url,
                )
            )

        return HttpResponse(c.serialize(), content_type="text/calendar")
