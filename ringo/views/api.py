"""The api modul include view functions which are some sort of helper
functions usually called by the client"""
import logging
from pyramid.response import Response
from pyramid.view import view_config

from formbar.form import Form
from formbar.config import Config, parse
from formbar.rules import Rule

from ringo.views.response import JSONResponse

log = logging.getLogger(__name__)


@view_config(route_name='get-language',
             renderer='json',
             request_method="GET")
def get_language(request):
    """Method return the preferred language of the user"""
    return JSONResponse(True, request._LOCALE_, {})


@view_config(route_name='rules-evaluate',
             renderer='json',
             request_method="GET")
def evaluate(request):
    """Method which will evaluate a formed rule given in the GET
    request. It will return a JSONResponse with the result of the
    evaluation."""
    try:
        ruleexpr = request.GET.get('rule').strip()
        rule = Rule(ruleexpr)
        result = rule.evaluate({})
        return JSONResponse(True, result, {"msg": rule.msg,
                                           "locale": request._LOCALE_})
    except:
        msg = "Can not evaluate rule '%s'" % ruleexpr
        log.error(msg)
        return JSONResponse(False, False, {"msg": msg,
                                           "headers": request._LOCALE_})


@view_config(route_name='form-render',
             renderer='json',
             request_method="POST")
def render(request):
    """Will return a JSONResponse with a rendererd form. The form
    defintion and the formid is provided in the POST request."""
    _ = request.translate
    form_config = request.POST.get("definition")
    config_name = request.POST.get("formid")
    out = []
    try:
        config = Config(parse(form_config))
        form_config = config.get_form(config_name)
        form = Form(form_config, None, request.db,
                    csrf_token=request.session.get_csrf_token())
        out.append(form.render(buttons=False, outline=False))
    except Exception as ex:
        out.append(_('ERROR: %s' % str(ex)))
    data = {"form": "".join(out)}
    return JSONResponse(True, data, {"msg": "Ole!"})


@view_config(route_name='set_current_form_page')
def set_current_form_page(request):
    """Will save the currently selected page of a form in the session.
    The request will have some attributes in the GET request which will
    config which page, of which item is currently shown. This function
    is used as a callback function within formbar.

    :request: Current request
    :returns: Response
    """
    page = request.GET.get('page')
    item = request.GET.get('item')
    itemid = request.GET.get('itemid')
    if page and item and itemid:
        #request.session['%s.form.page' % key] = page_id
        request.session['%s.%s.form.page' % (item, itemid)] = page
        request.session.save()
    return Response(body='OK', content_type='text/plain')
