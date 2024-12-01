from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool


@plugin_pool.register_plugin
class OnlyLoggedInPlugin(CMSPluginBase):
    render_template = "ShowLoggedIn.html"
    name = "ShowLoggedIn"
    allow_children = True
    cache = False
