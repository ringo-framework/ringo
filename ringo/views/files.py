import logging
import mimetypes
from pyramid.response import FileIter
from pyramid.view import view_config


from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.views.json import (
    list_   as json_list,
    create_ as json_create,
    update_ as json_update,
    read_   as json_read,
    delete_ as json_delete
    )
from ringo.lib.helpers import import_model
File = import_model('ringo.model.file.File')

log = logging.getLogger(__name__)

def save_file(request, item):
    """Helper function which is called after the validation of the form
    succeeds. The function will get the data from the file from the
    request and set it in the model including size and mime type.
    Addiotionally it will set the filename based on the uploaded file if
    no other name is given."""
    try:
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

@view_config(route_name=File.get_action_routename('list'),
             renderer='/default/list.mako',
             permission='list')
def list(request):
    return list_(File, request)


@view_config(route_name=File.get_action_routename('create'),
             renderer='/default/create.mako',
             permission='create')
def create(request):
    return create_(File, request, callback=save_file)


@view_config(route_name=File.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(File, request, callback=save_file)


@view_config(route_name=File.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(File, request)


@view_config(route_name=File.get_action_routename('delete'),
             renderer='/default/confirm.mako',
             permission='delete')
def delete(request):
    return delete_(File, request)


@view_config(route_name=File.get_action_routename('download'),
             permission='download')
def download(request):
    result = read_(File, request)
    item = result['item']
    response = request.response
    response.content_type = str(item.mime)
    response.content_disposition = 'attachment; filename=%s' % item.name
    response.body = item.data
    return response

#                               REST SERVICE                              #

@view_config(route_name=File.get_action_routename('list', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='list'
             )
def rest_list(request):
    return json_list(File, request)

@view_config(route_name=File.get_action_routename('create', prefix="rest"),
             renderer='json',
             request_method="POST",
             permission='create')
def rest_create(request):
    return json_create(File, request, encrypt_password)

@view_config(route_name=File.get_action_routename('read', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='read')
def rest_read(request):
    return json_read(File, request)

@view_config(route_name=File.get_action_routename('update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update(request):
    return json_update(File, request)

@view_config(route_name=File.get_action_routename('delete', prefix="rest"),
             renderer='json',
             request_method="DELETE",
             permission='delete')
def rest_delete(request):
    return json_delete(File, request)
