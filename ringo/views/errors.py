from pyramid.view import forbidden_view_config
from pyramid.view import notfound_view_config
from pyramid.response import Response

from ringo.lib.renderer import ErrorDialogRenderer


@forbidden_view_config(path_info='/rest')
def rest_forbidden(request):
    body = '{"success": false, "params": {"error": 403}}'
    response = Response(body=body, content_type='application/json')
    response.status = '403 Forbidden'
    return response


@notfound_view_config(path_info='/rest')
def rest_notfound(request):
    body = '{"success": false, "params": {"error": 404}}'
    response = Response(body=body, content_type='application/json')
    response.status = '404 Not Found'
    return response


@notfound_view_config(renderer='/default/error.mako')
def notfound_get(request):
    _ = request.translate
    title = _("Error 404")
    body = _("Sorry, the requested ressource could not be found!")
    renderer = ErrorDialogRenderer(request, title=title, body=body)
    rvalue = {}
    rvalue['dialog'] = renderer.render()
    request.response.status = 404
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
    request.response.status = 403
    return rvalue
