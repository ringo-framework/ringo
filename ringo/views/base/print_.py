import logging
import StringIO
from py3o.template import Template
from ringo.lib.renderer import (
    PrintDialogRenderer
)
from ringo.views.request import (
    handle_params,
    handle_history,
    is_confirmed,
    get_item_from_request,
)

log = logging.getLogger(__name__)


def _render_template(template, item):
    """Will render the given template with the items data.

    :template: @todo
    :item: @todo
    :returns: @todo

    """
    out = StringIO.StringIO()
    temp = Template(StringIO.StringIO(template.data), out)
    temp.render({"item": item})
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
        out = _render_template(template, item)
        # Build response
        return _build_response(request, template, out)
    else:
        clazz = item.__class__
        rvalue = {}
        rvalue['dialog'] = renderer.render()
        rvalue['clazz'] = clazz
        rvalue['item'] = item
        return rvalue
