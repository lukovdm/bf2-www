from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from djangocms_file.cms_plugins import FilePlugin


@plugin_pool.register_plugin
class BetterFilePlugin(FilePlugin):
    name = _("Better File")
    allow_children = True

    def get_render_template(self, context, instance, placeholder):
        return "djangocms_file_better/{}/file.html".format(instance.template)
