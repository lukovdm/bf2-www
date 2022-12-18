from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse


@apphook_pool.register
class EventApphook(CMSApp):
    app_name = "events"
    name = "Events"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["events.urls"]


@toolbar_pool.register
class EventToolbar(CMSToolbar):
    supported_apps = ["events"]

    def populate(self):
        if not (
            self.request.user.is_authenticated
            and self.request.user.has_perm("events.view_event")
        ):
            return

        menu = self.toolbar.get_or_create_menu(
            "events_cms_integration-events", "Events"
        )

        menu.add_sideframe_item(
            name="Event list",
            url=admin_reverse("events_event_changelist"),
        )

        menu.add_sideframe_item(
            name="Add Event",
            url=admin_reverse("events_event_add"),
        )
