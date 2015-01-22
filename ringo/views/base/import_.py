import logging
from pyramid.httpexceptions import HTTPFound

from ringo.lib.imexport import (
    JSONImporter,
    CSVImporter
)
from ringo.lib.renderer import (
    ImportDialogRenderer,
    ErrorDialogRenderer
)
from ringo.lib.sql.cache import invalidate_cache
from ringo.views.request import (
    handle_params,
    handle_event,
    handle_history,
    is_confirmed
)

log = logging.getLogger(__name__)

def _import(request):
    """Will read the import file from the request and create or update
    the items in the import file. Finally a list of items will be
    returned. The returned list is a list of tuples. The first element
    in the tuple is the item, the second element is a string with the
    operation (create, update) which was done during import for the
    item.

    :request: Request with importfile and importformat
    :returns: List of items.

    """
    clazz = request.context.__model__
    request.POST.get('file').file.seek(0)
    importfile = request.POST.get('file').file.read()
    if request.POST.get('format') == 'json':
        importer = JSONImporter(clazz, request.db)
    elif request.POST.get('format') == 'csv':
        importer = CSVImporter(clazz)
    return importer.perform(importfile, request.user, request.translate)


def _handle_save(request, items, callback):
    """This function will actually save the imported items. It iterates
    over the imported items and tries to

    * Save the item
    * Call the callback function
    * Call the import handler

    This function returns a list of tuples. The first element of the
    tuple is the element. The second element is the operation done in
    the initial import and the last element is a boolean flag indicating
    if the saving has succeeded.

    :request: Current request
    :items: List of imported items
    :callback: Callback function
    :returns: List of imported items

    """
    imported_items = []
    for item in items:
        item, operation = item[0], item[1]
        try:
            item.save(item.get_values(), request)
            if callback:
                item = callback(request, item)
            # handle update events
            handle_event(request, item, 'import')
            imported_items.append((item, operation, True))
        except:
            imported_items.append((item, operation, False))
    return imported_items


def _handle_redirect(request):
    """If there is a backurl in the session a redirect will be returned.
    Else None.

    :request: Current request
    :returns: Redirect or None

    """
    clazz = request.context.__model__
    backurl = request.session.get('%s.backurl' % clazz)
    if backurl:
        # Redirect to the configured backurl.
        del request.session['%s.backurl' % clazz]
        request.session.save()
        return HTTPFound(location=backurl)


def import_(request, callback=None):
    handle_history(request)
    handle_params(request)

    clazz = request.context.__model__
    _ = request.translate
    renderer = ImportDialogRenderer(request, clazz)
    imported_items = []
    form = renderer.form
    if (request.method == 'POST'
       and is_confirmed(request)
       and form.validate(request.params)):
        try:
            items = _import(request)
        except ValueError as e:
            err_title = _("Import failed")
            err_msg = _("Bad news! The import could not be finished and "
                        "returns with an error."
                        "No data has been modified in this operation and no "
                        "items has been imported or updated. "
                        "The last message we heard from the importer was: %s"
                        % e)
            renderer = ErrorDialogRenderer(request, err_title, err_msg)
            rvalue = {}
            ok_url = request.session['history'].pop(2)
            rvalue['dialog'] = renderer.render(ok_url)
            rvalue['clazz'] = clazz
            return rvalue

        imported_items = _handle_save(request, items, callback)
        invalidate_cache()
        redirect = _handle_redirect(request)
        if redirect:
            return redirect
    rvalue = {}
    rvalue['dialog'] = renderer.render(imported_items)
    rvalue['clazz'] = clazz
    return rvalue
