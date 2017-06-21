import logging
import sqlalchemy as sa
from pyramid.httpexceptions import HTTPFound
from ringo.lib.sql.cache import invalidate_cache
from ringo.lib.renderer import ConfirmDialogRenderer, InfoDialogRenderer
from ringo.lib.helpers import (
    get_action_routename,
    get_item_modul
)
from ringo.views.response import JSONResponse
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_callback,
    is_confirmed,
    get_item_from_request
)
from ringo.views.base.list_ import set_bundle_action_handler
from ringo.views.callbacks import Callback

log = logging.getLogger(__name__)


def _handle_redirect(request):
    """Will return a redirect.

    :request: Current request
    :returns: Redirect

    """
    clazz = request.context.__model__
    backurl = request.session.get('%s.backurl' % clazz)
    if backurl:
        # Redirect to the configured backurl.
        del request.session['%s.backurl' % clazz]
        request.session.save()
        return HTTPFound(location=backurl)
    else:
        # Redirect to the list view.
        route_name = get_action_routename(clazz, 'list')
        url = request.route_path(route_name)
        return HTTPFound(location=url)


def _handle_delete_request(request, items, callback):
    clazz = request.context.__model__
    _ = request.translate
    if request.method == 'POST' and is_confirmed(request):
        item_label = get_item_modul(request, clazz).get_label(plural=True)
        item_label_log = get_item_modul(request, clazz).get_label()
        mapping = {'item_type': item_label, 'num': len(items)}
        for item in items:
            handle_callback(request, callback, item=item, mode="pre,default")
            request.db.delete(item)
            handle_callback(request, callback, item=item, mode="post")
        # Invalidate cache
        invalidate_cache()
        try:
            request.db.flush()
        except (sa.exc.CircularDependencyError, sa.exc.IntegrityError) as e:
            mapping["error"] = e.message.decode("utf-8")
            title = _("Can not delete ${item_type} items.",
                      mapping=mapping)
            body = _("There has been an integrity error which prevents "
                     "the request to be fulfilled. There are still "
                     "depended items on the item to be deleted. Please "
                     "remove all depended relations to this item before "
                     "deleting it and try again. Hint: ${error}",
                     mapping=mapping)
            request.db.rollback()
            renderer = InfoDialogRenderer(request, title, body)
            rvalue = {}
            ok_url = request.session['history'].pop(2)
            rvalue['dialog'] = renderer.render(ok_url)
            return rvalue

        msg = _('Deleted ${num} ${item_type} successfully.', mapping=mapping)
        log_msg = u'User {user.login} deleted {item_label} {item.id}' \
            .format(item_label=item_label, item=item, user=request.user)
        log.info(log_msg)
        request.session.flash(msg, 'success')
        # Handle redirect after success.
        return _handle_redirect(request)
    else:
        renderer = ConfirmDialogRenderer(request, clazz, 'delete')
        rvalue = {}
        rvalue['dialog'] = renderer.render(items)
        rvalue['clazz'] = clazz
        rvalue['item'] = items
        return rvalue


def delete(request, callback=None):
    item = get_item_from_request(request)
    handle_history(request)
    handle_params(request)
    return _handle_delete_request(request, [item], callback)


def rest_delete(request, callback=None):
    """Deletes an item of type clazz. The item is deleted based on the
    unique id value provided in the matchtict object in the current
    DELETE request. The data will be deleted without any futher confirmation!

    :clazz: Class of item to delete
    :request: Current request
    :returns: JSON object.
    """
    item = get_item_from_request(request)
    request.db.delete(item)
    return JSONResponse(True, item)

set_bundle_action_handler("delete", _handle_delete_request)
