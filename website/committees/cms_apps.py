from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse


@apphook_pool.register
class CommitteeApphook(CMSApp):
    app_name = "committees"
    name = "Committees"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["committees.urls"]


@toolbar_pool.register
class CommitteeToolbar(CMSToolbar):
    supported_apps = ["committees"]

    def populate(self):
        if not (
            self.request.user.is_authenticated
            and self.request.user.has_perm("committees.view_committee")
        ):
            return

        menu = self.toolbar.get_or_create_menu(
            "committees_cms_integration-committees", "Committees"
        )

        menu.add_sideframe_item(
            name="Committees list",
            url=admin_reverse("committees_committee_changelist"),
        )

        menu.add_sideframe_item(
            name="Add Committees",
            url=admin_reverse("committees_committee_add"),
        )
