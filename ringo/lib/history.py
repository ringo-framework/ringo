import urlparse
import re

DOWNLOAD_URL = re.compile(".*\/download\/[0-9]+")
STATIC_URL = re.compile("\/\w+-static\/.*")
SET_CURRENT_FORM = re.compile("\/set_current_form_page.*")


def handle_history(event):
    request = event.request
    history = request.ringo.history
    history.push(request)
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
        """

        url = request.url

        # normalize the URL by removing scheme and netloc. This avoids
        # problems with the URLs when running ringo behind reverse
        # proxies.
        split = urlparse.urlsplit(url)
        normalized_url = urlparse.urlunsplit(("", "") + split[2:])

        # Ignore Download URLs
        if (DOWNLOAD_URL.match(normalized_url) or
           STATIC_URL.match(normalized_url) or
           SET_CURRENT_FORM.match(normalized_url)):
            return

        # Ignore URL defined from settings if configured
        for ignore in request.registry.settings.get("app.history.ignore", "").split(","):
            if normalized_url.startswith(ignore):
                return

        if not self.history or normalized_url != self.history[-1]:
            self.history.append(normalized_url)
        if len(self.history) > 5:
            del self.history[0]
        return True

    def pop(self, num=1):
        """Returns a url form the history and deletes the item and all
        decendants from the history. On default it will return the last
        recent entry in the history. Optionally you can provide a number
        to the pop method to get e.g the 2 most recent entry."""
        url = None
        for x in range(num):
            if len(self.history) > 0:
                url = self.history.pop()
        return url

    def last(self):
        """Returns the last element from the history stack without
        removing it"""
        if len(self.history) > 0:
            return self.history[-1]
        return None
