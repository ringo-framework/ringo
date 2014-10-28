from ringo.views.base.create import (
    create,
    rest_create
)
from ringo.views.base.list_ import (
    list_,
    bundle_,
    rest_list
)
from ringo.views.base.read import (
    read,
    rest_read
)
from ringo.views.base.update import (
    update,
    rest_update
)
from ringo.views.base.delete import (
    delete,
    rest_delete,
)
from ringo.views.base.export import (
    export,
)
from ringo.views.base.import_ import (
    import_,
)
from ringo.views.base.print_ import (
    print_
)

web_action_view_mapping = {
    "list": list_,
    "create": create,
    "read": read,
    "update": update,
    "delete": delete,
    "import": import_,
    "export": export,
    "print":  print_,
    "bundle": bundle_,
}

rest_action_view_mapping = {
    "list": rest_list,
    "create": rest_create,
    "read": rest_read,
    "update": rest_update,
    "delete": rest_delete,
}


def set_web_action_view(key, view):
    web_action_view_mapping[key] = view


def set_rest_action_view(key, view):
    rest_action_view_mapping[key] = view
