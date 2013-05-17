from pyramid.view import view_config


@view_config(route_name='home', renderer='/index.mako')
def index_view(request):
    return {}
