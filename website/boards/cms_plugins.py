from cms.models import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from boards.models import Board


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
        context["members"] = board.members.through.objects.all()
        context["picture"] = board.picture
        return context
