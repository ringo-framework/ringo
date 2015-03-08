import logging
import os
import cgi
import pkg_resources
from mako.lookup import TemplateLookup

from formbar.config import Config, load
from formbar.form import Form

import ringo.lib.helpers
from ringo.lib.helpers import (
    get_action_routename,
    get_item_modul
)
from ringo.lib.form import (
    eval_url,
    get_path_to_form_config,
)

base_dir = pkg_resources.get_distribution("ringo").location
template_dir = os.path.join(base_dir, 'ringo', 'templates')
template_lookup = TemplateLookup(directories=[template_dir])

log = logging.getLogger(__name__)


###########################################################################
#                         Renderers for dialogs                           #
###########################################################################


class DialogRenderer(object):
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
        self._request = request
        self._item = item
        self._action = action
        self._title = title
        self._body = body

    def render(self):
        """Initialize renderer"""
        pass


class ConfirmDialogRenderer(DialogRenderer):
    """Docstring for ConfirmDialogRenderer """

    def __init__(self, request, clazz, action, title=None, body=None):
        """@todo: to be defined """
        DialogRenderer.__init__(self, request, clazz, action, title, body)
        self.template = template_lookup.get_template("internal/confirm.mako")
        self.icon = self._request.static_path(
            'ringo:static/images/icons/32x32/dialog-warning.png')

    def render(self, items):
        _ = self._request.translate
        mapping = {'Action': _(self._action.capitalize())}
        values = {}
        values['request'] = self._request
        values['icon'] = self.icon
        values['header'] = _("Confirm ${Action}", mapping=mapping)
        values['body'] = self._render_body(items)
        values['action'] = _(self._action.capitalize())
        values['ok_url'] = self._request.current_route_path()
        values['_'] = self._request.translate
        values['cancel_url'] = self._request.referrer
        values['eval_url'] = self._request.application_url+eval_url
        return self.template.render(**values)

    def _render_body(self, items):
        out = []
        _ = self._request.translate
        item_label = cgi.escape(get_item_modul(self._request,
                                               self._item).get_label())
        mapping = {'action': cgi.escape(_(self._action.capitalize()).lower()),
                   'item': item_label,
                   'Action': cgi.escape(_(self._action.capitalize()))}
        out.append(_("Do you really want to ${action}"
                     " the following ${item} items?",
                     mapping=mapping))
        out.append("<br>")
        out.append("<ol>")
        for item in items:
            out.append("<li>")
            out.append(cgi.escape(unicode(item)))
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
        self.icon = self._request.static_path(
            'ringo:static/images/icons/32x32/dialog-error.png')

    def render(self, url=None):
        values = {}
        values['icon'] = self.icon
        values['header'] = self._title
        values['body'] = self._render_body()
        history = self._request.session.get('history')
        if url:
            values['ok_url'] = url
        elif history:
            values['ok_url'] = self._request.session['history'].pop()
        else:
            values['ok_url'] = self._request.route_path('home')
        values['eval_url'] = self._request.application_url+eval_url
        return self.template.render(**values)

    def _render_body(self):
        out = []
        out.append(self._body)
        return "".join(out)


class WarningDialogRenderer(ErrorDialogRenderer):
    def __init__(self, request, title, body):
        """@todo: to be defined """
        ErrorDialogRenderer.__init__(self, request, title, body)
        self.template = template_lookup.get_template("internal/warning.mako")
        self.icon = self._request.static_path(
            'ringo:static/images/icons/32x32/dialog-warning.png')


class InfoDialogRenderer(ErrorDialogRenderer):
    def __init__(self, request, title, body):
        """@todo: to be defined """
        ErrorDialogRenderer.__init__(self, request, title, body)
        self.template = template_lookup.get_template("internal/info.mako")
        self.icon = self._request.static_path(
            'ringo:static/images/icons/32x32/dialog-information.png')


class ExportDialogRenderer(DialogRenderer):
    """Docstring for ExportDialogRenderer"""

    def __init__(self, request, clazz):
        """@todo: to be defined """
        DialogRenderer.__init__(self, request, clazz, "export")
        self.template = template_lookup.get_template("internal/export.mako")
        config = Config(load(get_path_to_form_config('export.xml', 'ringo')))
        form_config = config.get_form('default')
        self.form = Form(form_config,
                         csrf_token=self._request.session.get_csrf_token(),
                         dbsession=request.db,
                         eval_url=eval_url,
                         url_prefix=request.application_url)

    def render(self, items):
        _ = self._request.translate
        values = {}
        values['request'] = self._request
        values['items'] = items
        values['body'] = self._render_body()
        values['modul'] = get_item_modul(self._request, self._item).get_label(plural=True)
        values['action'] = _(self._action.capitalize())
        values['ok_url'] = self._request.current_route_path()
        values['_'] = self._request.translate
        values['cancel_url'] = self._request.referrer
        values['eval_url'] = self._request.application_url+eval_url
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
                         csrf_token=self._request.session.get_csrf_token(),
                         dbsession=request.db,
                         eval_url=eval_url,
                         url_prefix=request.application_url)

    def render(self, items):
        values = {}
        values['request'] = self._request
        values['body'] = self._render_body()
        values['modul'] = get_item_modul(self._request, self._item).get_label(plural=True)
        values['action'] = self._action.capitalize()
        values['ok_url'] = self._request.current_route_path()
        values['_'] = self._request.translate
        values['cancel_url'] = self._request.referrer
        values['overview_url'] = self._request.route_path(get_action_routename(self._item, 'list'))
        values['eval_url'] = self._request.application_url+eval_url
        values['items'] = items
        values['h'] = ringo.lib.helpers
        return self.template.render(**values)

    def _render_body(self):
        out = []
        out.append(self.form.render(buttons=False))
        return "".join(out)
