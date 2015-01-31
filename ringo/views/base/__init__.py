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

web_action_view_mapping = {
    "default": {
        "list": list_,
        "create": create,
        "read": read,
        "update": update,
        "delete": delete,
        "import": import_,
        "export": export,
        "bundle": bundle_,
    }
}

rest_action_view_mapping = {
    "default": {
        "list": rest_list,
        "create": rest_create,
        "read": rest_read,
        "update": rest_update,
        "delete": rest_delete,
    }
}

def get_action_view(mapping, action, module):
    if module in mapping:
        views = mapping[module]
        if action in views:
            return views[action]
    return mapping["default"].get(action)


def set_web_action_view(key, view, module="default"):
    if module in web_action_view_mapping:
        mod_actions = web_action_view_mapping.get(module)
    else:
        web_action_view_mapping[module] = {}
        mod_actions = web_action_view_mapping.get(module)
    mod_actions[key] = view
    web_action_view_mapping[module] = mod_actions


def set_rest_action_view(key, view, module="default"):
    if module in rest_action_view_mapping:
        mod_actions = rest_action_view_mapping.get(module)
    else:
        rest_action_view_mapping[module] = {}
        mod_actions = rest_action_view_mapping.get(module)
    mod_actions[key] = view
    rest_action_view_mapping[module] = mod_actions
