def parse_setting(name, settings, default=None):
    value = settings.get(name) if settings.get(name, None) else default
    if value and not isinstance(value, list):
        values = []
        for v in value.split(" "):
            values.append("'%s'" % v)
        return values
    else:
        return value


def build_csp_policy(settings):
    # TODO: Remove "unsafe-inline" default here. Change Ringo in the way
    # that it does not contain inline javascript! (ti) <2015-06-03 17:10>
    config = {
        'default-src': parse_setting('security.csp.default_src', settings,
                                     ["'self'"]),
        'script-src': parse_setting('security.csp.script_src',
                                    settings,
                                    ["'self'", "'unsafe-inline'"]),
        'object-src': parse_setting('security.csp.object_src', settings),
        'style-src': parse_setting('security.csp.style_src',
                                   settings,
                                   ["'self'", "'unsafe-inline'"]),
        'img-src': parse_setting('security.csp.img_src', settings),
        'media-src': parse_setting('security.csp.media_src', settings),
        'frame-src': parse_setting('security.csp.frame_src', settings),
        'frame-ancestors': parse_setting('security.csp.frame_ancestors',
                                         settings,
                                         ["'none'"]),
        'font-src': parse_setting('security.csp.font_src', settings),
        'connect-src': parse_setting('security.csp.connect_src', settings),
        'sandbox': parse_setting('security.csp.sandbox', settings),
    }
    policy = ['{0} {1}'.format(k, ' '.join(v)) for (k, v) in
              config.iteritems() if v]
    if settings.get('csp.report_uri', None):
        policy.append('report-uri {0}'.format(settings.get('csp.report_uri')))
    return '; '.join(policy)


def csp_factory(handler, registry):
    def csp_tween(request):
        settings, response = registry.settings, request.response
        HEADERS = ['Content-Security-Policy', 'X-WebKit-CSP']

        prefixes = settings.get('csp.exclude_prefixes', ('/admin'))
        if request.path.startswith(prefixes):
            return handler(request)
        if response.headers.get(HEADERS[0], None) is None:
            policy = build_csp_policy(settings)
            for HEADER in HEADERS:
                response.headers[HEADER] = policy
        return handler(request)
    return csp_tween
