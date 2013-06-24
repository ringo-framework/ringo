from pyramid.view import forbidden_view_config
from pyramid.view import notfound_view_config

from ringo.lib.renderer import ErrorDialogRenderer


@notfound_view_config(renderer='/default/error.mako')
def notfound_get(request):
    _ = request.translate
    title = _("Error 404")
    body = _("Sorry, the requested ressource could not be found!")
    renderer = ErrorDialogRenderer(request, title=title, body=body)
    rvalue = {}
    rvalue['dialog'] = renderer.render()
    request.response_status = '404 Not Found'
    return rvalue


@forbidden_view_config(renderer='/default/error.mako')
def forbidden(request):
    _ = request.translate
    title = _("Error 403")
    body = _("Authorisation error! Sorry, you are not allowed"
             " to access to requested ressource!")
    renderer = ErrorDialogRenderer(request, title=title, body=body)
    rvalue = {}
    rvalue['dialog'] = renderer.render()
    request.response_status = '403 Forbidden'
    return rvalue
