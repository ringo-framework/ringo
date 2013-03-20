import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from formbar.config import Config, load
from formbar.form import Form

from ringo.model.user import User
from ringo.lib.helpers import get_path_to_form_config

log = logging.getLogger(__name__)


@view_config(route_name='admin-users-list', renderer='/default/list.mako')
def list(request):
    rvalue = {}
    rvalue['item'] = None
    rvalue['items'] = request.db.query(User).all()
    return rvalue


@view_config(route_name='admin-users-create', renderer='/default/create.mako')
def create(request):
    rvalue = {}
    item = User()
    config = Config(load(get_path_to_form_config('user.xml')))
    form_config = config.get_form('create')
    form = Form(form_config, item, request.db)
    if request.POST:
        if form.validate(request.params):
            sitem = form.save()
            log.info('Created new user "%s"' % form.data.get('login'))
            # flush the session to make the new id in the element
            # presistent.
            request.db.flush()
            url = request.route_url('admin-users-update', id=sitem.id)
            # Redirect to the update view.
            return HTTPFound(location=url)

    rvalue['form'] = form.render()
    return rvalue


@view_config(route_name='admin-users-update', renderer='/default/update.mako')
def update(request):
    rvalue = {}
    uid = request.matchdict.get('id')
    user = request.db.query(User).filter(User.id == uid).one()
    config = Config(load(get_path_to_form_config('user.xml')))
    form_config = config.get_form('update')
    form = Form(form_config, user)
    if request.POST:
        if form.validate(request.params):
            form.save()
            log.info('Edited user "%s"' % form.data.get('login'))
    rvalue['form'] = form.render()
    return rvalue


@view_config(route_name='admin-users-read', renderer='/default/read.mako')
def read(request):
    rvalue = {}
    uid = request.matchdict.get('id')
    user = request.db.query(User).filter(User.id == uid).one()
    config = Config(load(get_path_to_form_config('user.xml')))
    form_config = config.get_form('read')
    form = Form(form_config, user)
    rvalue['form'] = form.render()
    return rvalue
