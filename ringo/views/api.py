"""The api modul include view functions which are some sort of helper
functions usually called by the client"""
import logging
from pyramid.view import view_config

from formbar.form import Form
from formbar.config import Config, parse
from formbar.rules import Rule, Parser

from ringo.views.response import JSONResponse

log = logging.getLogger(__name__)


@view_config(route_name='rules-evaluate',
             renderer='json',
             request_method="GET")
def evaluate(request):
    """Method which will evaluate a formed rule given in the GET
    request. It will return a JSONResponse with the result of the
    evaluation."""
    try:
        ruleexpr = request.GET.get('rule')
        expr = Parser().parse(ruleexpr)
        rule = Rule(expr=expr)
        result = rule.evaluate({})
        return JSONResponse(True, result, {"msg": rule.msg})
    except:
        msg = "Can not evaluate rule '%s'" % ruleexpr
        log.error(msg)
        return JSONResponse(False, False, {"msg": msg})


@view_config(route_name='form-render',
             renderer='json',
             request_method="POST")
def render(request):
    """Will return a JSONResponse with a rendererd form. The form
    defintion and the formid is provided in the POST request."""
    form_config = request.POST.get("definition")
    config_name = request.POST.get("formid")
    config = Config(parse(form_config))
    out = []
    form_config = config.get_form(config_name)
    form = Form(form_config, None, request.db,
                csrf_token=request.session.get_csrf_token())
    out.append(form.render(buttons=False, outline=False))
    data = {"form": "".join(out)}
    return JSONResponse(True, data, {"msg": "Ole!"})
