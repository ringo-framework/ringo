#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ringo.lib.request.helpers import decode_values


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
    return request.GET.get('addrelation')


#def handle_params(request):
#    """Handles varios sytem GET params comming with the request
#    Known params are:
#
#     * backurl: A url which should be called instead of the default
#       action after the next request succeeds. The backurl will be saved
#       in the session and stays there until it is deleted on a
#       successfull request. So take care to delete it to not mess up
#       with the application logic.
#     * form: The name of a alternative form configuration which is
#       used for the request.
#     * values: A comma separated list of key/value pair. Key and value
#       are separated with an ":"
#     * addrelation: A ":" separated string 'relation:class:id' to identify that
#       a item with id should be linked to the relation of this item.
#    """
#    clazz = request.context.__model__
#    params = {}
#    backurl = request.GET.get('backurl')
#    if backurl:
#        request.session['%s.backurl' % clazz] = backurl
#        params['backurl'] = backurl
#    values = request.GET.get('values')
#    if values:
#        params['values'] = {}
#        values = decode_values(values)
#        for key in values:
#            params['values'][key] = values[key]
#    form = request.GET.get('form')
#    if form:
#        params['form'] = form
#    relation = request.GET.get('addrelation')
#    if relation:
#        request.session['%s.addrelation' % clazz] = relation
#        params['addrelation'] = relation
#    request.session.save()
#    return params
