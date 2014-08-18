import logging
from pyramid.httpexceptions import HTTPFound
from ringo.lib.sql.cache import invalidate_cache
from ringo.lib.renderer import ConfirmDialogRenderer
from ringo.views.request import (
    handle_params,
    handle_history,
    is_confirmed,
    get_item_from_request
)

log = logging.getLogger(__name__)


def _handle_delete_request(clazz, request, items):
    _ = request.translate
    rvalue = {}
    if request.method == 'POST' and is_confirmed(request):
        for item in items:
            request.db.delete(item)
        route_name = clazz.get_action_routename('list')
        url = request.route_path(route_name)
        item_label = clazz.get_item_modul(request).get_label(plural=True)
        mapping = {'item_type': item_label, 'num': len(items)}
        msg = _('Deleted ${num} ${item_type} successfull.', mapping=mapping)
        log.info(msg)
        request.session.flash(msg, 'success')
        # Invalidate cache
        invalidate_cache()
        # Handle redirect after success.
        backurl = request.session.get('%s.backurl' % clazz)
        if backurl:
            # Redirect to the configured backurl.
            del request.session['%s.backurl' % clazz]
            request.session.save()
            return HTTPFound(location=backurl)
        else:
            # Redirect to the update view.
            return HTTPFound(location=url)
    else:
        # FIXME: Get the ActionItem here and provide this in the Dialog to get
        # the translation working (torsten) <2013-07-10 09:32>
        renderer = ConfirmDialogRenderer(request, clazz, 'delete')
        rvalue['dialog'] = renderer.render(items)
        rvalue['clazz'] = clazz
        rvalue['item'] = items
        return rvalue


def delete__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return delete_(clazz, request)


def delete_(clazz, request):
    item = get_item_from_request(request)
    handle_history(request)
    handle_params(clazz, request)
    return _handle_delete_request(clazz, request, [item])
