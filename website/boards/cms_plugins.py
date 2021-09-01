from cms.models import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

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
