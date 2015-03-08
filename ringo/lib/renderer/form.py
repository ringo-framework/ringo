import logging
import cgi
import os
import pkg_resources
from mako.lookup import TemplateLookup
from formbar.renderer import (
    FieldRenderer,
    DropdownFieldRenderer as FormbarDropdown,
    SelectionFieldRenderer as FormbarSelectionField
)
import ringo.lib.helpers as helpers
from ringo.lib.helpers import get_action_routename
from ringo.model.base import BaseItem, BaseList, get_item_list
from ringo.lib.table import get_table_config
import ringo.lib.security as security

base_dir = pkg_resources.get_distribution("ringo").location
template_dir = os.path.join(base_dir, 'ringo', 'templates')
template_lookup = TemplateLookup(directories=[template_dir])

log = logging.getLogger(__name__)

###########################################################################
#                         Renderers for form elements                     #
###########################################################################

def add_renderers(custom_renderers):
    """Helper function to add ringo ringo specific renderers for form
    rendering."""
    for key in custom_renderers:
        if not key in renderers:
            renderers[key] = custom_renderers[key]
    return renderers


def get_link_url(item, request):
    if isinstance(item, BaseItem):
        if security.has_permission("update", item, request):
            route_name = get_action_routename(item, 'update')
        elif security.has_permission("read", item, request):
            route_name = get_action_routename(item, 'read')
        else:
            return None
        return request.route_path(route_name, id=item.id)
    return None


def filter_options_on_permissions(request, options):
    """Will filter the given options based on the permissions on the
    current user of the request. After filtering the options will only
    have items where the user is allowed to at least read it.

    :request: current request
    :options: list of tuple of options (item, value, filtered)
    :returns: filtered list of option tuples.

    """
    filtered_options = []
    for option in options:
        visible = False
        if (option[2] and (security.has_permission('read', option[0], request)
           or not hasattr(option[0], 'owner'))):
            visible = True
        filtered_options.append((option[0], option[1], visible))
    return filtered_options


class LinkFieldRenderer(FieldRenderer):
    def __init__(self, field, translate):
        """@todo: to be defined"""
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("internal/linkfield.mako")

    def _get_template_values(self):
        values = FieldRenderer._get_template_values(self)
        values['link_text'] = self._field.label
        try:
            item = getattr(self._field._form._item, self._field.name)
        except AttributeError:
            # If the attribute is not part of the item there may be a
            # value in the field based on a expression. So set the item
            # to the value of the field. If this is not an instance of
            # BaseItem the link can not be generated.
            item = self._field.value
            if not item:
                name = self._field.name
                item = self._field._form._item
                log.warning("Missing value for %s in %s" % (name, item))
        values['url'] = get_link_url(item, self._field._form._request) or "#"
        return values

    def _render_label(self):
        return ""


class DropdownFieldRenderer(FormbarDropdown):
    """Ringo specific DropdownFieldRenderer. This renderer add a small
    link next to the label to make it possible to jump to the selected
    item in the dropdown list.

    * nolink: Flag "true" or "false" to configure completly disable
      linking Default to "false".

    """

    def __init__(self, field, translate):
        """@todo: to be defined"""
        FormbarDropdown.__init__(self, field, translate)
        self.template = template_lookup.get_template("internal/dropdown.mako")

    def _get_template_values(self):
        values = FormbarDropdown._get_template_values(self)
        values['options'] = filter_options_on_permissions(
            self._field._form._request,
            values['options'])
        return values

    def render_link(self):
        html = []
        items = []
        try:
            item = getattr(self._field._form._item, self._field.name)
        except AttributeError:
            log.warning("Missing %s attribute in %s"
                        % (self._field.name, self._field._form._item))
            return "".join(html)

        if not isinstance(item, list):
            items.append(item)
        else:
            items = item
        for item in items:
            url = get_link_url(item, self._field._form._request)
            if url:
                html.append('<a href="%s">%s</a>'
                            % (url, cgi.escape(unicode(item))))
        return "".join(html)

    def _render_label(self):
        html = []
        html.append(FormbarDropdown._render_label(self))
        if not self._field.is_readonly() and not self.nolink == "true":
            link = self.render_link()
            if link:
                html.append(" [%s]" % link)
        return "".join(html)


class StateFieldRenderer(FormbarDropdown):
    """Ringo specific DropdownFieldRenderer to change the current state
    of an item.  This renderer will render a combined widget containing
    a textfield showing the current state of the item and a dropdown
    with available actions which can be done from this state.

    You can configure the layout of the statefield by setting the layout
    option. On default the renderer shows the current state with
    description and the resulting state and description when choosing a
    transtion. Setting the option to simple will render a simple
    dropdown with the current state as part of the fields label and the
    available transitions as options of the dropdown

    * layout: Option to change the layout of the statefield.

    """

    def __init__(self, field, translate):
        """@todo: to be defined"""
        FormbarDropdown.__init__(self, field, translate)
        self.template = template_lookup.get_template("internal/"
                                                     "statefield.mako")

    def _render_label(self):
        return ""

    def render(self):
        """Initialize renderer"""
        html = []
        # Get all available transitions from the current state for this
        # item and request.
        item = self._field._form._item
        sm = item.get_statemachine(self._field.name,
                                   request=self._field._form._request)
        state = sm.get_state()
        has_errors = len(self._field.get_errors())
        has_warnings = len(self._field.get_warnings())

        html.append('<div class="form-group %s %s">' % ((has_errors and 'has-error'), (has_warnings and 'has-warning')))
        html.append(self._render_label())
        values = {'field': self._field,
                  'request': self._field._form._request,
                  'state': state,
                  '_': self._field._form._translate}
        html.append(self.template.render(**values))
        html.append('</div>')
        return "".join(html)


class ListingFieldRenderer(FormbarSelectionField):
    """Renderer to render a listing of linked items. Used attributes:

    * form: Name of the form which is used to add new items
    * table: Name of the table configuration which is used to list items
    * hideadd: Flag "true" or "false" to configure hiding the add button.
    * nolinks: Flag "true" or "false" to configure completly disable
      linking.
    * showsearch: Flag "true" or "false" to configure rendering a search
      field.
    * showall: "true" or "false". If true all items (linked and
      unlinked) regardless if the current user is allowed to read
      or update the item will be listed. However clicking on items the
      user has no permission to read will have no effect as no links are
      rendered for those items. Defaults to false.
    * onlylinked: "true" or "false". If true only linked items will be
      rendered. Checkboxes will be hidden.
    * multiple: "true" or "false". If false only one option can be
      selected. Defaults to true. Note that this restriction is only
      implemented on client side.
    * openmodal: "true" or "false". If true the item will be opened in a
      modal popup.
    * backlink: "true" or "false". If true the user will be redirected
      back to the listing after creating a new item. Defaults to true.
    """

    def __init__(self, field, translate):
        FormbarSelectionField.__init__(self, field, translate)
        self.itemlist = self._get_all_items()
        self.template = template_lookup.get_template("internal/listfield.mako")

    def get_class(self):
        try:
            clazz = self._field._get_sa_mapped_class()
            return clazz
        except AttributeError:
            # Special logic if the fields item is not an SQLAlchemy
            # attribute but a python property (used to add futher
            # informations to the fields item model). In this case getting
            # the clazz from the SA attributes mapper -> clazz will
            # fail.
            clazz = getattr(self._field._form._item, self._field.name)
            if isinstance(clazz, BaseList):
                return clazz.clazz
            return clazz

    def _get_all_items(self):
        clazz = self.get_class()
        itemlist = get_item_list(self._field._form._request, clazz)
        config = get_table_config(itemlist.clazz,
                                  self._field._config.renderer.table)
        sort_field = config.get_default_sort_column()
        sort_order = config.get_default_sort_order()
        itemlist.sort(sort_field, sort_order)
        return itemlist

    def _get_selected_items(self, items):
        try:
            selected = getattr(self._field._form._item, self._field.name) or []
            # Usually the getattr function should return a single item
            # or a list of items. But in some cases the attribute can be
            # a BaseList. This can happen if the attribute is a python
            # property of the item to dynamically add some attributes.
            # This property might return a BaseList.
            if isinstance(selected, BaseList):
                selected = selected.items
            elif not isinstance(selected, list):
                selected = [selected]
            return selected
        except AttributeError:
            # Can happen when designing forms an the model of the item
            # is not yet configured.
            log.warning("Missing %s attribute in %s"
                        % (self._field.name, repr(self._field._form._item)))
        return []

    def render(self):
        """Initialize renderer"""
        html = []
        config = self._field._config.renderer
        has_errors = len(self._field.get_errors())
        has_warnings = len(self._field.get_warnings())
        html.append('<div class="form-group %s %s">' % ((has_errors and 'has-error'), (has_warnings and 'has-warning')))
        html.append(self._render_label())
        if self._field.is_readonly() or self.onlylinked == "true":
            items = self._get_selected_items(self.itemlist.items)
        else:
            items = self.itemlist.items

        # Get filtered options and only use the items which are
        # in the origin items list and has passed filtering.
        items = self._field.filter_options(items)
        # Now filter the items based on the user permissions
        items = filter_options_on_permissions(self._field._form._request,
                                              items)

        values = {'items': items,
                  'field': self._field,
                  'clazz': self.get_class(),
                  'pclazz': self._field._form._item.__class__,
                  'request': self._field._form._request,
                  '_': self._field._form._translate,
                  's': security,
                  'h': helpers,
                  'tableconfig': get_table_config(self.itemlist.clazz,
                                                  config.table)}
        html.append(self.template.render(**values))
        html.append(self._render_errors())
        html.append(self._render_help())
        html.append('</div>')
        return "".join(html)

renderers = {
    "dropdown": DropdownFieldRenderer,
    "listing": ListingFieldRenderer,
    "state": StateFieldRenderer,
    "link": LinkFieldRenderer
}
