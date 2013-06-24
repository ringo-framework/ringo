from ringo.lib.history import History


def handle_history(request):
    history = request.session.get('history')
    if history is None:
        history = History([])
    history.push(request.url)
    request.session['history'] = history
