class History:

    def __init__(self, history):
        self.history = history

    def push(self, url):
        """Adds an url to the history if the url is not already the most
        recent entry. If there are more than 10 entries in the list the
        oldes entry will be removed."""
        if url != self.history[-1]:
            self.history.append(url)
        if len(self.history) > 10:
            del self.history[0]
        print self.history

    def pop(self):
        if len(self.history) > 0:
            return self.history.pop()
        return None
