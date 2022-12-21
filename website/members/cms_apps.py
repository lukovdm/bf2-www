from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class MemberApphook(CMSApp):
    app_name = "members"
    name = "Members"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["members.urls"]
