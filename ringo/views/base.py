import logging
from ringo.views.crud.create import (
    create_,
    create__
)
from ringo.views.crud.list_ import (
    bundle_,
    list_,
    list__
)
from ringo.views.crud.read import (
    read_,
    read__
)
from ringo.views.crud.update import (
    update_,
    update__
)
from ringo.views.crud.delete import (
    delete_,
    delete__,
    _handle_delete_request
)
from ringo.views.crud.export import (
    export_,
    export__,
    _handle_export_request
)
from ringo.views.crud.import_ import (
    import_,
    import__
)
from ringo.views.crud.print_ import (
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

log = logging.getLogger(__name__)


action_view_mapping = {
    "list": list__,
    "create": create__,
    "read": read__,
    "update": update__,
    "delete": delete__,
    "import": import__,
    "export": export__,
    "print":  print_,
}
