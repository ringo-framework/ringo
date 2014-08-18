"""
Modul for a simple RESTfull Interface to basic CRUD operations on the
items
"""
from formbar.form import Form

from ringo.views.base import rest_create, rest_update, rest_read, rest_delete, rest_list
from ringo.views.request import get_item_from_request
from ringo.views.response import JSONResponse


action_view_mapping = {
    "list": rest_list,
    "create": rest_create,
    "read": rest_read,
    "update": rest_update,
    "delete": rest_delete,
}
