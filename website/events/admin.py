from cms.admin.placeholderadmin import PlaceholderAdminMixin
from django.contrib.admin import ModelAdmin, register, StackedInline, TabularInline

from events.models import Event, Registration
from utils.translations import TranslatedModelAdmin


class RegistrationInline(TabularInline):
    """Inline to display registrations"""

    model = Registration


@register(Event)
class EventAdmin(PlaceholderAdminMixin, TranslatedModelAdmin):
    """The admin off events"""

    inlines = [RegistrationInline]

    list_display = ("name", "start_date", "end_date", "registrations_count", "cost")

    def registrations_count(self, event):
        if event.limit:
            return f"{len(event.registration_set.all())}/{event.limit}"
        return str(len(event.registration_set.all()))
