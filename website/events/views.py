import ics
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from ics import Calendar, Organizer

from events.models import Event, Registration


class EventListView(ListView):
    """View to render a list of events still to come. The template event_list.html will be used."""

    model = Event

    def get_queryset(self):
        events = super().get_queryset()
        events = events.filter(end_date__gt=timezone.now()).order_by("start_date")

        if self.request.user.is_authenticated:
            for event in events:
                try:
                    event.registration = Registration.objects.get(
                        user=self.request.user, event=event
                    )
                except Registration.DoesNotExist:
                    pass

        return events


class EventDetailView(DetailView):
    """View to render a details about one event, specified in the url."""

    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["now"] = timezone.now()

        if self.request.user.is_authenticated:
            try:
                context["registration"] = Registration.objects.get(
                    user=self.request.user, event=context["event"]
                )
            except Registration.DoesNotExist:
                pass

        return context


class EventRegisterView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs["pk"])

        if event.registration_start and event.registration_start > timezone.now():
            messages.error(
                request,
                _("The registrations for this event have not opened yet."),
            )
        elif event.registration_end and event.registration_end < timezone.now():
            messages.error(
                request,
                _("The registrations for this event have already closed."),
            )
        elif event.end_date < timezone.now():
            messages.error(
                request,
                _("This event has already passed."),
            )
        elif event.limit and len(event.registration_set.all()) >= event.limit:
            messages.error(request, _("This event is already full."))
        elif event.registration_set.all().filter(user=request.user).exists():
            messages.error(request, _("You have already registered for this event."))
        else:
            Registration.objects.create(
                event=event, user=request.user, has_payed=False if event.cost else None
            )
            messages.success(request, _("You successfully registered."))

            if event.form_link is not None:
                return redirect("events:form", pk=event.pk)

        return redirect(event)


class EventFormView(LoginRequiredMixin, TemplateView):
    template_name = "events/event_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=kwargs["pk"])
        if not event.form_link:
            raise Http404("Event has no form")

        context["event"] = event
        context["next"] = event.get_absolute_url()
        return context


class EventUnregisterView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs["pk"])
        registration = get_object_or_404(Registration, event=event, user=request.user)

        if event.registration_end and event.registration_end < timezone.now():
            messages.error(
                request,
                _(
                    "The registrations for this event have already closed, "
                    "if you still want to deregister contact the committee."
                ),
            )

        registration.delete()
        messages.success(request, _("You successfully unregistered."))

        return redirect(event)


class EventICSView(View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        events = (
            Event.objects.filter(end_date__gt=timezone.now())
            .order_by("start_date")
            .all()
        )

        c = Calendar(creator="BFrisBee2's")
        for event in events:
            e = ics.Event(
                name=event.name,
                begin=event.start_date,
                end=event.end_date,
                url=request.build_absolute_uri(event.get_absolute_url()),
                organizer=Organizer(
                    email="info@bfrisbee2s.nl", common_name="BFrisBee2's"
                ),
                description=_("For more details, see the website: ")
                + request.build_absolute_uri(event.get_absolute_url()),
            )
            c.events.add(e)

        return HttpResponse(c.serialize(), content_type="text/calendar")
