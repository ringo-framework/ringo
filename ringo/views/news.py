import logging
from pyramid.view import view_config
from ringo.model.news import News
from ringo.views.base import read_, update_
from ringo.views.json import read_ as json_read

log = logging.getLogger(__name__)

def _mark_news_as_read(request, item):
    """Will mark the given news item as read for the current user of the request.

    :request: current request
    :item: news item
    :returns: news item

    """
    user = request.user
    user.news.remove(item)
    return item

def read_callback(request, item):
    """Callback which is called right after the news item has been loaded.

    :request: current request
    :item: the news item
    :returns: news item

    """
    item = _mark_news_as_read(request, item)
    return item

@view_config(route_name=News.get_action_routename('markasread', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='read')
def rest_markasread(request):
    return json_read(News, request, callback=read_callback)


# FIXME: Overwritten templates for News. These templates do not escape
# the header as it might contain links. This is a security risk! (ti)
# See https://bitbucket.org/ti/ringo/issue/66/add-link-fields-to-news-modul
# <2014-08-28 12:20> 
@view_config(route_name=News.get_action_routename('read'),
             renderer='/news/read.mako',
             permission='read')
def read(request):
    return read_(News, request)

@view_config(route_name=News.get_action_routename('update'),
             renderer='/news/update.mako',
             permission='update')
def update(request):
    return update_(News, request)
