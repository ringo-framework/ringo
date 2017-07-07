#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ringo.lib.request.helpers import decode_values


def save_params_in_session(event):
    """Method to save selected params of the request in the session.
    This method can only be called after the context is found."""
    request = event.request
    if hasattr(request.context, "__model__"):
        clazz = request.context.__model__
        params = request.ringo.params
        if params.backurl:
            request.session['%s.backurl' % clazz] = params.backurl
        if params.addrelation:
            request.session['%s.addrelation' % clazz] = params.addrelation
        request.session.save()


def get_backurl(request):
    return request.GET.get('backurl')


def get_values(request):
    values = request.GET.get('values', {})
    if values:
        values = decode_values(values)
        return values
    else:
        return {}


def get_form(request):
    return request.GET.get('form')


def get_relation(request):
    return request.params.get('addrelation')


def is_confirmed(request):
    """Returns True id the request is confirmed"""
    return request.params.get('confirmed') == "1"


class Params(object):

    """Class for Ringo specific GET params"""

    def __init__(self, request):
        self.request = request

    @property
    def values(self):
        """Return a dictionary generated from a A comma separated list
        of key/value pairs in the GET parameter. Key and value
        are separated with an ':'"""
        return get_values(self.request)

    @property
    def backurl(self):
        """backurl: A url which should be called instead of the default
        action after the next request succeeds. The backurl will be
        saved in the session and stays there until it is deleted on a
        successfull request. So take care to delete it to not mess up"""
        return get_backurl(self.request)

    @property
    def form(self):
        """form: The name of a alternative form configuration which is
        used for the request."""
        return get_form(self.request)

    @property
    def addrelation(self):
        """addrelation: A ":" separated string 'relation:class:id' to
        identify that a item with id should be linked to the relation of
        this item."""
        return get_relation(self.request)

    @property
    def confirmed(self):
        """confirmed: Boolean flag if the request is confirmed. E.g on
        delete requests."""
        return is_confirmed(self.request)
