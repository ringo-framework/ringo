import logging
from pyramid.view import view_config
from ringo.model.modul import ModulItem
from ringo.lib.sql import DBSession
from ringo.lib.helpers import dynamic_import
from ringo.model.mixins import Printable

log = logging.getLogger(__name__)

def setup_mixin_views(config):
    from ringo.views.base import print_
    for modul in DBSession.query(ModulItem).all():
        clazzpath = modul.clazzpath
        clazz = dynamic_import(clazzpath)
        if issubclass(clazz, Printable):
            config.add_view(print_, route_name=clazz.get_action_routename('print'),
                            renderer='/default/print.mako',
                            permission='read')
    return config


