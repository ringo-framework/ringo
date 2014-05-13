import uuid
import StringIO
import logging
from py3o.template import Template
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config
import sqlalchemy as sa

from formbar.config import Config, load, parse
from formbar.form import Form, variabledecode

from ringo.model.base import BaseFactory
from ringo.model.form import Form as BlobformForm
from ringo.model.mixins import Owned, Logged, Blobform, Versioned
from ringo.lib.helpers import import_model, get_path_to_form_config
from ringo.lib.security import has_role, has_permission
from ringo.lib.imexport import JSONImporter, JSONExporter, \
CSVExporter, CSVImporter
User = import_model('ringo.model.user.User')
from ringo.lib.renderer import (
    ListRenderer, ConfirmDialogRenderer,
    ExportDialogRenderer, ImportDialogRenderer,
    PrintDialogRenderer, add_renderers
)
from ringo.lib.sql import invalidate_cache
from ringo.views import handle_history

log = logging.getLogger(__name__)


def _get_item_from_context(request):
    """On every request pyramid will use a resource factory to load the
    requested resource for the current request. This resource is the
    context for the current request. This function will extract the
    loaded resource from the context. If the context is None, the item
    could not be loaded. In this case raise a 400 HTTP Status code
    exception.

    :request: Current request having the item loaded in the current context
    :returns: Loaded item

    """
    item = request.context.item
    if not item:
        raise HTTPBadRequest()
    return item


def get_current_form_page(clazz, request):
    """Returns the id of the currently selected page. The currently
    selected page is saved in the session. If there is no saved value
    then the the first page is returned

    :clazz: The clazz for which the form is displayed
    :request: Current request
    :returns: id of the currently selected page. Default: 1
    """
    itemid = request.matchdict.get('id')
    item = clazz.__tablename__
    page = request.session.get('%s.%s.form.page' % (item, itemid))
    if page:
        return int(page)
    else:
        return 1


def get_ownership_form(item, request, readonly=None):
    if (readonly is None and isinstance(item, Owned)):
        readonly = not (item.is_owner(request.user)
                        or has_role(request.user, "admin"))
    config = Config(load(get_path_to_form_config('ownership.xml', 'ringo')))
    if readonly:
        form_config = config.get_form('ownership-form-read')
    else:
        form_config = config.get_form('ownership-form-update')
    return Form(form_config, item, request.db,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')


def get_logbook_form(item, request, readonly=None, renderers={}):
    config = Config(load(get_path_to_form_config('logbook.xml', 'ringo')))
    if readonly:
        form_config = config.get_form('logbook-form-read')
    else:
        form_config = config.get_form('logbook-form-update')
    return Form(form_config, item, request.db,
                renderers=renderers,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')


@view_config(route_name='set_current_form_page')
def set_current_form_page(request):
    """Will save the currently selected page of a form in the session.
    The request will have some attributes in the GET request which will
    config which page, of which item is currently shown. This function
    is used as a callback function within formbar.

    :request: Current request
    :returns: Response
    """
    page = request.GET.get('page')
    item = request.GET.get('item')
    itemid = request.GET.get('itemid')
    if page and item and itemid:
        #request.session['%s.form.page' % key] = page_id
        request.session['%s.%s.form.page' % (item, itemid)] = page
        request.session.save()
    return Response(body='OK', content_type='text/plain')


def get_blobform_config(request, item, formname):
    """Helper function used in the create_ method to setup the create
    forms for blogform items. To create a new blogform item the
    creation is done in three steps:

    1. Stage 1: The user selects a form from a list
    2. Stage 2: The create dialog is rendered with the selected form
    3. Stage 3: The item is validated and saved.

    :request: current request
    :item: item to build the form
    :formname: name of the form in the formconfig
    :returns: formconfig, item used to build a form.

    """
    # First check if the fid parameter is provided
    fid = request.params.get('fid')
    blobform = request.params.get('blobforms')
    if fid:
        log.debug("Stage 3: User has submitted data to create a new item")
        setattr(item, 'fid', fid)
        formfactory = BlobformForm.get_item_factory()
        formconfig = Config(parse(formfactory.load(fid).definition))
        return item, formconfig.get_form(formname)
    elif blobform:
        log.debug("Stage 2: User has selected a blobform %s " % blobform)
        setattr(item, 'fid', blobform)
        formfactory = BlobformForm.get_item_factory()
        formconfig = Config(parse(formfactory.load(blobform).definition))
        return item, formconfig.get_form(formname)
    else:
        log.debug("Stage 1: User is selecting a blobform")
        modul = item.get_item_modul()
        formconfig = modul.get_form_config("blobform")
        return modul, formconfig


def handle_event(event, request, item):
    """Will call the event listeners for the given event on every base
    class of the given item."""
    for class_ in item.__class__.__bases__:
        if hasattr(class_, event + '_handler'):
            handler = getattr(class_, event + '_handler')
            handler(request, item)


def handle_params(clazz, request):
    """Handles varios sytem GET params comming with the request
    Known params are:

     * backurl: A url which should be called instead of the default
       action after the next request succeeds. The backurl will be saved
       in the session and stays there until it is deleted on a
       successfull request. So take care to delete it to not mess up
       with the application logic.
     * form: The name of a alternative form configuration which is
       used for the request.
     * values: A comma separated list of key/value pair. Key and value
       are separated with an ":"
     * addrelation: A ":" separated string 'relation:class:id' to identify that
       a item with id should be linked to the relation of this item.
    """
    params = {}
    backurl = request.GET.get('backurl')
    if backurl:
        request.session['%s.backurl' % clazz] = backurl
        params['backurl'] = backurl
    values = request.GET.get('values')
    if values:
        params['values'] = {}
        for kvpair in values.split(','):
            key, value = kvpair.split(':')
            params['values'][key] = value
    form = request.GET.get('form')
    if form:
        request.session['%s.form' % clazz] = form
        params['form'] = form
    relation = request.GET.get('addrelation')
    if relation:
        request.session['%s.addrelation' % clazz] = relation
        params['addrelation'] = relation
    request.session.save()
    return params


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
    default_field = clazz.get_table_config().get_default_sort_column()
    default_order = clazz.get_table_config().get_default_sort_order()

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
            saved_search.append((search, search_field))
    return saved_search

def bundle_(request):
    clazz = request.context.__model__
    handle_history(request)
    handle_params(clazz, request)

    # Handle bundle params. If the request has the bundle_action param
    # the request is the intial request for a bundled action. In this
    # case we can delete all previous selected and stored item ids in
    # the session.
    params = variabledecode.variable_decode(request.params)
    if params.get('bundle_action'):
        request.session['%s.bundle.action' % clazz] = params.get('bundle_action')
        try:
            del request.session['%s.bundle.items' % clazz]
        except KeyError:
            pass
        request.session['%s.bundle.items' % clazz] = params.get('id', [])
    bundle_action = request.session.get('%s.bundle.action' % clazz)
    ids = request.session.get('%s.bundle.items' % clazz)

    factory = clazz.get_item_factory()
    items = []
    for id in ids:
        # Check if the user is allowed to call the requested action on
        # the loaded item. If so append it the the bundle, if not ignore
        # it.
        item = factory.load(id)
        if has_permission(bundle_action.lower(), item, request):
            items.append(item)

    if bundle_action == 'Export':
        rvalue = _handle_export_request(clazz, request, items)
    elif bundle_action == 'Delete':
        rvalue = _handle_delete_request(clazz, request, items)
    return rvalue


def list_(clazz, request):
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
    listing = clazz.get_item_list(request, user=request.user)
    listing.sort(sorting[0], sorting[1])
    listing.filter(search)
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


def create_(clazz, request, callback=None, renderers={}):
    """Base view to create a new item of type clazz. This view will
    render a create form to create new items. It the user submits the
    data (POST) that the data will be validated and the new item will be
    saved to the database. Finally after saving on the POST-request the
    optional callback will be called.

    :clazz: Class of items which will be created.
    :request: The current request
    :callback: A callback function [function(request, item)] which
    returns the item again.
    :renderers: A optional dictionary of custom renderers which are
    provided to the form to render specific formelements.
    :returns: Dictionary with the following keys 'clazz', 'item', 'form'
    """
    handle_history(request)
    params = handle_params(clazz, request)
    _ = request.translate
    rvalue = {}

    # Add ringo specific renderers
    renderers = add_renderers(renderers)

    # Create a new item
    factory = clazz.get_item_factory()
    item = factory.create(request.user)

    formname = request.session.get('%s.form' % clazz)
    if not formname:
        formname = 'create'

    # handle blobforms
    do_validate = True
    if isinstance(item, Blobform):
        item, formconfig = get_blobform_config(request, item, formname)
        do_validate = "blobforms" not in request.params
    else:
        formconfig = item.get_form_config(formname)

    form = Form(formconfig, item,
                request.db, translate=_,
                renderers=renderers,
                change_page_callback={'url': 'set_current_form_page',
                                      'item': clazz.__tablename__,
                                      'itemid': None},
                request=request,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')

    if request.POST and do_validate:
        item_label = clazz.get_item_modul().get_label()
        mapping = {'item_type': item_label}
        if form.validate(request.params):

            # Handle linking of the new item to antoher relation. The
            # relation was provided as GET parameter in the current
            # request and is now saved in the session.
            addrelation = request.session.get('%s.addrelation' % clazz)
            if addrelation:
                rrel, rclazz, rid = addrelation.split(':')
                parent = import_model(rclazz)
                pfactory = parent.get_item_factory()
                pitem = pfactory.load(rid)
                log.debug('Linking %s to %s in %s' % (item, pitem, rrel))
                tmpattr = getattr(pitem, rrel)
                tmpattr.append(item)

            # Save the item. Save validated values submitted from the
            # form into the new created item.
            sitem = item.save(form.data, request)
            msg = _('Created new ${item_type} successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')

            # handle create events
            handle_event('create', request, item)

            # Call callback. The callback is called as last action after
            # the rest of the saving has been done.
            if callback:
                sitem = callback(request, sitem)

            # Invalidate cache
            invalidate_cache()
            formname = request.session.get('%s.form' % clazz)
            if formname:
                del request.session['%s.form' % clazz]
                request.session.save()

            # Handle redirect after success.
            backurl = request.session.get('%s.backurl' % clazz)
            if backurl:
                # Redirect to the configured backurl.
                del request.session['%s.backurl' % clazz]
                request.session.save()
                return HTTPFound(location=backurl)
            else:
                # Set the URL the user will be redirected after the save
                # operation. URL depends on whether the user is allowed to
                # call the update page or not.
                if has_permission("update", item, request):
                    route_name = item.get_action_routename('update')
                    url = request.route_path(route_name, id=item.id)
                else:
                    route_name = item.get_action_routename('read')
                    url = request.route_path(route_name, id=item.id)
                return HTTPFound(location=url)
        else:
            msg = _('Error on validation the data'
                    ' for new ${item_type}', mapping=mapping)
            request.session.flash(msg, 'error')
    rvalue['clazz'] = clazz
    rvalue['item'] = item
    values = {'_roles': [str(r.name) for r in request.user.get_roles()]}
    values.update(params.get('values', {}))
    rvalue['form'] = form.render(values=values,
                                 page=get_current_form_page(clazz, request))
    return rvalue


def update_(clazz, request, callback=None, renderers={}):
    item = _get_item_from_context(request)
    handle_history(request)
    handle_params(clazz, request)
    _ = request.translate
    rvalue = {}

    # Add ringo specific renderers
    renderers = add_renderers(renderers)

    owner_form = get_ownership_form(item, request)
    logbook_form = get_logbook_form(item, request, readonly=True,
                                    renderers=renderers)
    item_form_name = request.session.get("%s.form" % clazz) or "update"
    item_form = Form(item.get_form_config(item_form_name),
                item, request.db, translate=_,
                renderers=renderers,
                change_page_callback={'url': 'set_current_form_page',
                                      'item': clazz.__tablename__,
                                      'itemid': item.id},
                request=request, csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')

    if request.POST:
        # Check which form should handled. If the submitted data has the
        # key "owner" than handle the ownership form.
        if 'owner' in request.params:
            form = owner_form
        else:
            form = item_form

        item_label = clazz.get_item_modul().get_label()
        mapping = {'item_type': item_label, 'item': item}
        if form.validate(request.params):
            item.save(form.data, request)
            msg = _('Edited ${item_type} "${item}" successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')

            # handle update events
            handle_event('update', request, item)

            # Call callback. The callback is called as last action after
            # the rest of the saving has been done.
            if callback:
                item = callback(request, item)

            # Invalidate cache
            invalidate_cache()
            if request.session.get('%s.form' % clazz):
                del request.session['%s.form' % clazz]
                request.session.save()

            backurl = request.session.get('%s.backurl' % clazz)
            if backurl:
                # Redirect to the configured backurl.
                del request.session['%s.backurl' % clazz]
                request.session.save()
                return HTTPFound(location=backurl)
            else:
                # Handle redirect after success.
                # Check if the user is allowed to call the url after saving
                if has_permission("update", item, request):
                    route_name = item.get_action_routename('update')
                    url = request.route_path(route_name, id=item.id)
                else:
                    route_name = item.get_action_routename('read')
                    url = request.route_path(route_name, id=item.id)
                return HTTPFound(location=url)
        else:
            msg = _('Error on validation the data for '
                    '${item_type} "${item}".', mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'error')

    # Validate the form to generate the warnings if the form has not
    # been alreaded validated.
    if not item_form.validated:
        item_form.validate(None)

    rvalue['clazz'] = clazz
    rvalue['item'] = item
    if isinstance(item, Owned):
        rvalue['owner'] = owner_form.render()
    else:
        rvalue['owner'] = ""
    if isinstance(item, Logged):
        rvalue['logbook'] = logbook_form.render()
    else:
        rvalue['logbook'] = ""

    # Add ringo specific values into the renderered form
    values = {'_roles': [str(r.name) for r in request.user.get_roles()]}
    rvalue['form'] = item_form.render(values = values,
                                      page = get_current_form_page(clazz, request))
    return rvalue


def read_(clazz, request, callback=None, renderers={}):
    item = _get_item_from_context(request)
    handle_history(request)
    handle_params(clazz, request)
    _ = request.translate
    rvalue = {}

    # Add ringo specific renderers
    renderers = add_renderers(renderers)

    owner_form = get_ownership_form(item, request, readonly=True)
    logbook_form = get_logbook_form(item, request, readonly=True,
                                    renderers=renderers)
    item_form = Form(item.get_form_config('read'), item, request.db,
                     translate=_,
                     renderers=renderers,
                     change_page_callback={'url': 'set_current_form_page',
                                           'item': clazz.__tablename__,
                                           'itemid': item.id},
                     request=request, csrf_token=request.session.get_csrf_token(),
                     eval_url='/rest/rule/evaluate')

    # Validate the form to generate the warnings if the form has not
    # been alreaded validated.
    if not item_form.validated:
        item_form.validate(None)

    if callback:
        item = callback(request, item)

    rvalue['clazz'] = clazz
    rvalue['item'] = item
    if isinstance(item, Owned):
        rvalue['owner'] = owner_form.render()
    else:
        rvalue['owner'] = ""
    if isinstance(item, Logged):
        rvalue['logbook'] = logbook_form.render()
    else:
        rvalue['logbook'] = ""

    if isinstance(item, Versioned):
        previous_values = item.get_previous_values(author=request.user.login)
    else:
        previous_values = {}
    # Add ringo specific values into the renderered form
    values = {'_roles': [str(r.name) for r in request.user.get_roles()]}
    rvalue['form'] = item_form.render(page=get_current_form_page(clazz, request),
                                      values = values,
                                      previous_values=previous_values)
    return rvalue

def _handle_delete_request(clazz, request, items):
    _ = request.translate
    rvalue = {}
    if request.method == 'POST' and confirmed(request):
        for item in items:
            request.db.delete(item)
        route_name = clazz.get_action_routename('list')
        url = request.route_path(route_name)
        item_label = clazz.get_item_modul().get_label(plural=True)
        mapping = {'item_type': item_label, 'item': item, 'num': len(items)}
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


def delete_(clazz, request):
    item = _get_item_from_context(request)
    handle_history(request)
    handle_params(clazz, request)
    return _handle_delete_request(clazz, request, [item])

def export_(clazz, request):
    item = _get_item_from_context(request)
    handle_history(request)
    handle_params(clazz, request)
    return _handle_export_request(clazz, request, [item])

def _handle_export_request(clazz, request, items):
    """Helper function to handle the export request. This function
    provides the required logic to show the export configuration dialog
    and returning the exported items. It is called when exporting a
    single item or when exporting multiple items in a bundle."""
    rvalue = {}
    renderer = ExportDialogRenderer(request, clazz)
    form = renderer.form
    if (request.method == 'POST'
       and confirmed(request)
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
        rvalue['dialog'] = renderer.render(items)
        return rvalue


def import_(clazz, request, callback=None):
    handle_history(request)
    handle_params(clazz, request)
    imported_items = []
    rvalue = {}

    # Load the item return 400 if the item can not be found.
    renderer = ImportDialogRenderer(request, clazz)
    form = renderer.form
    if (request.method == 'POST'
       and confirmed(request)
       and form.validate(request.params)):
        request.POST.get('file').file.seek(0)
        if request.POST.get('format') == 'json':
            importer = JSONImporter(clazz)
        elif request.POST.get('format') == 'csv':
            importer = CSVImporter(clazz)
        items = importer.perform(request, request.POST.get('file').file.read())
        for item in items:
            item, operation = item[0], item[1]
            try:
                item.save(item.get_values(), request)
                route_name = item.get_action_routename('update')
                url = request.route_path(route_name, id=item.id)
                if callback:
                    item = callback(request, item)
                # handle update events
                handle_event('import', request, item)
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

def print_(request):
    item = request.context.item
    clazz = item.__class__
    handle_history(request)
    handle_params(clazz, request)
    rvalue = {}

    renderer = PrintDialogRenderer(request, item)
    form = renderer.form
    if (request.method == 'POST'
       and confirmed(request)
       and form.validate(request.params)):

        # Render the template
        template = form.data.get('printtemplates')[0]
        out = StringIO.StringIO()
        temp = Template(StringIO.StringIO(template.data), out)
        temp.render({"item":item.get_values()})

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


def confirmed(request):
    """Returns True id the request is confirmed"""
    return request.params.get('confirmed') == "1"
