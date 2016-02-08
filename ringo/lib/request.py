from pyramid.events import NewRequest
from pyramid.decorator import reify

class RingoRequest(object):

    """Ringo specific functions and properties directly attached to the
    request object."""

    def __init__(self, request):
        self.request = request

    @reify
    def feature(self):
        """Cached property to the FeatureToggle configuration."""
        return FeatureToggle(self.request.registry.settings)

class FeatureToggle(object):

    """FeatureToggle will give access to the configuration of feature
    toggle configuration in the config file. Feature can be configured
    usind *feature.name* config variables in the ini file. 

    To enable a feature you the feature must be set to *true* Any other
    value will evaluate to False which means the feature is not
    enabled."""

    def __init__(self, settings):
        self.settings = settings

    def __getattr__(self, name):
        return self.settings.get("feature.%s" % name) == "true"

def includeme(config):
    config.add_subscriber(add_ringo_request, NewRequest)

def add_ringo_request(event):
    event.request.ringo = RingoRequest(event.request)
