from ringo.views.base.create import (
    create,
    rest_create,
)

from ringo.views.base.list_ import (
    bundle_,
    list_,
    rest_list,
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
    _handle_delete_request
)
from ringo.views.base.export import (
    export_,
    export__,
    _handle_export_request
)
from ringo.views.base.import_ import (
    import_,
    import__
)
from ringo.views.base.print_ import (
    print_,
)
from ringo.views.forms import (
    get_ownership_form,
    get_logbook_form
)
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_event,
    is_confirmed,
    get_item_from_request,
    get_current_form_page
)

web_action_view_mapping = {
    "list": list_,
    "create": create,
    "read": read,
    "update": update,
    "delete": delete,
    "import": import__,
    "export": export__,
    "print":  print_,
}

rest_action_view_mapping = {
    "list": rest_list,
    "create": rest_create,
    "read": rest_read,
    "update": rest_update,
    "delete": rest_delete,
}
