from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import gettext_lazy as _
from djangocms_file.cms_plugins import FilePlugin


@plugin_pool.register_plugin
class OnlyLoggedInPlugin(CMSPluginBase):
    render_template = "ShowLoggedIn.html"
    name = "ShowLoggedIn"
    allow_children = True
    cache = False

@plugin_pool.register_plugin
class BetterFilePlugin(FilePlugin):
    name = _("Better File")
    allow_children = True

    def get_render_template(self, context, instance, placeholder):
        return "djangocms_file_better/{}/file.html".format(instance.template)
