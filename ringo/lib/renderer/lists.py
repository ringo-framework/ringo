import logging
import os
import pkg_resources
from mako.lookup import TemplateLookup
import ringo.lib.helpers
from ringo.lib.helpers import (
    get_saved_searches,
    get_item_actions,
    literal,
    get_action_routename
)
from ringo.lib.table import get_table_config
import ringo.lib.security as security

base_dir = pkg_resources.get_distribution("ringo").location
template_dir = os.path.join(base_dir, 'ringo', 'templates')
template_lookup = TemplateLookup(directories=[template_dir],
                                 default_filters=['h'])

log = logging.getLogger(__name__)

###########################################################################
#                         Renderers for overviews                         #
###########################################################################


def get_read_update_url(request, item, clazz, prefilterd=False):
    """Helper method to get the URL to read or update in item in various
    overviews. If the user of this request is not allowed to see the
    item at all, None will be returned as the url."""

    permissions = ['read']
    # If the application is configured to open items in readmode on
    # default then we will not add the update action to the actions to
    # check.
    if not request.registry.settings.get("app.readmode") in ["True", "true"]:
        permissions.append('update')

    is_admin = request.user.has_role("admin")
    url = None
    for permission in permissions:
        if (permission == 'read' and prefilterd) \
           or is_admin \
           or security.has_permission(permission, item, request):
            url = request.route_path(get_action_routename(clazz, permission), id=item.id)
        else:
            break
    return url


class ListRenderer(object):
    """Docstring for ListRenderer """

    def __init__(self, listing, tablename=None):
        """@todo: to be defined """
        self.listing = listing
        self.config = get_table_config(self.listing.clazz, tablename)
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

        bundled_actions = []
        for action in get_item_actions(request, self.listing.clazz):
            if action.bundle and security.has_permission(action.name.lower(),
                                                         request.context,
                                                         request):
                bundled_actions.append(action)

        values = {'items': self.listing.items,
                  'clazz': self.listing.clazz,
                  'listing': self.listing,
                  'request': request,
                  '_': request.translate,
                  'h': ringo.lib.helpers,
                  's': security,
                  'bundled_actions': bundled_actions,
                  'search': search,
                  'regexpr': regexpr,
                  'search_field': search_field,
                  'saved_searches': ssearch,
                  'tableconfig': self.config}
        return literal(self.template.render(**values))


class DTListRenderer(object):
    """Docstring for a ListRenderer using the DataTables Jquery Plugin"""
    def __init__(self, listing, tablename=None):
        self.listing = listing
        self.config = get_table_config(self.listing.clazz, tablename)
        self.template = template_lookup.get_template("internal/dtlist.mako")

        # Template for JS datatable configuration
        self.js_template = template_lookup.get_template("internal/dtlist.js.mako")

    def _get_table_id(self):
        table_id = ["dt",
                    self.config.clazz.__tablename__,
                    self.config.name]
        table_id = "_".join(table_id)
        return table_id

    def _render_js_config(self, request, table_id, bundled_actions):
        values = {'tableconfig': self.config,
                  'table_id': table_id,
                  'request': request,
                  'bundled_actions': bundled_actions,
                  '_': request.translate}
        return self.js_template.render(**values)

    def render(self, request):
        """Initialize renderer"""

        # Get the bundles_actions.
        # If bundle_actions is True, display checkboxes and more in the table.
        bundled_actions = []
        for action in get_item_actions(request, self.listing.clazz):
            if action.bundle and security.has_permission(action.name.lower(),
                                                         request.context,
                                                         request):
                bundled_actions.append(action)
        table_id = self._get_table_id()
        table_config = self._render_js_config(request,
                                              table_id,
                                              bundled_actions)
        values = {'items': self.listing.items,
                  'clazz': self.listing.clazz,
                  'listing': self.listing,
                  'request': request,
                  '_': request.translate,
                  's': security,
                  'h': ringo.lib.helpers,
                  'bundled_actions': bundled_actions,
                  'tableconfig': self.config,
                  'tableid': table_id,
                  'dtconfig': table_config}
        return literal(self.template.render(**values))


class StaticListRenderer(ListRenderer):

    """Docstring for StaticListRendenderer."""

    def __init__(self, listing, tablename=None):
        self.listing = listing
        self.config = get_table_config(self.listing.clazz, tablename)
        self.template = template_lookup.get_template("internal/staticlist.mako")

    def _get_table_id(self):
        table_id = ["static",
                    self.config.clazz.__tablename__,
                    self.config.name]
        table_id = "_".join(table_id)
        return table_id

    def render(self, request):
        """Initialize renderer"""

        table_id = self._get_table_id()
        values = {'items': self.listing.items,
                  'clazz': self.listing.clazz,
                  'listing': self.listing,
                  'request': request,
                  '_': request.translate,
                  's': security,
                  'h': ringo.lib.helpers,
                  'tableconfig': self.config,
                  'tableid': table_id}
        return literal(self.template.render(**values))
