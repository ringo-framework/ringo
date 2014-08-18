import logging
from pyramid.view import view_config
from ringo.model.news import News
from ringo.views.base.read import rest_read

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
    return rest_read(request, callback=read_callback)
