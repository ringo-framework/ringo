from pyramid.events import BeforeRender

import ringo.lib.security as security
import ringo.lib.helpers as helpers
from ringo.lib.form import (
    formbar_js_filenames,
    formbar_css_filenames
)
from ringo.lib.renderer.form import add_renderers
from ringo.lib.renderer.dialogs import (
    DialogRenderer,
    ConfirmDialogRenderer,
    ErrorDialogRenderer,
    WarningDialogRenderer,
    InfoDialogRenderer,
    ExportDialogRenderer,
    ImportDialogRenderer
)
from ringo.lib.renderer.lists import (
    ListRenderer,
    DTListRenderer
)

def setup_render_globals(config):
    config.add_subscriber(add_renderer_globals, BeforeRender)


def add_renderer_globals(event):
    request = event['request']
    event['h'] = helpers
    event['s'] = security
    event['_'] = request.translate
    event['N_'] = request.translate
    event['formbar_css_filenames'] = formbar_css_filenames
    event['formbar_js_filenames'] = formbar_js_filenames
    event['localizer'] = request.localizer
