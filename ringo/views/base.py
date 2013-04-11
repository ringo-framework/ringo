import logging
from sqlalchemy.orm import joinedload
from pyramid.httpexceptions import HTTPFound

from formbar.form import Form

from ringo.lib.renderer import ListRenderer, ConfirmDialogRenderer

log = logging.getLogger(__name__)


def list_(clazz, request):
    rvalue = {}
    # TODO: Check which is the best loading strategy here for large
    # collections. Tests with 100k datasets rendering only 100 shows
    # that the usual lazyload method seems to be the fastest which is
    # not what if have been expected.
    items = request.db.query(clazz).options(joinedload('*')).all()
    renderer = ListRenderer(clazz)
    rvalue['clazz'] = clazz
    rvalue['listing'] = renderer.render(items)
    return rvalue


def create_(clazz, request, callback=None):
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
            msg = _('Created new ${item_type} successfull.', mapping)
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
                    ' for new ${item_type}', mapping)
            request.session.flash(msg, 'error')
    rvalue['clazz'] = clazz
    rvalue['item'] = item
    rvalue['form'] = form.render()
    return rvalue


def update_(clazz, request):
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
            msg = _('Edited ${item_type} "${item}" successfull.', mapping)
            log.info(msg)
            request.session.flash(msg, 'success')
        else:
            msg = _('Error on validation the data for '
                    '${item_type} "${item}".', mapping)
            request.session.flash(msg, 'error')
    rvalue['clazz'] = clazz
    rvalue['item'] = item
    rvalue['form'] = form.render()
    return rvalue


def read_(clazz, request):
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
        msg = _('Deleted ${item_type} "${item}" successfull.', mapping)
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
