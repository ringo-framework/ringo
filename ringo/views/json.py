"""
Modul for a simple RESTfull Interface to basic CRUD operations on the
items
"""
from formbar.form import Form

from ringo.views.base import rest_create, rest_update
from ringo.views.request import get_item_from_request
from ringo.views.response import JSONResponse


def list__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return list_(clazz, request)

def list_(clazz, request):
    """Returns a JSON objcet with all item of a clazz. The list does not
    have any capabilities for sorting or filtering

    :clazz: Class of items to list
    :request: Current request.
    :returns: JSON object.

    """
    listing = clazz.get_item_list(request)
    return JSONResponse(True, listing)

def read__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return read_(clazz, request)

def read_(clazz, request, callback=None):
    """Returns a JSON object of a specific item of type clazz. The
    loaded item is determined by the id provided in the matchdict object
    of the current request.

    :clazz: Class of item to load
    :request: Current request
    :callback: Current function which is called after the item has been read.
    :returns: JSON object.
    """
    item = get_item_from_request(request)
    if callback is not None:
        item = callback(request, item)
    return JSONResponse(True, item)

def delete__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missdeleteing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return delete_(clazz, request)

def delete_(clazz, request):
    """Deletes an item of type clazz. The item is deleted based on the
    unique id value provided in the matchtict object in the current
    DELETE request. The data will be deleted without any futher confirmation!

    :clazz: Class of item to delete
    :request: Current request
    :returns: JSON object.
    """
    item = get_item_from_request(request)
    request.db.delete(item)
    return JSONResponse(True, item)

action_view_mapping = {
    "list": list__,
    "create": rest_create,
    "read": read__,
    "update": rest_update,
    "delete": delete__,
}
