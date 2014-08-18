"""
Modul for a simple RESTfull Interface to basic CRUD operations on the
items
"""
from formbar.form import Form

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

def create__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return create_(clazz, request)

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

def update__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return update_(clazz, request)

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
    item = get_item_from_request(request)
    form = Form(item.get_form_config('update'),
                item, request.db, translate=request.translate,
                csrf_token=request.session.get_csrf_token())
    if form.validate(request.params):
            sitem = form.save()
            return JSONResponse(True, sitem)
    else:
        # Validation fails! return item
        return JSONResponse(False, item)

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
    "create": create__,
    "read": read__,
    "update": update__,
    "delete": delete__,
}
