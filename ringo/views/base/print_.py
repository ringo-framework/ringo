import logging
import StringIO
from xml.sax.saxutils import escape
from py3o.template import Template
from ringo.lib.renderer import (
    PrintDialogRenderer
)
from genshi.core import Markup
from ringo.views.request import (
    handle_params,
    handle_history,
    is_confirmed,
    get_item_from_request,
)
from ringo.lib.helpers import prettify

log = logging.getLogger(__name__)


class PrintValueGetter(object):

    def __init__(self, item, request):
        self.item = item
        self.request = request

    def __str__(self):
        return str(self.item)

    def __unicode__(self):
        return unicode(self.item)

    def __getattr__(self, name):
        if hasattr(self.item, name):
            value = self.item.get_value(name, expand=True)
            if isinstance(value, BaseItem):
                return PrintValueGetter(value, self.request)
            elif isinstance(value, basestring):
                value = escape(value)
                return Markup(value.replace("\n", "<text:line-break/>"))
            else:
                return prettify(self.request, value)


def _render_template(request, template, item):
    """Will render the given template with the items data.

    :template: @todo
    :item: @todo
    :returns: @todo

    """
    out = StringIO.StringIO()
    temp = Template(StringIO.StringIO(template.data), out)
    temp.render({"item": item, "print_item": PrintValueGetter(item, request)})
    return out


def _build_response(request, template, data):
    """Will return a response object with the rendererd template

    :request: Current request
    :template: The template.
    :data: Payload of the response
    :returns: Response object.

    """
    resp = request.response
    resp.content_type = str(template.mime)
    resp.content_disposition = 'attachment; filename="%s.odt"' % template.name
    resp.body = data.getvalue()
    return resp


def print_(request):
    handle_history(request)
    handle_params(request)
    item = get_item_from_request(request)
    renderer = PrintDialogRenderer(request, item)
    form = renderer.form
    if (request.method == 'POST'
       and is_confirmed(request)
       and form.validate(request.params)):
        template = form.data.get('printtemplates')[0]
        # Render the template
        out = _render_template(request, template, item)
        # Build response
        return _build_response(request, template, out)
    else:
        clazz = item.__class__
        rvalue = {}
        rvalue['dialog'] = renderer.render()
        rvalue['clazz'] = clazz
        rvalue['item'] = item
        return rvalue
