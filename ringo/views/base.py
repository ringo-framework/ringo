import logging
from pyramid.httpexceptions import HTTPFound

from formbar.form import Form

from ringo.model.base import BaseList
from ringo.lib.renderer import ListRenderer, ConfirmDialogRenderer
from ringo.views import handle_history

log = logging.getLogger(__name__)


def handle_sorting(clazz, request):
    name = clazz.__tablename__
    default_sort_field = clazz._table_fields[0][0]
    field = request.GET.get('sort_field', default_sort_field)
    order = request.GET.get('sort_order', 'asc')
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

    # If the request is not a POST request from the search form then
    # abort here and return the saved search params if there are any.
    form_name = request.POST.get('form')
    if form_name != "search":
        return saved_search

    search = request.POST.get('search')
    search_field = request.POST.get('field')

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
            log.debug('Adding search for "%s" in field "%s"' % (search, search_field))
            saved_search.append((search, search_field))
    return saved_search


def list_(clazz, request):
    handle_history(request)
    rvalue = {}
    search = get_search(clazz, request)
    field, order = handle_sorting(clazz, request)
    # TODO: Check which is the best loading strategy here for large
    # collections. Tests with 100k datasets rendering only 100 shows
    # that the usual lazyload method seems to be the fastest which is
    # not what if have been expected.
    #items = request.db.query(clazz).options(joinedload('*')).all()
    listing = BaseList(clazz, request.db)
    listing.sort(field, order)
    listing.filter(search)
    # Only save the search if there are items
    if len(listing.items) > 0:
        request.session['%s.list.search' % clazz.__tablename__] = search
        request.session.save()

    renderer = ListRenderer(listing)
    rendered_page = renderer.render(request)
    rvalue['clazz'] = clazz
    rvalue['listing'] = rendered_page
    return rvalue


def create_(clazz, request, callback=None):
    """Base view to create a new item of type clazz. This view will
    render a create form to create new items. It the user submits the
    data (POST) that the data will be validated and the new item will be
    saved to the database. Finally after saving on the POST-request the
    optional callback will be called.

    :clazz: Class of items which will be created.
    :request: The current request
    :callback: A callback function [function(request, item)] which
    returns the item again.
    :returns: Dictionary with the following keys 'clazz', 'item', 'form'
    """
    handle_history(request)
    _ = request.translate
    rvalue = {}
    factory = clazz.get_item_factory()
    item = factory.create(request.user)
    form = Form(item.get_form_config('create'), item, request.db)
    if request.POST:
        item_label = clazz.get_item_modul().get_label()
        mapping = {'item_type': item_label}
        if form.validate(request.params):
            sitem = form.save()
            msg = _('Created new ${item_type} successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')
            # flush the session to make the new id in the element
            # presistent.
            request.db.flush()
            route_name = sitem.get_action_routename('update')
            url = request.route_url(route_name, id=sitem.id)
            if callback:
                sitem = callback(request, sitem)
            # Redirect to the update view.
            return HTTPFound(location=url)
        else:
            msg = _('Error on validation the data'
                    ' for new ${item_type}', mapping=mapping)
            request.session.flash(msg, 'error')
    rvalue['clazz'] = clazz
    rvalue['item'] = item
    rvalue['form'] = form.render()
    return rvalue


def update_(clazz, request):
    handle_history(request)
    _ = request.translate
    rvalue = {}
    id = request.matchdict.get('id')
    factory = clazz.get_item_factory()
    item = factory.load(id, request.db)
    form = Form(item.get_form_config('update'), item)
    if request.POST:
        item_label = clazz.get_item_modul().get_label()
        mapping = {'item_type': item_label, 'item': item}
        if form.validate(request.params):
            form.save()
            msg = _('Edited ${item_type} "${item}" successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')
            route_name = item.get_action_routename('update')
            url = request.route_url(route_name, id=item.id)
            # Redirect to the update view.
            return HTTPFound(location=url)
        else:
            msg = _('Error on validation the data for '
                    '${item_type} "${item}".', mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'error')
    rvalue['clazz'] = clazz
    rvalue['item'] = item
    rvalue['form'] = form.render()
    return rvalue


def read_(clazz, request):
    handle_history(request)
    rvalue = {}
    id = request.matchdict.get('id')
    factory = clazz.get_item_factory()
    item = factory.load(id, request.db)
    form = Form(item.get_form_config('read'), item)
    rvalue['clazz'] = clazz
    rvalue['item'] = item
    rvalue['form'] = form.render()
    return rvalue


def delete_(clazz, request):
    handle_history(request)
    _ = request.translate
    rvalue = {}
    id = request.matchdict.get('id')
    factory = clazz.get_item_factory()
    item = factory.load(id, request.db)
    if request.method == 'POST' and confirmed(request):
        request.db.delete(item)
        route_name = clazz.get_action_routename('list')
        url = request.route_url(route_name)
        item_label = clazz.get_item_modul().get_label()
        mapping = {'item_type': item_label, 'item': item}
        msg = _('Deleted ${item_type} "${item}" successfull.', mapping=mapping)
        log.info(msg)
        request.session.flash(msg, 'success')
        return HTTPFound(location=url)
    else:
        renderer = ConfirmDialogRenderer(request, item, 'delete')
        rvalue['dialog'] = renderer.render()
        rvalue['clazz'] = clazz
        rvalue['item'] = item
        return rvalue


def confirmed(request):
    """Returns True id the request is confirmed"""
    return request.params.get('confirmed') == "1"
