class History:

    def __init__(self, history):
        self.history = history

    def push(self, url):
        """Adds an url to the history if the url is not already the most
        recent entry. If there are more than 10 entries in the list the
        oldes entry will be removed."""
        if not self.history or url != self.history[-1]:
            self.history.append(url)
        if len(self.history) > 10:
            del self.history[0]
        #print self.history

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
