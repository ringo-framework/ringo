import logging
from pyramid.httpexceptions import HTTPFound

from ringo.lib.imexport import (
    JSONImporter,
    CSVImporter
)
from ringo.lib.renderer import (
    ImportDialogRenderer
)
from ringo.lib.sql.cache import invalidate_cache
from ringo.views.request import (
    handle_params,
    handle_event,
    handle_history,
    is_confirmed
)

log = logging.getLogger(__name__)


def import__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return import_(clazz, request)


def import_(clazz, request, callback=None):
    handle_history(request)
    handle_params(clazz, request)
    imported_items = []
    rvalue = {}

    # Load the item return 400 if the item can not be found.
    renderer = ImportDialogRenderer(request, clazz)
    form = renderer.form
    if (request.method == 'POST'
       and is_confirmed(request)
       and form.validate(request.params)):
        request.POST.get('file').file.seek(0)
        if request.POST.get('format') == 'json':
            importer = JSONImporter(clazz)
        elif request.POST.get('format') == 'csv':
            importer = CSVImporter(clazz)
        items = importer.perform(request.POST.get('file').file.read(),
                                 request.user,
                                 request.translate)
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

        # TODO: Set URL which is called after the import finished.
        # This should be some kind of a result page showing the imported
        # items (ti) <2014-04-03 10:11>

        # Invalidate cache
        invalidate_cache()
        # Handle redirect after success.
        backurl = request.session.get('%s.backurl' % clazz)
        if backurl:
            # Redirect to the configured backurl.
            del request.session['%s.backurl' % clazz]
            request.session.save()
            return HTTPFound(location=backurl)

    # FIXME: Get the ActionItem here and provide this in the Dialog to get
    # the translation working (torsten) <2013-07-10 09:32>
    rvalue['dialog'] = renderer.render(imported_items)
    rvalue['clazz'] = clazz
    return rvalue
