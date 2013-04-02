from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.i18n import get_localizer, TranslationStringFactory

_ = TranslationStringFactory('ringo')


@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(string, default=None, mapping={}):
        return localizer.translate(_(string, default=default, mapping=mapping))

    request.localizer = localizer
    request.translate = auto_translate


def locale_negotiator(request):
    accepted = request.accept_language
    return accepted.best_match(('en', 'fr', 'de'), 'en')

#@subscriber(NewRequest)
#def setAcceptedLanguagesLocale(event):
#    request = event.request
#    if not request.accept_language:
#        return
#    event.request._LOCALE_ = locale_negotiator(event.request)
