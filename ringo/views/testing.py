from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


@view_config(route_name='start_test_case')
def begin(request):
    if request.params.get("_testcase"):
        history = request.session['history']
        url = history.pop()
    else:
        url = request.route_path("start_test_case",
                                 _query={"_testcase": "begin"})
    return HTTPFound(url)


@view_config(route_name='stop_test_case')
def end(request):
    if request.params.get("_testcase"):
        history = request.session['history']
        url = history.pop()
    else:
        url = request.route_path("stop_test_case",
                                 _query={"_testcase": "end"})
    return HTTPFound(url)
