import logging
from ringo.lib.imexport import (
    JSONExporter,
    CSVExporter
)
from ringo.lib.renderer import (
    ExportDialogRenderer
)
from ringo.views.request import (
    handle_params,
    handle_history,
    is_confirmed
)
from ringo.views.helpers import get_item_from_request
from ringo.views.base.list_ import set_bundle_action_handler

log = logging.getLogger(__name__)


def export(request):
    handle_history(request)
    handle_params(request)
    item = get_item_from_request(request)
    return _handle_export_request(request, [item])


def _handle_export_request(request, items):
    """Helper function to handle the export request. This function
    provides the required logic to show the export configuration dialog
    and returning the exported items. It is called when exporting a
    single item or when exporting multiple items in a bundle."""
    clazz = request.context.__model__
    renderer = ExportDialogRenderer(request, clazz)
    form = renderer.form
    if (request.method == 'POST'
       and is_confirmed(request)
       and form.validate(request.params)):
        # Setup exporter
        ef = form.data.get('format')
        if ef == "json":
            exporter = JSONExporter(clazz)
        elif ef == "csv":
            exporter = CSVExporter(clazz)
        export = exporter.perform(items)
        # Build response
        resp = request.response
        resp.content_type = str('application/%s' % ef)
        resp.content_disposition = 'attachment; filename=export.%s' % ef
        resp.body = export
        return resp
    else:
        # FIXME: Get the ActionItem here and provide this in the Dialog to get
        # the translation working (torsten) <2013-07-10 09:32>
        rvalue = {}
        rvalue['dialog'] = renderer.render(items)
        return rvalue

set_bundle_action_handler("export", _handle_export_request)
