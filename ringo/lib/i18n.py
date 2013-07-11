import json
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.i18n import get_localizer, TranslationStringFactory

translators = []
translators.append(TranslationStringFactory('ringo'))
"""The translators variable holds a list of available
TranslationStringFactory. Usually there is one factory per i18n domain
which needs to be translated. On translation the availabe translation
strings will be iterated until one of them returns a translated string.
On default there is only on factory for ringo available, but derived
applications can append their own translation factory."""


@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(string, default=None, mapping={}):
        """The translation function will iterate over the available
        TranslationStringFactorys in the translators varibale and try to
        translate the given string. TranslationsStrings will be iterated
        in reversed order and iteration stops as soon as the
        TranslationsString returns a string different from the given
        string (msgid)"""
        for _ in translators[::-1]:
            ts = localizer.translate(_(string,
                                       default=default,
                                       mapping=mapping))
            if ts != string:
                break
        return ts

    request.localizer = localizer
    request.translate = auto_translate


def locale_negotiator(request):
    accepted = request.accept_language
    return accepted.best_match(('en', 'fr', 'de'), 'en')


def extract_i18n_tableconfig(fileobj, keywords, comment_tags, options):
    """Extract messages from JSON table configuration files.
    :param fileobj: the file-like object the messages should be extracted
                    from
    :param keywords: a list of keywords (i.e. function names) that should
                     be recognized as translation functions
    :param comment_tags: a list of translator tags to search for and
                         include in the results
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """
    config = json.load(fileobj)
    # FIXME: Fix linenumbering. No real linenummer, just iterate somehow
    lineno = 0
    for key, tc in config.iteritems():
        lineno += 1
        for col in tc.get('columns'):
            lineno += 1
            # "_" is one of the default keywords which marks a string
            # for extraction. As the json file does not have any
            # keywords. Set a dummy funcname here.
            yield (lineno,
                   "_",
                   col.get('label'),
                   ["Label for %s column in %s table config"
                    % (col.get('name'), key)])

#@subscriber(NewRequest)
#def setAcceptedLanguagesLocale(event):
#    request = event.request
#    if not request.accept_language:
#        return
#    event.request._LOCALE_ = locale_negotiator(event.request)
