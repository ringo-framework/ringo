import urlparse


class History:

    def __init__(self, history):
        self.history = history

    def push(self, url):
        """Adds an url to the history if the url is not already the most
        recent entry. The scheme and network location (host, port,
        username, password), if present, are removed from the URL before
        storing it. If there are more than 5 entries in the list the
        oldes entry will be removed.
        """

        # normalize the URL by removing scheme and netloc. This avoids
        # problems with the URLs when running ringo behind reverse
        # proxies.
        split = urlparse.urlsplit(url)
        normalized_url = urlparse.urlunsplit(("", "") + split[2:])

        if not self.history or normalized_url != self.history[-1]:
            self.history.append(normalized_url)
        if len(self.history) > 5:
            del self.history[0]

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
