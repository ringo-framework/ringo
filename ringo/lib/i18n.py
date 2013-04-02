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

@subscriber(NewRequest)
def setAcceptedLanguagesLocale(event):
    if not event.request.accept_language:
        return
    accepted = event.request.accept_language
    al = accepted.best_match(('en', 'fr', 'de'), 'en')
    event.request._LOCALE_ = al
