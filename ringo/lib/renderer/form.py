import logging
import cgi
import json
import os
import pkg_resources
from mako.lookup import TemplateLookup
from formbar.renderer import (
    FieldRenderer,
    DropdownFieldRenderer as FormbarDropdown,
    SelectionFieldRenderer as FormbarSelectionField
)
import ringo.lib.helpers as helpers
from ringo.lib.helpers import (
    get_action_routename,
    get_item_modul
)
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


def add_renderers(renderers):
    """Helper function to add ringo ringo specific renderers for form
    rendering."""
    if not "dropdown" in renderers:
        renderers["dropdown"] = DropdownFieldRenderer
    if not "listing" in renderers:
        renderers["listing"] = ListingFieldRenderer
    if not "logbook" in renderers:
        renderers["logbook"] = LogRenderer
    if not "state" in renderers:
        renderers["state"] = StateFieldRenderer
    if not "comments" in renderers:
        renderers["comments"] = CommentRenderer
    if not "link" in renderers:
        renderers["link"] = LinkFieldRenderer
    if not "tags" in renderers:
        renderers["tags"] = TagFieldRenderer
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
            log.warning("Missing %s attribute in %s" % (self._field.name,
                                                        self._field._form._item))
            return "".join(html)

        if not isinstance(item, list):
            items.append(item)
        else:
            items = item
        for item in items:
            url = get_link_url(item, self._field._form._request)
            if url:
                html.append('<a href="%s">%s</a>' % (url, cgi.escape(unicode(item))))
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
        self.template = template_lookup.get_template("internal/statefield.mako")

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

        html.append(self._render_label())
        values = {'field': self._field,
                  'request': self._field._form._request,
                  'state': state,
                  '_': self._field._form._translate}
        html.append(self.template.render(**values))
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
    * onlylinked: "true" or "false". If true only linked items will be
      rendered
    * multiple: "true" or "false". If false only one option can be
      selected. Defaults to true. Note that this restriction is only
      implemented on client side.
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
            log.warning("Missing %s attribute in %s" % (self._field.name,
                                                        repr(self._field._form._item)))
        return []

    def render(self):
        """Initialize renderer"""
        html = []
        config = self._field._config.renderer
        html.append(self._render_label())
        if self._field.is_readonly() or self.onlylinked == "true":
            items = self._get_selected_items(self.itemlist.items)
        else:
            items = self.itemlist.items

        # Get filtered options and only use the items which are
        # in the origin items list and has passed filtering.
        items = self._field.filter_options(items)
        # Now filter the items based on the user permissions
        items = filter_options_on_permissions(self._field._form._request, items)

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
        return "".join(html)


class TagFieldRenderer(ListingFieldRenderer):
    """Renderer to render tags  listings. The renderer will only show
    tags which are either associated to no module or the the items
    module."""

    def __init__(self, field, translate):
        ListingFieldRenderer.__init__(self, field, translate)

    def _get_all_items(self):
        tags = []
        alltags = ListingFieldRenderer._get_all_items(self)
        item_modul = get_item_modul(self._field._form._request,
                                    self._field._form._item).id
        for tag in alltags:
            if not tag.modul or (tag.modul.id == item_modul):
                tags.append(tag)
        alltags.items = tags
        return alltags


class LogRenderer(FieldRenderer):
    """Custom Renderer for the logbook listing"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)

    def _render_body(self, log):
        html = []
        html.append("<tr>")
        html.append("<td>")
        html.append(log.created.strftime("%y.%m.%d %H:%M"))
        html.append("</td>")
        html.append("<td>")
        html.append(cgi.escape(unicode(log.author)))
        html.append("</td>")
        html.append("<td>")
        if log.subject:
            html.append('<strong>%s</strong>' % cgi.escape(log.subject))
            html.append('<br>')
        logentry = []
        try:
            logdata = json.loads(log.text)
            logentry.append("<ol>")
            for field in logdata:
                try:
                    xxx = ("""%s:
                           <i><span class="formbar-del-value">%s</span>
                           <span class="formbar-new-value">%s</span></i>"""
                           % (cgi.escape(field),
                              cgi.escape(logdata[field]["old"]),
                              cgi.escape(logdata[field]["new"])))
                except:
                    xxx = ("""%s: <i><span class="formbar-new-value">%s</span></i>"""
                           % (field, logdata[field]))
                logentry.append("<li>")
                logentry.append(xxx)
                logentry.append("</li>")
            logentry.append("</ol>")
        except:
            logentry.append(cgi.escape(log.text or ""))
        html.append("".join(logentry))
        html.append("</td>")
        html.append("</tr>")
        return html

    def render(self):
        html = []
        logs = self._field._form._item.logs
        html.append('<label for="">%s (%s)</label>'
                    % (cgi.escape(self._field.label), len(logs)))
        html.append('<table class="table table-densed">')
        html.append('<tr>')
        html.append('<th width="150px">%s</th>' % 'Date')
        html.append('<th width="150px">%s</th>' % 'Author')
        html.append('<th>%s</th>' % 'Log')
        html.append('</tr>')
        for log in logs[::-1]:
            html.append('<input type="checkbox" name="%s" value="%s"'
                        ' style="display:none"/>'
                        % (cgi.escape(self._field.name), log.id))
            html.extend(self._render_body(log))
        html.append('</table>')
        return "".join(html)


class CommentRenderer(FieldRenderer):
    """Custom Renderer for the comment listing"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)

    def _render_info(self, comment):
        html = []
        html.append("<small>")
        html.append('<a href="/comments/read/%s">#%s</a>'
                    % (comment.id, comment.id))
        html.append(" | ")
        html.append("<bold>" + cgi.escape(unicode(comment.owner.profile[0])) + "</bold>")
        html.append(" | ")
        str_updated = comment.updated.strftime("%y.%m.%d %H:%M")
        str_created = comment.created.strftime("%y.%m.%d %H:%M")
        html.append(str_created)
        if str_updated != str_created:
            html.append(" | (")
            html.append(str_updated)
            html.append(")</small>")
        return html

    def _render_body(self, comment):
        html = []
        html.append(cgi.escape(comment.text.replace('\n', '<br>') or ""))
        return html

    def render(self):
        _ = self.translate
        html = []
        comments = []
        for comment in self._field._form._item.comments:
            if security.has_permission('read',
                                       comment,
                                       self._field._form._request):
                comments.append(comment)
        if not self._field.is_readonly():
            html.append('<label for="new-comment" class="control-label">')
            html.append(_('New entry'))
            html.append('</label>')
            html.append('<textarea class="form-control" id="new-comment" name="comment"></textarea>')
            html.append('</br>')
        html.append('<label for="">%s (%s)</label>'
                    % (cgi.escape(self._field.label), len(comments)))
        for comment in comments[::-1]:
            html.append('<input type="checkbox" name="%s" value="%s"'
                        ' style="display:none"/>'
                        % (cgi.escape(self._field.name), comment.id))
            html.append('<div class="readonlyfield">')
            html.append("<table>")
            html.append("<tr >")
            html.append("<td>")
            html.extend(self._render_body(comment))
            html.append("</td>")
            html.append("<tr>")
            html.append('<td>')
            html.extend(self._render_info(comment))
            html.append("</td>")
            html.append("</tr>")
            html.append("</table>")
            html.append("</div>")
        return "".join(html)
