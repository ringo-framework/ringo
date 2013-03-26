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
    rvalue['listing'] = renderer.render(items)
    return rvalue


def create_(clazz, request):
    rvalue = {}
    item = clazz()
    form = Form(item.get_form_config('create'), item, request.db)
    if request.POST:
        if form.validate(request.params):
            sitem = form.save()
            log.info('Created new user "%s"' % form.data.get('login'))
            # flush the session to make the new id in the element
            # presistent.
            request.db.flush()
            route_name = sitem.get_action_routename('update')
            url = request.route_url(route_name, id=sitem.id)
            # Redirect to the update view.
            return HTTPFound(location=url)
    rvalue['form'] = form.render()
    return rvalue


def update_(clazz, request):
    rvalue = {}
    id = request.matchdict.get('id')
    item = request.db.query(clazz).filter(clazz.id == id).one()
    form = Form(item.get_form_config('update'), item)
    if request.POST:
        if form.validate(request.params):
            form.save()
            msg = '"%s" was edited successfull.' % item
            request.session.flash(msg, 'success')
            log.info('Edited "%s"' % form.data.get('login'))
    rvalue['item'] = item
    rvalue['form'] = form.render()
    return rvalue


def read_(clazz, request):
    rvalue = {}
    id = request.matchdict.get('id')
    item = request.db.query(clazz).filter(clazz.id == id).one()
    form = Form(item.get_form_config('read'), item)
    rvalue['item'] = item
    rvalue['form'] = form.render()
    return rvalue


def delete_(clazz, request):
    rvalue = {}
    id = request.matchdict.get('id')
    item = request.db.query(clazz).filter(clazz.id == id).one()
    if request.method == 'POST' and confirmed(request):
        request.db.delete(item)
        route_name = clazz.get_action_routename('list')
        url = request.route_url(route_name)
        msg = '"%s" was deleted successfull.' % item
        request.session.flash(msg, 'success')
        log.info('Deleted "%s"' % item)
        return HTTPFound(location=url)
    else:
        renderer = ConfirmDialogRenderer(request, item, 'delete')
        rvalue['dialog'] = renderer.render()
        return rvalue


def confirmed(request):
    """Returns True id the request is confirmed"""
    return request.params.get('confirmed') == "1"
