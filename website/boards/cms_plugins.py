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
        board = Board.objects.order_by("-start").first()
        context["year"] = board.start.year
        context["board_members"] = board.boardmembership_set.all()
        context["picture"] = board.picture
        return context


@plugin_pool.register_plugin
class PreviousBoardPlugin(CMSPluginBase):
    name = "previous board"
    model = PreviousBoardModel
    render_template = "previous_board_plugin.html"

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        board = instance.board
        context["year"] = board.start.year
        context["picture"] = board.picture
        context["board_members"] = board.boardmembership_set.all()
        return context
