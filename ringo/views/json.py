"""
Modul for a simple RESTfull Interface to basic CRUD operations on the
items
"""
from pyramid.view import forbidden_view_config
from pyramid.view import notfound_view_config
from pyramid.response import Response

from formbar.form import Form

from ringo.views.base import _load_item

class JSONResponse(object):
    """Generic response item for JSON responses on the RESTfull api"""

    def __init__(self, success, data, params=None):
        """Create a new JSONResponse. The Response object has the
        following format::

        {
            "success":[true|false],
            "data": object
            "params": {
                "parm1": "value1",
                "parm2": "value1",
                ...
                "parmN": "value1"
            }
        }

        The format of the data or params attribute is not specified. It
        can basically contain any valid JSON. Usually the data attribute
        will contain a dictionary with the attributes of an item or a
        list of  dictionarys with values of items.

        :data: Payload included in the Response.
        :success: Generic status of the query
        :params: Optional parameters. Can include further information.
        E.g why the last request failed.
        """
        self._data = data
        self._success = success
        self._params = params

    def __json__(self, request):
        rvalue = {}
        rvalue['success'] = self._success
        rvalue['data'] = self._data
        rvalue['params'] = self._params
        return rvalue

@forbidden_view_config(path_info='/rest')
def rest_forbidden(request):
    body = '{"success": false, "params": {"error": 403}}'
    response = Response(body=body, content_type='application/json')
    response.status = '403 Forbidden'
    return response

@notfound_view_config(path_info='/rest')
def rest_notfound(request):
    body = '{"success": false, "params": {"error": 404}}'
    response = Response(body=body, content_type='application/json')
    response.status = '404 Not Found'
    return response

def list_(clazz, request):
    """Returns a JSON objcet with all item of a clazz. The list does not
    have any capabilities for sorting or filtering

    :clazz: Class of items to list
    :request: Current request.
    :returns: JSON object.

    """
    listing = clazz.get_item_list(request.db)
    return JSONResponse(True, listing)

def create_(clazz, request):
    """Create a new item of type clazz. The item will be
    initialised with the data provided in the submitted POST request.
    The submitted data will be validated before the item is actually
    saved. If the submission fails the item is not saved in the
    database. In all cases the item is return as JSON object with the
    item and updated values back to the client. The JSON Response will
    include further details on the reason why the validation failed.

    :clazz: Class of item to create
    :request: Current request
    :returns: JSON object.

    """
    # Create a new item.
    factory = clazz.get_item_factory()
    item = factory.create(request.user)
    # Initialise the create form for the item to be able to validate the
    # submitted data.
    form = Form(item.get_form_config('create'), 
                item, request.db, translate=request.translate,
                csrf_token=request.session.get_csrf_token())
    if form.validate(request.params):
            sitem = form.save()
            return JSONResponse(True, sitem)
    else:
        # Validation fails! return item
        return JSONResponse(False, sitem)

def read_(clazz, request):
    """Returns a JSON object of a specific item of type clazz. The
    loaded item is determined by the id provided in the matchdict object
    of the current request.

    :clazz: Class of item to load
    :request: Current request
    :returns: JSON object.
    """
    return JSONResponse(True, _load_item(clazz, request))

def update_(clazz, request):
    """Updates an item of type clazz. The item is loaded based on the
    unique id value provided in the matchtict object in the current
    request. The item will be updated with the data submitted in the
    current PUT request. Before updating the item the data will be
    validated against the "update" form of the item. If the validation
    fails the item will not be updated. In all cases the item is return as
    JSON object with the item and updated values back to the client. The
    JSON Response will include further details on the reason why the
    validation failed.

    :clazz: Class of item to load
    :request: Current request
    :returns: JSON object.
    """
    item = _load_item(clazz, request)
    form = Form(item.get_form_config('update'),
                item, request.db, translate=request.translate,
                csrf_token=request.session.get_csrf_token())
    if form.validate(request.params):
            sitem = form.save()
            return JSONResponse(True, sitem)
    else:
        # Validation fails! return item
        return JSONResponse(False, item)

def delete_(clazz, request):
    """Deletes an item of type clazz. The item is deleted based on the
    unique id value provided in the matchtict object in the current
    DELETE request. The data will be deleted without any futher confirmation!

    :clazz: Class of item to delete
    :request: Current request
    :returns: JSON object.
    """
    item = _load_item(clazz, request)
    request.db.delete(item)
    return JSONResponse(True, item)
