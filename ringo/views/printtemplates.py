import logging
import mimetypes
from pyramid.view import view_config

from ringo.lib.helpers import get_action_routename
from ringo.views.base import (
    create, rest_create,
    update, rest_update,
    read
)
from ringo.model.printtemplate import Printtemplate

log = logging.getLogger(__name__)


def save_file(request, item):
    """Helper function which is called after the validation of the form
    succeeds. The function will get the data from the file from the
    request and set it in the model including size and mime type.
    Addiotionally it will set the filename based on the uploaded file if
    no other name is given."""
    try:
        #  FIXME: Use global helper method for this??? (ti) <2015-01-31
        #  16:49>
        # Rewind file
        request.POST.get('file').file.seek(0)
        data = request.POST.get('file').file.read()
        filename = request.POST.get('file').filename
        item.data = data
        item.size = len(data)
        item.mime = mimetypes.guess_type(filename)[0]
        if not request.POST.get('name'):
            item.name = filename
    except AttributeError:
        # Will be raised if the user submits no file.
        pass
    return item

#                                HTML VIEW                                #


@view_config(route_name=get_action_routename(Printtemplate, 'create'),
             renderer='/default/create.mako',
             permission='create')
def create_(request):
    return create(request, callback=save_file)


@view_config(route_name=get_action_routename(Printtemplate, 'update'),
             renderer='/default/update.mako',
             permission='update')
def update_(request):
    return update(request, callback=save_file)


@view_config(route_name=get_action_routename(Printtemplate, 'download'),
             permission='download')
def download(request):
    result = read(request)
    item = result['item']
    response = request.response
    response.content_type = str(item.mime)
    response.content_disposition = 'attachment; filename=%s' % item.name
    response.body = item.data
    return response

#                               REST SERVICE                              #

@view_config(route_name=get_action_routename(Printtemplate, 'create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create_(request):
    return rest_create(request, callback=save_file)

@view_config(route_name=get_action_routename(Printtemplate, 'update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update_(request):
    return rest_update(request, callback=save_file)
