import logging
import json
from mako.lookup import TemplateLookup
from ringo import template_dir
from ringo.lib.helpers import (
    get_saved_searches,
    get_path_to_overview_config,
)

template_lookup = TemplateLookup(directories=[template_dir],
                                 module_directory='/tmp/ringo_modules')

log = logging.getLogger(__name__)


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
    return {'fields': fields}


class OverviewConfig:
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
                        "width": "width"
                    }
                ]
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
    * *width": The width of the field. If not units are given the pixel
      are assumed.

    If no configuration file can be found, then add all fields
    configured in the form configuration to the overview.
    """

    def __init__(self, clazz):
        """Will initialize the configuration of the overview for the
        clazz."""
        self.clazz = clazz
        config = _load_overview_config(clazz)
        if config:
            self.config = config
        else:
            form_config = clazz.get_form_config('create')
            self.config = _form2overview(form_config)

    def get_fields(self):
        fields = []
        for field in self.config.get('fields'):
            fields.append((field.get('name'), field.get('label')))
        return fields


class Renderer(object):
    """Baseclass for all renderers"""

    def __init__(self):
        """Initialize renderer"""
        pass

    def render(self):
        """Initialize renderer"""
        pass


class ListRenderer(Renderer):
    """Docstring for ListRenderer """

    def __init__(self, listing):
        """@todo: to be defined """
        Renderer.__init__(self)
        self.listing = listing
        self.template = template_lookup.get_template("internal/list.mako")

    def render(self, request):
        """Initialize renderer"""
        if len(self.listing.search_filter) > 0:
            search = self.listing.search_filter[-1][0]
            search_field = self.listing.search_filter[-1][1]
        else:
            search = ""
            search_field = ""
        values = {'items': self.listing.items,
                  'clazz': self.listing.clazz,
                  'listing': self.listing,
                  'request': request,
                  'enable_bundled_actions': False,
                  'search': search,
                  'search_field': search_field,
                  'saved_searches': get_saved_searches(request, self.listing.clazz.__tablename__),
                  'headers': self.listing.clazz.get_table_config()}
        return self.template.render(**values)


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

    def __init__(self, request, item, action, title=None, body=None):
        """@todo: to be defined """
        DialogRenderer.__init__(self, request, item, action, title, body)
        self.template = template_lookup.get_template("internal/confirm.mako")

    def render(self):
        values = {}
        values['icon'] = self._request.static_url(
            'ringo:static/images/icons/32x32/dialog-warning.png')
        values['header'] = "Confirm %s" % self._action
        values['body'] = self._render_body()
        values['action'] = self._action.capitalize()
        values['ok_url'] = self._request.current_route_url()
        values['cancel_url'] = self._request.referrer
        return self.template.render(**values)

    def _render_body(self):
        out = []
        item_label = self._item.get_item_modul().get_label()
        out.append("Do you really want to %s"
                   " the following %s items?" % (self._action, item_label))
        out.append("<br>")
        out.append("<ol>")
        if isinstance(self._item, list):
            items = self._item
        else:
            items = [self._item]
        for item in items:
            out.append("<li>")
            out.append(unicode(item))
            out.append("</li>")
        out.append("</ol>")
        out.append('Please press "%s" to %s the item.'
                   ' Press "Cancel" to cancel the action.'
                   % (self._action.capitalize(), self._action))

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
            values['ok_url'] = self._request.route_url('home')
        return self.template.render(**values)

    def _render_body(self):
        out = []
        out.append(self._body)
        return "".join(out)
