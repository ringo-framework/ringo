import logging
import os
import pkg_resources
from mako.lookup import TemplateLookup
import ringo.lib.helpers
from ringo.lib.helpers import (
    get_saved_searches,
)
from ringo.lib.table import get_table_config
import ringo.lib.security as security

base_dir = pkg_resources.get_distribution("ringo").location
template_dir = os.path.join(base_dir, 'ringo', 'templates')
template_lookup = TemplateLookup(directories=[template_dir])

log = logging.getLogger(__name__)

###########################################################################
#                         Renderers for overviews                         #
###########################################################################


class ListRenderer(object):
    """Docstring for ListRenderer """

    def __init__(self, listing):
        """@todo: to be defined """
        self.listing = listing
        self.config = get_table_config(self.listing.clazz)
        self.template = template_lookup.get_template("internal/list.mako")

    def render(self, request):
        """Initialize renderer"""
        # TODO: Enabled sorting of lists. Mind that these lists might be
        # presorted if the user clicked on the header. In this case some
        # get params with sort configurations are in the session. This
        # logic is currently in base/view. (ti) <2014-01-23 23:15>
        # sort_field = self.config.get_default_sort_column()
        # sort_order = self.config.get_default_sort_order()
        # self.listing.sort(sort_field, sort_order)

        if len(self.listing.search_filter) > 0:
            search = self.listing.search_filter[-1][0]
            search_field = self.listing.search_filter[-1][1]
            regexpr = self.listing.search_filter[-1][2]
        else:
            search = ""
            search_field = ""
            regexpr = False
        ssearch = get_saved_searches(request,
                                     self.listing.clazz.__tablename__)
        values = {'items': self.listing.items,
                  'clazz': self.listing.clazz,
                  'listing': self.listing,
                  'request': request,
                  '_': request.translate,
                  'h': ringo.lib.helpers,
                  's': security,
                  'enable_bundled_actions': True,
                  'search': search,
                  'regexpr': regexpr,
                  'search_field': search_field,
                  'saved_searches': ssearch,
                  'tableconfig': self.config}
        return self.template.render(**values)


class DTListRenderer(object):
    """Docstring for a ListRenderer using the DataTables Jquery Plugin"""
    def __init__(self, listing, tablename=None):
        self.listing = listing
        self.config = get_table_config(self.listing.clazz, tablename)
        self.template = template_lookup.get_template("internal/dtlist.mako")

    def render(self, request):
        """Initialize renderer"""
        values = {'items': self.listing.items,
                  'listing': self.listing,
                  'request': request,
                  '_': request.translate,
                  's': security,
                  'h': ringo.lib.helpers,
                  'tableconfig': self.config}
        return self.template.render(**values)
