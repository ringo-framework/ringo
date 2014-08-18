"""
Modul for a simple RESTfull Interface to basic CRUD operations on the
items
"""
from formbar.form import Form

from ringo.views.base import rest_create, rest_update, rest_read, rest_delete
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

action_view_mapping = {
    "list": list__,
    "create": rest_create,
    "read": rest_read,
    "update": rest_update,
    "delete": rest_delete,
}
