from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class CommitteeApphook(CMSApp):
    app_name = "committees"
    name = "Committees"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["committees.urls"]
