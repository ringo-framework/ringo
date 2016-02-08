from pyramid.events import NewRequest
from pyramid.decorator import reify

class RingoRequest(object):

    """Ringo specific functions and properties directly attached to the
    request object."""

    def __init__(self, request):
        self.request = request

def includeme(config):
    config.add_subscriber(add_ringo_request, NewRequest)

def add_ringo_request(event):
    event.request.ringo = RingoRequest(event.request)
