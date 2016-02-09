from pyramid.events import NewRequest
from pyramid.decorator import reify

from ringo.lib.request.featuretoggle import FeatureToggle


class RingoRequest(object):

    """Ringo specific functions and properties directly attached to the
    request object."""

    def __init__(self, request):
        self.request = request

    @reify
    def feature(self):
        """Cached property to the FeatureToggle configuration."""
        return FeatureToggle(self.request.registry.settings)


def includeme(config):
    config.add_subscriber(add_ringo_request, NewRequest)


def add_ringo_request(event):
    event.request.ringo = RingoRequest(event.request)
