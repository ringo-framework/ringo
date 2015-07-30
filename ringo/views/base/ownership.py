import logging
from ringo.views.helpers import (
    get_ownership_form,
    get_rendered_ownership_form
)
from ringo.views.request import (
    handle_params,
    handle_history,
    get_return_value,
    get_item_from_request,
    get_item_modul,
    handle_POST_request,
    handle_redirect_on_success
)

log = logging.getLogger(__name__)


def ownership(request, callback=None, renderers=None):
    """Base method to handle requests to change the ownership.

    :request: Current request
    :callback: Current function which is called after the item has been read.
    :returns: Dictionary.
    """
    handle_history(request)
    handle_params(request)
    clazz = request.context.__model__
    item_label = get_item_modul(request, clazz).get_label()
    form = get_ownership_form(request)
    if request.POST:
        item = get_item_from_request(request)
        old_gid = str(item.gid)
        old_uid = str(item.uid)
        new_gid = str(request.params.get('group'))
        new_uid = str(request.params.get('owner'))
        if handle_POST_request(form, request, callback, 'update', renderers):
            if old_uid != new_uid:
                log_msg = u'User {user.login} changed uid of {item_label} '\
                          '{item.id} from {old} -> {new}'\
                          .format(item_label=item_label, item=item, 
                                  user=request.user, old=old_uid, new=new_uid)
                log.info(log_msg)
            if old_gid != new_gid:
                log_msg = u'User {user.login} changed gid of {item_label} '\
                          '{item.id} from {old} -> {new}'\
                          .format(item_label=item_label, item=item, 
                                  user=request.user, old=old_gid, new=new_gid)
                log.info(log_msg)
            return handle_redirect_on_success(request)
    rvalues = get_return_value(request)
    rvalues['form'] = get_rendered_ownership_form(request)
    return rvalues
