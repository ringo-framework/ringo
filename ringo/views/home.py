import pkg_resources

from pyramid.view import view_config

from ringo.lib.helpers import (
    get_ringo_version,
    get_app_version,
    get_app_name,
    get_app_title
)
from ringo.lib.renderer import DTListRenderer, NewsListRenderer

from ringo.model.base import BaseList
from ringo.model.appointment import Reminders
from ringo.model.news import News
from ringo.views import handle_history


@view_config(route_name='home', renderer='/index.mako')
def index_view(request):
    reminders = Reminders(request.db)

    if request.user:
        news_for_user = request.user.news
    else:
        news_for_user = []
    news = BaseList(News, request.db, items=news_for_user)

    reminder_renderer = DTListRenderer(reminders)
    news_renderer = NewsListRenderer(news)
    handle_history(request)
    values = {}
    values['reminders'] = reminder_renderer.render(request)
    values['news'] = news_renderer.render(request)
    return values


@view_config(route_name='about', renderer='/about.mako')
def about_view(request):
    handle_history(request)
    values = {}
    values['app_title'] = get_app_title()
    return values


@view_config(route_name='contact', renderer='/contact.mako')
def contact_view(request):
    handle_history(request)
    return {}


@view_config(route_name='version', renderer='/version.mako')
def version_view(request):
    # Fetch the versions of some Packages
    # Ringo
    handle_history(request)
    values = {}
    formbar_pkg = pkg_resources.get_distribution('formbar')
    sqla_pkg = pkg_resources.get_distribution('sqlalchemy')
    pyramid_pkg = pkg_resources.get_distribution('pyramid')
    values['app_title'] = get_app_title()
    values['app_version'] = get_app_version()
    values['app_name'] = get_app_name()
    values['ringo_version'] = get_ringo_version()
    values['app_version'] = get_app_version()
    values['formbar_version'] = formbar_pkg.version
    values['sqlalchemy_version'] = sqla_pkg.version
    values['pyramid_version'] = pyramid_pkg.version
    return values
