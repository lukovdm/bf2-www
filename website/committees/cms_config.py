from cms.app_base import CMSAppConfig

from committees.models import Committee
from committees.views import committee_detail_endpoint_view


class CommitteeConfig(CMSAppConfig):
    cms_enabled = True
    cms_toolbar_enabled_models = [(Committee, committee_detail_endpoint_view)]
