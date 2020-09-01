from cms.admin.placeholderadmin import PlaceholderAdminMixin
from django.contrib.admin import ModelAdmin, register, StackedInline, TabularInline

from events.models import Event, Registration


class RegistrationInline(TabularInline):
    """Inline to display registrations"""

    model = Registration


@register(Event)
class EventAdmin(PlaceholderAdminMixin, ModelAdmin):
    """The admin off events"""

    inlines = [RegistrationInline]
