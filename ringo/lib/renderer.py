import logging
import json
from mako.lookup import TemplateLookup
from pyramid.events import BeforeRender
from formbar.renderer import (
    FieldRenderer,
    DropdownFieldRenderer as FormbarDropdown,
    SelectionFieldRenderer as FormbarSelectionField
)
from formbar.config import Config, load
from formbar.form import Form
from ringo.config import template_dir
import ringo.lib.helpers
from ringo.lib.helpers import (
    get_saved_searches,
    get_path_to_overview_config,
    get_path_to_form_config,
)
from ringo.model.base import BaseItem, BaseList
import ringo.lib.security as security

template_lookup = TemplateLookup(directories=[template_dir])

log = logging.getLogger(__name__)


def setup_render_globals(config):
    config.add_subscriber(add_renderer_globals, BeforeRender)


def add_renderer_globals(event):
    request = event['request']
    event['h'] = ringo.lib.helpers
    event['s'] = security
    event['_'] = request.translate
    event['N_'] = request.translate
    event['localizer'] = request.localizer


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


def _load_overview_config(clazz):
        """Return a datastructure representing the overview
        configuration. The configuration is loaded from a JSON
        configuration file under /view/overviews relative to the
        application root. If no configuration can be found return
        None."""
        cfile = "%s.json" % clazz.__tablename__
        # Try to load the configuration for the overview first.
        config = None
        try:
            config = open(get_path_to_overview_config(cfile), "r")
        except IOError:
            try:
                config = open(get_path_to_overview_config(cfile, 'ringo'), "r")
            except IOError:
                log.warning('Can not load overview configuration for "%s" '
                            'Configuring the overview now based on the form '
                            'configuration' % clazz)

        if config:
            return json.load(config)
        return None


def _form2overview(formconfig):
    """Converts a the form configuration of the given clazz into a
    datastructure representing the overview configuration."""
    fields = []
    for key, field in formconfig.get_fields().iteritems():
        fields.append({'name': field.name, 'label': field.label})
    return {'overview': {'columns': fields}}


class TableConfig:
    """The TableConfig clazz provides an interface for configuring the
    overview of the the given clazz. The configuration includes

    * Enabled features of the overview
    * Which fields should be enabled in the overview
    * Labeling of the fields
    * Rendering of the fields
    * Layout of the table (column width etc.)

    The configuration of the overview is loaded from a an JSON
    configuration file which is located under view/overviews relative to
    the application root.

    The configuration has the following form and options::

        {
            "overview": {
                "columns": [
                    {
                        "name": "fieldname",
                        "label": "Label",
                        "width": "width",
                        "screen": "xlarge",
                        "expand": true
                    }
                ]
                "settings": {
                    "default-sort-field": "name"
                    "default-sort-order": "desc"
                    "auto-responsive": true
                }
            }
        }

    The configuration can have configurations for more than one table
    configuration. The default name of a configuration is *overview*.
    The next sections defines the *columns* of the table. The columns
    are rendered in the order they are defined. Each column can have the
    following options:

    * *name*: The name of the attribute within clazz which should be
      listed here.
    * *label*: The label of the field.
    * *width*: The width of the field. If not units are given the pixel
      are assumed.
    * *screen*: Define from which size on this field will be displayed.
      Defaults to "small" which means rendering on all sizes.
      Available media sizes: (xlarge, large, medium, small).
    * *expand*: The expand option is used to expand the referneces
      values in selections into the literal value of the corrispondig
      option. Note that this option is only usefull for selection fields
      in *formbar* which do not have a real relation attached. In all
      other cases the reference values are expanded automatically.


    Further the table has some table wide configuration options:

    * *default-sort-field*: Name of the column which should be used as
      default sorting on the table. Defaults to the first column in the table.
    * *default-sort-order*: Sort order (desc, asc) Defaults to asc.
    * *auto-responsive*: If True than only the first column of a table
      will be displayed on small devices. Else you need to configure the
      "screen" attribute for the fields.
    """

    def __init__(self, clazz, name):
        """Will initialize the configuration of the overview for the
        clazz.

        :clazz: The clazz for which the overview configuration should be
        loaded.
        :name: name of the configuration. Defaults to the
        "overview" configuration.
        """
        self.clazz = clazz
        self.name = name or "overview"
        self.config = _load_overview_config(clazz)

    def get_settings(self):
        """Returns the settings for the table as dictionary
        :returns: Settings dictionary

        """
        config = self.config.get(self.name)
        return config.get('settings', {})

    def is_autoresponsive(self):
        settings = self.get_settings()
        return settings.get("auto-responsive", True)

    def get_columns(self):
        """Return a list of configured columns within the configuration.
        Each colum is a dictionary containing the one or more available
        conifguration attributes."""
        cols = []
        config = self.config.get(self.name)
        for col in config.get('columns'):
            cols.append(col)
        return cols

    def get_default_sort_column(self):
        """Returns the name of the attribute of the clazz which is
        marked as field for default sorting in the *settings* section of
        the configuration. If no default sorting is configured then
        return the name of the attribute in the first column which is
        configured in the table"""
        settings = self.get_settings()
        if settings:
            def_sort = settings.get('default-sort-field')
            if def_sort:
                return def_sort
        return self.get_columns()[0].get('name')

    def get_default_sort_order(self):
        """Returns the ordering of the sort in the table """
        settings = self.get_settings()
        if settings:
            def_order = settings.get('default-sort-order')
            if def_order:
                return def_order
        return "asc"


class Renderer(object):
    """Baseclass for all renderers"""

    def __init__(self):
        """Initialize renderer"""
        pass

    def render(self):
        """Initialize renderer"""
        pass


###########################################################################
#                         Renderers for overviews                         #
###########################################################################

class ListRenderer(Renderer):
    """Docstring for ListRenderer """

    def __init__(self, listing):
        """@todo: to be defined """
        Renderer.__init__(self)
        self.listing = listing
        self.config = self.listing.clazz.get_table_config()
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
                  'saved_searches': get_saved_searches(request,
                                                       self.listing.clazz.__tablename__),
                  'tableconfig': self.config}
        return self.template.render(**values)


class DTListRenderer(Renderer):
    """Docstring for a ListRenderer using the DataTables Jquery Plugin"""
    def __init__(self, listing):
        Renderer.__init__(self)
        self.listing = listing
        self.config = self.listing.clazz.get_table_config()
        self.template = template_lookup.get_template("internal/dtlist.mako")

    def render(self, request):
        """Initialize renderer"""
        values = {'items': self.listing.items,
                  'listing': self.listing,
                  'request': request,
                  '_': request.translate,
                  's': security,
                  'tableconfig': self.config}
        return self.template.render(**values)


class NewsListRenderer(DTListRenderer):
    def __init__(self, listing):
        DTListRenderer.__init__(self, listing)
        self.template = template_lookup.get_template("internal/newslist.mako")


class TodoListRenderer(DTListRenderer):
    def __init__(self, listing):
        DTListRenderer.__init__(self, listing)
        self.template = template_lookup.get_template("internal/todolist.mako")


###########################################################################
#                         Renderers for dialogs                           #
###########################################################################


class DialogRenderer(Renderer):
    """Renderer for Dialogs"""

    def __init__(self, request, item, action, title=None, body=None):
        """Renders a renderered dialog for the requested action on the
        given item. If not header or body is provided the dialog will
        have a default message.

        :request: The current request
        :item: The item for which the item should be confirmed.
        :action: The actions which must be confirmend.
        :header: Custom text for the header of the dialog
        :body: Custom text for the body of the dialog.

        """
        Renderer.__init__(self)

        self._request = request
        self._item = item
        self._action = action
        self._title = title
        self._body = body


class ConfirmDialogRenderer(DialogRenderer):
    """Docstring for ConfirmDialogRenderer """

    def __init__(self, request, clazz, action, title=None, body=None):
        """@todo: to be defined """
        DialogRenderer.__init__(self, request, clazz, action, title, body)
        self.template = template_lookup.get_template("internal/confirm.mako")

    def render(self, items):
        _ = self._request.translate
        mapping = {'Action': self._action.capitalize()}
        values = {}
        values['request'] = self._request
        values['icon'] = self._request.static_url(
            'ringo:static/images/icons/32x32/dialog-warning.png')
        values['header'] = _("Confirm ${Action}", mapping=mapping)
        values['body'] = self._render_body(items)
        values['action'] = self._action.capitalize()
        values['ok_url'] = self._request.current_route_path()
        values['_'] = self._request.translate
        values['cancel_url'] = self._request.referrer
        return self.template.render(**values)

    def _render_body(self, items):
        out = []
        _ = self._request.translate
        item_label = self._item.get_item_modul(self._request).get_label()
        mapping = {'action': self._action, 'item': item_label,
                   'Action': self._action.capitalize()}
        out.append(_("Do you really want to ${action}"
                     " the following ${item} items?",
                     mapping=mapping))
        out.append("<br>")
        out.append("<ol>")
        for item in items:
            out.append("<li>")
            out.append(unicode(item))
            out.append("</li>")
        out.append("</ol>")
        out.append(_('Please press "${Action}" to ${action} the item.'
                     ' Press "Cancel" to cancel the action.',
                     mapping=mapping))

        return "".join(out)


class ErrorDialogRenderer(DialogRenderer):
    """Docstring for ErrorDialogRenderer """

    def __init__(self, request, title, body):
        """@todo: to be defined """
        DialogRenderer.__init__(self, request, None, None, title, body)
        self.template = template_lookup.get_template("internal/error.mako")

    def render(self):
        values = {}
        values['icon'] = self._request.static_url(
            'ringo:static/images/icons/32x32/dialog-error.png')
        values['header'] = self._title
        values['body'] = self._render_body()
        history = self._request.session.get('history')
        if history:
            values['ok_url'] = self._request.session['history'].pop()
        else:
            values['ok_url'] = self._request.route_path('home')
        return self.template.render(**values)

    def _render_body(self):
        out = []
        out.append(self._body)
        return "".join(out)


class ExportDialogRenderer(DialogRenderer):
    """Docstring for ExportDialogRenderer"""

    def __init__(self, request, clazz):
        """@todo: to be defined """
        DialogRenderer.__init__(self, request, clazz, "export")
        self.template = template_lookup.get_template("internal/export.mako")
        config = Config(load(get_path_to_form_config('export.xml', 'ringo')))
        form_config = config.get_form('default')
        self.form = Form(form_config,
                         csrf_token=self._request.session.get_csrf_token())

    def render(self, items):
        values = {}
        values['request'] = self._request
        values['items'] = items
        values['body'] = self._render_body()
        values['modul'] = self._item.get_item_modul(self._request).get_label(plural=True)
        values['action'] = self._action.capitalize()
        values['ok_url'] = self._request.current_route_path()
        values['_'] = self._request.translate
        values['cancel_url'] = self._request.referrer
        return self.template.render(**values)

    def _render_body(self):
        out = []
        out.append(self.form.render(buttons=False))
        return "".join(out)


class ImportDialogRenderer(DialogRenderer):
    """Docstring for ImportDialogRenderer"""

    def __init__(self, request, clazz):
        """@todo: to be defined """
        DialogRenderer.__init__(self, request, clazz, "import")
        self.template = template_lookup.get_template("internal/import.mako")
        config = Config(load(get_path_to_form_config('import.xml', 'ringo')))
        form_config = config.get_form('default')
        self.form = Form(form_config,
                         csrf_token=self._request.session.get_csrf_token())

    def render(self, items):
        values = {}
        values['request'] = self._request
        values['body'] = self._render_body()
        values['modul'] = self._item.get_item_modul(self._request).get_label(plural=True)
        values['action'] = self._action.capitalize()
        values['ok_url'] = self._request.current_route_path()
        values['_'] = self._request.translate
        values['cancel_url'] = self._request.referrer
        values['overview_url'] = self._request.route_path(self._item.get_action_routename('list'))
        values['items'] = items
        return self.template.render(**values)

    def _render_body(self):
        out = []
        out.append(self.form.render(buttons=False))
        return "".join(out)


class PrintDialogRenderer(DialogRenderer):
    """Docstring for ImportDialogRenderer"""

    def __init__(self, request, clazz):
        """@todo: to be defined """
        DialogRenderer.__init__(self, request, clazz, "print")
        self.template = template_lookup.get_template("internal/print.mako")
        config = Config(load(get_path_to_form_config('print.xml', 'ringo')))
        form_config = config.get_form('default')
        self.form = Form(form_config,
                         item=clazz,
                         csrf_token=self._request.session.get_csrf_token(),
                         dbsession=request.db)

    def render(self):
        values = {}
        values['request'] = self._request
        values['body'] = self._render_body()
        values['modul'] = self._item.get_item_modul(self._request).get_label(plural=True)
        values['action'] = self._action.capitalize()
        values['ok_url'] = self._request.current_route_path()
        values['_'] = self._request.translate
        values['cancel_url'] = self._request.referrer
        return self.template.render(**values)

    def _render_body(self):
        out = []
        out.append(self.form.render(buttons=False))
        return "".join(out)


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
            route_name = item.get_action_routename('update')
        elif security.has_permission("read", item, request):
            route_name = item.get_action_routename('read')
        else:
            return None
        return request.route_path(route_name, id=item.id)
    return None


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
                html.append('<a href="%s">%s</a>' % (url, item))
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
        itemlist = clazz.get_item_list(self._field._form._request)
        config = itemlist.clazz.get_table_config(
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
                  'tableconfig': self.itemlist.clazz.get_table_config(config.table)}
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
        item_modul = self._field._form._item.get_item_modul(self._field._form._request).id
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
        html.append(unicode(log.author))
        html.append("</td>")
        html.append("<td>")
        if log.subject:
            html.append('<strong>%s</strong>' % log.subject)
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
                           % (field, logdata[field]["old"], logdata[field]["new"]))
                except:
                    xxx = ("""%s: <i><span class="formbar-new-value">%s</span></i>"""
                           % (field, logdata[field]))
                logentry.append("<li>")
                logentry.append(xxx)
                logentry.append("</li>")
            logentry.append("</ol>")
        except:
            logentry.append(log.text or "")
        html.append("".join(logentry))
        html.append("</td>")
        html.append("</tr>")
        return html

    def render(self):
        html = []
        logs = self._field._form._item.logs
        html.append('<label for="">%s (%s)</label>'
                    % (self._field.label, len(logs)))
        html.append('<table class="table table-densed">')
        html.append('<tr>')
        html.append('<th width="150px">%s</th>' % 'Date')
        html.append('<th width="150px">%s</th>' % 'Author')
        html.append('<th>%s</th>' % 'Log')
        html.append('</tr>')
        for log in logs[::-1]:
            html.append('<input type="checkbox" name="%s" value="%s"'
                        ' style="display:none"/>'
                        % (self._field.name, log.id))
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
        html.append("<bold>" + unicode(comment.owner.profile[0]) + "</bold>")
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
        html.append(comment.text.replace('\n', '<br>') or "")
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
                    % (self._field.label, len(comments)))
        for comment in comments[::-1]:
            html.append('<input type="checkbox" name="%s" value="%s"'
                        ' style="display:none"/>'
                        % (self._field.name, comment.id))
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
