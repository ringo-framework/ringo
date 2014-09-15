def clickjacking_factory(handler, registry):
    def clickjacking_tween(request):
        settings, response = registry.settings, request.response
        HEADER = 'X-Frame-Options'
        if not response.headers.get(HEADER, None):
            option = settings.get('x_frame_options', 'SAMEORIGIN').upper()
            response.headers[HEADER] = option
        return handler(request)
    return clickjacking_tween
