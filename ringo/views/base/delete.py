import logging
import sqlalchemy as sa
import re
from pyramid.httpexceptions import HTTPFound
from ringo.lib.sql.cache import invalidate_cache
from ringo.lib.renderer import ConfirmDialogRenderer, InfoDialogRenderer
from ringo.lib.helpers import (
    get_item_modul
)
from ringo.views.response import JSONResponse
from ringo.views.request import (
    handle_callback,
    get_item_from_request
)
from ringo.views.base.list_ import set_bundle_action_handler

log = logging.getLogger(__name__)


def _handle_redirect(request):
    """Will return a redirect.

    :request: Current request
    :returns: Redirect

    """
    def remove_virtual_path(request, url):
        """This function removes the virtual path from the given URL.
        This is needed because otherwise the regular expression does not
        work.
        """
        virtual_path = request.environ["SCRIPT_NAME"]
        clean_path = url.strip(virtual_path)
        if not clean_path.startswith("/"):
            clean_path = "/"+clean_path
        return clean_path

    clazz = request.context.__model__
    backurl = request.session.get('%s.backurl' % clazz)
    if backurl:
        # Redirect to the configured backurl.
        del request.session['%s.backurl' % clazz]
        request.session.save()
        return HTTPFound(location=backurl)
    else:
        history = request.ringo.history
        # Redirect to page where the user initialy came from to delete
        # the current item. The url depend on how the item is deleted.
        action = re.compile("^\/(\w+)\/(\w+).*")
        action_backurl = re.compile(".*backurl=%2F(\w+)%2F(\w+)%2F.*")
        url = history.last() or ""
        action_match = action.match(remove_virtual_path(request, url))

        if action_match:
            # Initiated delete from detail view of a single item.
            modulname = action_match.group(1)
            while 1:
                url = history.pop()
                if url:
                    clean_path = remove_virtual_path(request, url)
                    m = action.match(clean_path)
                    x = action_backurl.match(clean_path)
                    if m and (m.group(1) != modulname or m.group(2) == "list"):
                        if x:
                            # Has a backurl. Check if the backurl
                            # indicates that the user came from the
                            # recently deleted item and therefore this
                            # URL is very likely to be invalid too.
                            if (x.group(1) != modulname or x.group(2) == "list"):
                                break
                        else:
                            break
                else:
                    url = request.route_path("home")
                    break
        else:
            # We are not sure where to redirect. Use main page
            url = request.route_path("home")
        return HTTPFound(location=url)


def _handle_delete_request(request, items, callback):
    clazz = request.context.__model__
    _ = request.translate
    if request.method == 'POST' and request.ringo.params.confirmed:
        item_label = get_item_modul(request, clazz).get_label(plural=True)
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
            ok_url = request.ringo.history.pop(2)
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
