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


def print_(request):
    item = get_item_from_request(request)
    clazz = item.__class__
    handle_history(request)
    handle_params(clazz, request)
    rvalue = {}

    renderer = PrintDialogRenderer(request, item)
    form = renderer.form
    if (request.method == 'POST'
       and is_confirmed(request)
       and form.validate(request.params)):

        # Render the template
        template = form.data.get('printtemplates')[0]
        out = StringIO.StringIO()
        temp = Template(StringIO.StringIO(template.data), out)
        temp.render({"item": item.get_values()})

        # Build response
        resp = request.response
        resp.content_type = str(template.mime)
        resp.content_disposition = 'attachment; filename=%s' % template.name
        resp.body = out.getvalue()
        return resp
    else:
        # FIXME: Get the ActionItem here and provide this in the Dialog to get
        # the translation working (torsten) <2013-07-10 09:32>
        rvalue['dialog'] = renderer.render()
        rvalue['clazz'] = clazz
        rvalue['item'] = item
        return rvalue
