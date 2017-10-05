import urlparse
import re

DOWNLOAD_URL = re.compile(".*\/download\/[0-9]+")
STATIC_URL = re.compile(".*\/\w+-static\/.*")
SET_CURRENT_FORM = re.compile(".*\/set_current_form_page.*")
REST_URLS = re.compile(".*\/rest\/.*")
FAVICON = re.compile(".*\/favicon\.ico")


def handle_history(event):
    """Is called per subscriber on NewResponse event."""
    request = event.request
    history = request.ringo.history
    history.push(request)
    request.session["history"] = history
    request.session.save()


class History:

    def __init__(self, history):
        self.history = history

    def push(self, request):
        """Adds an url to the history if the url is not already the most
        recent entry. The scheme and network location (host, port,
        username, password), if present, are removed from the URL before
        storing it. If there are more than 5 entries in the list the
        oldes entry will be removed.

        Please note, that the most recent entry in the history is always
        the url of the current request. This is because the history is
        is filled at the very beginnin of the request on the NewRequest
        event. It is **not** possible to handle the history at response
        time because the history can not be saved in the session. The
        reason for this is unknown.  Howwver this special behaviour is
        relevant if you want to access the history list directly for
        some reasone and not want to use the pop and last methods.
        """
        url = request.url

        # normalize the URL by removing scheme and netloc. This avoids
        # problems with the URLs when running ringo behind reverse
        # proxies.
        split = urlparse.urlsplit(url)
        normalized_url = urlparse.urlunsplit(("", "") + split[2:])

        # Ignore Download URLs and Favicon
        if (DOWNLOAD_URL.match(normalized_url) or
           STATIC_URL.match(normalized_url) or
           SET_CURRENT_FORM.match(normalized_url) or
           REST_URLS.match(normalized_url) or
           FAVICON.match(normalized_url)):
            return

        # Ignore URL defined from settings if configured
        for ignore in request.registry.settings.get("app.history.ignore", "").split(","):
            if ignore and normalized_url.startswith(ignore):
                return

        if not self.history or normalized_url != self.history[-1]:
            self.history.append(normalized_url)
        if len(self.history) > 10:
            del self.history[0]
        return True

    def pop(self, num=1):
        """Returns a url form the history and deletes the item and all
        decendants from the history. On default it will return the last
        recent entry in the history. Optionally you can provide a number
        to the pop method to get e.g the 2 most recent entry."""
        url = None
        current_url = None

        # Because the last entry in the history is always the url of the
        # current request we need to temporay pop the last entry to
        # to make the actually last entry available as last entry in the
        # history.
        if len(self.history) > 0:
            current_url = self.history.pop()

        for x in range(num):
            if len(self.history) > 0:
                url = self.history.pop()

        # Now readd the current entry to the history, because the
        # current entry will be needed to build the history.
        if current_url:
            self.history.append(current_url)
        return url

    def last(self):
        """Returns the last element from the history stack without
        removing it"""
        if len(self.history) > 1:
            # Because the last entry is always the current url we will
            # return the pre last url (-2)
            return self.history[-2]
        return None
