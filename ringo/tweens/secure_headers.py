def secure_headers_factory(handler, registry):
    def secure_headers_tween(request):
        response = request.response
        # Just modify this dict to inject new headers
        HEADERS = {
            'X-XSS-Protection': '1; mode=block',
            'X-Content-Type-Options': 'nosniff'
        }
        for header in HEADERS:
            if not response.headers.get(header, None):
                response.headers[header] = HEADERS[header]
        return handler(request)
    return secure_headers_tween
