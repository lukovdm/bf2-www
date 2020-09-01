from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView

from events.models import Event, Registration


class EventListView(ListView):
    """View to render a list of events still to come. The template event_list.html will be used."""

    model = Event

    def get_queryset(self):
        events = super().get_queryset()
        events = events.filter(date__gte=timezone.now()).order_by("date")
        return events


class EventDetailView(DetailView):
    """View to render a details about one event, specified in the url."""

    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["registration"] = Registration.objects.get(
                user=self.request.user, event=context["event"]
            )
        except Registration.DoesNotExist:
            pass

        return context


class EventRegisterView(LoginRequiredMixin, View):
    http_method_names = ["get", "post"]

    def get(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs["pk"])
        return redirect(event)

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs["pk"])

        if (
            event.registration_start
            and event.registration_start > timezone.now()
            or event.registration_end
            and event.registration_end < timezone.now()
        ):
            messages.error(
                request,
                "You can't register outside of the start or end date of this event.",
            )
        elif event.limit and len(event.registration_set.all()) >= event.limit:
            messages.error(request, "Event is already full.")
        elif event.registration_set.all().filter(user=request.user).exists():
            messages.error(request, "You already registered for this event.")
        else:
            Registration.objects.create(
                event=event, user=request.user, has_payed=False if event.cost else None
            )
            messages.success(request, "You successfully registered.")

        return redirect(event)
