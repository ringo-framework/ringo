import uuid
import StringIO
import logging
from py3o.template import Template
from pyramid.httpexceptions import HTTPFound
import sqlalchemy as sa

from formbar.form import Form

from ringo.model.base import BaseFactory
from ringo.model.mixins import Owned, Logged, Versioned
from ringo.lib.helpers import import_model
from ringo.lib.security import has_permission
from ringo.lib.imexport import JSONImporter, JSONExporter, \
CSVExporter, CSVImporter
User = import_model('ringo.model.user.User')
from ringo.lib.renderer import (
    ListRenderer, ConfirmDialogRenderer,
    ExportDialogRenderer, ImportDialogRenderer,
    PrintDialogRenderer, add_renderers
)
from ringo.lib.sql.cache import invalidate_cache
from ringo.views.crud.create import (
    create_,
    create__
)
from ringo.views.forms import (
    get_ownership_form,
    get_logbook_form
)
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_event,
    is_confirmed,
    get_item_from_request,
    get_current_form_page
)

log = logging.getLogger(__name__)


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

    regexpr = request.session.get('%s.list.search.regexpr' % name, False)
    if "enableregexpr" in request.params:
        request.session['%s.list.search.regexpr' % name] = True
        return saved_search
    elif  "disableregexpr" in request.params:
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
    handle_history(request)
    handle_params(clazz, request)

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
    # If the user only selects one single item it is not a list. So
    # convert it to a list with one item.
    if not isinstance(ids, list):
        ids = [ids]

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

def list__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return list_(clazz, request)

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

def update__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return update_(clazz, request)

def update_(clazz, request, callback=None, renderers={}):
    item = get_item_from_request(request)
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

        item_label = clazz.get_item_modul(request).get_label()
        mapping = {'item_type': item_label, 'item': item}
        if form.validate(request.params):
            item.save(form.data, request)
            msg = _('Edited ${item_type} "${item}" successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')

            # handle update events
            handle_event(request, item, 'update')

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

def read__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return read_(clazz, request)

def read_(clazz, request, callback=None, renderers={}):
    item = get_item_from_request(request)
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

def export__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return export_(clazz, request)

def export_(clazz, request):
    item = get_item_from_request(request)
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
        rvalue['dialog'] = renderer.render(items)
        return rvalue

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
                route_name = item.get_action_routename('update')
                url = request.route_path(route_name, id=item.id)
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

def print_(request):
    item = request.context.item
    clazz = item.__class__
    handle_history(request)
    handle_params(clazz, request)
    rvalue = {}

    renderer = PrintDialogRenderer(request, item)
    form = renderer.form
    if (request.method == 'POST'
       and is_confirmed(request)
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


action_view_mapping = {
    "list": list__,
    "create": create__,
    "read": read__,
    "update": update__,
    "delete": delete__,
    "import": import__,
    "export": export__,
    "print":  print_,
}
