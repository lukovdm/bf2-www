from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class EventApphook(CMSApp):
    app_name = "events"
    name = "Events"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["events.urls"]
