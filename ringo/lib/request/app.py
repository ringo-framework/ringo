from pyramid.events import NewRequest, ContextFound
from pyramid.decorator import reify

from ringo.lib.request.featuretoggle import FeatureToggle
from ringo.lib.request.params import Params, save_params_in_session
from ringo.lib.history import handle_history


class RingoRequest(object):

    """Ringo specific functions and properties directly attached to the
    request object."""

    def __init__(self, request):
        self.request = request


    @reify
    def feature(self):
        """Cached property to the FeatureToggle configuration."""
        return FeatureToggle(self.request.registry.settings)

    @reify
    def params(self):
        """Cached property to the Ringo GET params."""
        return Params(self.request)


def includeme(config):
    config.add_subscriber(add_ringo_request, NewRequest)
    config.add_subscriber(save_params_in_session, ContextFound)
    config.add_subscriber(handle_history, ContextFound)


def add_ringo_request(event):
    event.request.ringo = RingoRequest(event.request)
