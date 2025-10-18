from cms.app_base import CMSAppConfig
from events.models import Event
from events.views import event_detail_endpoint_view


class EventConfig(CMSAppConfig):
    cms_enabled = True
    cms_toolbar_enabled_models = [(Event, event_detail_endpoint_view)]
