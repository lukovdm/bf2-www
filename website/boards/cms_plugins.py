from cms.models import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse

from boards.models import Board, PreviousBoardModel


@plugin_pool.register_plugin
class CurrentBoardPlugin(CMSPluginBase):
    name = "current board"
    model = CMSPlugin
    render_template = "current_board_plugin.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        boards = Board.objects.order_by("-start").all()
        context["boards"] = boards
        return context


@toolbar_pool.register
class BoardToolbar(CMSToolbar):
    supported_apps = ["boards"]

    def populate(self):
        if not (
            self.request.user.is_authenticated
            and self.request.user.has_perm("boards.view_board")
        ):
            return

        menu = self.toolbar.get_or_create_menu(
            "boards_cms_integration-boards", "Boards"
        )

        menu.add_sideframe_item(
            name="Boards list",
            url=admin_reverse("boards_board_changelist"),
        )

        menu.add_sideframe_item(
            name="Add Board",
            url=admin_reverse("boards_board_add"),
        )
