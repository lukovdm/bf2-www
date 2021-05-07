from menus.base import Modifier
from menus.menu_pool import menu_pool
from cms.models import Page


class HomeModifier(Modifier):
    """
    This modifier makes the is_home attribute of a page
    accessible for the menu system.
    """

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        # only do something when the menu has already been cut
        if post_cut:
            # only consider nodes that refer to cms pages
            # and put them in a dict for efficient access
            page_nodes = {n.id: n for n in nodes if n.attr["is_page"]}
            # retrieve the attributes of interest from the relevant pages
            pages = Page.objects.filter(id__in=page_nodes.keys()).values(
                "id", "is_home"
            )
            # loop over all relevant pages
            for page in pages:
                # take the node referring to the page
                node = page_nodes[page["id"]]
                # put the is_home attribute on the node
                node.attr["is_home"] = page["is_home"]
        return nodes


menu_pool.register_modifier(HomeModifier)
