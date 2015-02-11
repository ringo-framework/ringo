import uuid
import logging
from ringo.model.base import BaseFactory, get_item_list
from ringo.model.user import User
from ringo.lib.table import get_table_config
from ringo.lib.helpers.misc import get_item_modul
from ringo.lib.security import has_permission
from ringo.lib.renderer import (
    ListRenderer
)
from ringo.lib.renderer.dialogs import (
    WarningDialogRenderer
)
from ringo.views.response import JSONResponse
from ringo.views.request import (
    handle_params,
    handle_history
)

# The dictionary will hold the request handlers for bundled actions. The
# dictionary will be filled from the view definitions
_bundle_request_handlers = {}

log = logging.getLogger(__name__)


def get_bundle_action_handler(mapping, action, module):
    if module in mapping:
        views = mapping[module]
        if action in views:
            return views[action]
    return mapping["default"].get(action)


def set_bundle_action_handler(key, handler, module="default"):
    if module in _bundle_request_handlers:
        mod_actions = _bundle_request_handlers.get(module)
    else:
        _bundle_request_handlers[module] = {}
        mod_actions = _bundle_request_handlers.get(module)
    mod_actions[key] = handler
    _bundle_request_handlers[module] = mod_actions


def handle_paginating(clazz, request):
    """Returns a tupe of current page and pagesize. The default page and
    size is page on and all items on one page. This is also the default
    if pagination is not enabled for the table."""

    name = clazz.__tablename__
    # Default pagination options
    if get_table_config(clazz).is_paginated():
        default_page = 0 # First page
        default_size = 50
    else:
        return (0, None)

    # Get pagination from session
    page = request.session.get('%s.list.pagination_page' % name, default_page)
    size = request.session.get('%s.list.pagination_size' % name, default_size)

    # Overwrite options with options from get request
    page = int(request.GET.get('pagination_page', page))
    size = request.GET.get('pagination_size', size)
    if size:
        size = int(size)
    else:
        size = None

    if 'reset' in request.params:
        request.session['%s.list.pagination_page' % name] = default_page
        request.session['%s.list.pagination_size' % name] = default_size
    else:
        request.session['%s.list.pagination_page' % name] = page
        request.session['%s.list.pagination_size' % name] = size
    request.session.save()

    return (page, size)


def handle_sorting(clazz, request):
    """Return a tuple of *fieldname* and *sortorder* (asc, desc). The
    sorting is determined in the follwoing order: First try to get the
    sorting from the current request (GET-Param). If there are no
    sorting params try to get the params saved in the session or if
    requested from a saved search. As last
    fallback use the default sorting for the table.
    """
    name = clazz.__tablename__

    # Default sorting options
    default_field = get_table_config(clazz).get_default_sort_column()
    default_order = get_table_config(clazz).get_default_sort_order()

    # Get sorting from the session. If there is no saved sorting use the
    # default value.
    field = request.session.get('%s.list.sort_field' % name, default_field)
    order = request.session.get('%s.list.sort_order' % name, default_order)

    # Get saved sorting from the the saved search.
    saved_search_id = request.params.get('saved')
    if saved_search_id:
        searches_dic = request.user.settings.get('searches', {})
        if searches_dic:
            search = searches_dic.get(name)
            if search:
                field, order = search.get(saved_search_id, [[], [], None])[1]

    # Get sorting from the request. If there is no sorting option in
    # the request then use the saved sorting options.
    field = request.GET.get('sort_field', field)
    order = request.GET.get('sort_order', order)

    # Save current sorting in the session
    if 'reset' in request.params:
        request.session['%s.list.sort_field' % name] = default_field
        request.session['%s.list.sort_order' % name] = default_order
    else:
        request.session['%s.list.sort_field' % name] = field
        request.session['%s.list.sort_order' % name] = order
    request.session.save()

    return field, order


def get_search(clazz, request):
    """Returns a list of tuples with the search word and the fieldname.
    The function will first look if there is already a saved search in
    the session for the overview of the given clazz. If there is no
    previous search the start with an empty search stack.  The following
    behavior differs depending if it is a POST or GET request:

    1. GET
    Return either an empty search stack or return the saved stack in the
    session.

    2. POST
    Get the new submitted search. If the search is not already on the
    stack, then push it.  If the search word is empty, then pop the last
    search from the stack.  Finally return the modified stack.

    Please note the this function will not save the modified search
    stack in the session! This should be done elsewhere. E.g Depending
    if the search was successfull.
    """
    name = clazz.__tablename__
    # Check if there is already a saved search in the session
    saved_search = request.session.get('%s.list.search' % name, [])

    regexpr = request.session.get('%s.list.search.regexpr' % name, False)
    if "enableregexpr" in request.params:
        request.session['%s.list.search.regexpr' % name] = True
        return saved_search
    elif "disableregexpr" in request.params:
        request.session['%s.list.search.regexpr' % name] = False
        return saved_search

    if 'reset' in request.params:
        return []

    # If the request is not a equest from the search form then
    # abort here and return the saved search params if there are any.
    form_name = request.params.get('form')
    if form_name != "search":
        return saved_search

    saved_search_id = request.params.get('saved')
    if saved_search_id:
        searches_dic = request.user.settings.get('searches', {})
        if searches_dic:
            searches_dic_search = searches_dic.get(name)
            if searches_dic_search:
                return searches_dic_search.get(saved_search_id, [[],
                                               [], None])[0]
    elif "save" in request.params:
        return saved_search
    elif "delete" in request.params:
        return saved_search
    else:
        search = request.params.get('search')
        search_field = request.params.get('field')

    # If search is empty try to pop the last filter in the saved search
    if search == "" and len(saved_search) > 0:
        popped = saved_search.pop()
        log.debug('Popping %s from search stack' % repr(popped))

    # Iterate over the saved search. If the search is not already in the
    # stack push it.
    if search != "":
        found = False
        for x in saved_search:
            if search == x[0] and search_field == x[1]:
                found = True
                break
        if not found:
            log.debug('Adding search for "%s" in field "%s"' % (search,
                                                                search_field))
            saved_search.append((search, search_field, regexpr))
    return saved_search


def bundle_(request):
    clazz = request.context.__model__
    module = get_item_modul(request, clazz)
    handle_history(request)
    handle_params(request)
    _ = request.translate

    # Handle bundle params. If the request has the bundle_action param
    # the request is the intial request for a bundled action. In this
    # case we can delete all previous selected and stored item ids in
    # the session.
    params = request.params.mixed()
    if params.get('bundle_action'):
        request.session['%s.bundle.action' % clazz] = params.get('bundle_action')
        try:
            del request.session['%s.bundle.items' % clazz]
        except KeyError:
            pass
        request.session['%s.bundle.items' % clazz] = params.get('id', [])
    bundle_action = request.session.get('%s.bundle.action' % clazz)
    ids = request.session.get('%s.bundle.items' % clazz)

    # Check if the user selected at least one item. If not show an
    # dialog informing that the selection is empty.
    if not ids:
        title =  _("Empty selection")
        body =  _("You have not selected any item in the list. "
                  "Click 'OK' to return to the overview.")
        renderer = WarningDialogRenderer(request, title, body)
        rvalue = {}
        rvalue['dialog'] = renderer.render(url=request.referrer)
        return rvalue

    # If the user only selects one single item it is not a list. So
    # convert it to a list with one item.
    if not isinstance(ids, list):
        ids = [ids]

    factory = clazz.get_item_factory()
    items = []
    ignored_items = []
    for id in ids:
        # Check if the user is allowed to call the requested action on
        # the loaded item. If so append it the the bundle, if not ignore
        # it.
        item = factory.load(id)
        if has_permission(bundle_action.lower(), item, request):
            items.append(item)
        else:
            ignored_items.append(item)

    # After checking the permissions the list of items might be empty.
    # If so show a warning to the user to inform him that the selected
    # action is not applicable.
    if not items:
        title = _("${action} not applicable",
                  mapping={"action": bundle_action})
        body = _("After checking the permissions no items remain "
                 "for which an '${action}' can be performed. "
                 "(${num} items were filtered out.)",
                 mapping={"action": bundle_action,
                          "num": len(ignored_items)})
        renderer = WarningDialogRenderer(request, title, body)
        rvalue = {}
        rvalue['dialog'] = renderer.render(url=request.referrer)
        return rvalue

    handler = get_bundle_action_handler(_bundle_request_handlers,
                                        bundle_action.lower(),
                                        module.name)
    return handler(request, items)


def list_(request):
    clazz = request.context.__model__
    # Important! Prevent any write access on the database for this
    # request. This is needed as transform would modify the items values
    # else.
    handle_history(request)

    # If the user enters the overview page of an item we assume that the
    # user actually leaves any context where a former set backurl is
    # relevant anymore. So delete it.
    backurl = request.session.get('%s.backurl' % clazz)
    if backurl:
        # Redirect to the configured backurl.
        del request.session['%s.backurl' % clazz]
        request.session.save()

    rvalue = {}
    search = get_search(clazz, request)
    sorting = handle_sorting(clazz, request)
    pagination_page, pagination_size = handle_paginating(clazz, request)
    listing = get_item_list(request, clazz, user=request.user)
    listing.sort(sorting[0], sorting[1])
    listing.filter(search)
    listing.paginate(pagination_page, pagination_size)
    # Only save the search if there are items
    if len(listing.items) > 0:
        request.session['%s.list.search' % clazz.__tablename__] = search
        if (request.params.get('form') == "search"):
            if "save" in request.params:
                query_name = request.params.get('save')
                user = BaseFactory(User).load(request.user.id)
                searches_dic = user.settings.get('searches', {})
                searches_dic_search = searches_dic.get(clazz.__tablename__, {})

                # Check if there is already a search saved with the name
                found = False
                for xxx in searches_dic_search.values():
                    if xxx[1] == query_name:
                        found = True
                        break
                if not found:
                    searches_dic_search[str(uuid.uuid1())] = (search, sorting, query_name)
                searches_dic[clazz.__tablename__] = searches_dic_search
                user.settings.set('searches', searches_dic)
                request.db.flush()
            elif "delete" in request.params:
                query_key = request.params.get('delete')
                user = BaseFactory(User).load(request.user.id)
                searches_dic = user.settings.get('searches', {})
                searches_dic_search = searches_dic.get(clazz.__tablename__, {})
                try:
                    del searches_dic_search[query_key]
                except:
                    pass
                searches_dic[clazz.__tablename__] = searches_dic_search
                user.settings.set('searches', searches_dic)
                request.db.flush()
        request.session.save()

    renderer = ListRenderer(listing)
    rendered_page = renderer.render(request)
    rvalue['clazz'] = clazz
    rvalue['listing'] = rendered_page
    rvalue['itemlist'] = listing
    return rvalue


def rest_list(request):
    """Returns a JSON objcet with all item of a clazz. The list does not
    have any capabilities for sorting or filtering

    :request: Current request.
    :returns: JSON object.

    """
    clazz = request.context.__model__
    listing = get_item_list(request, clazz)
    return JSONResponse(True, listing)
