class History:

    def __init__(self, history):
        self.history = history

    def push(self, url):
        self.history.append(url)

    def pop(self):
        if len(self.history) > 0:
            return self.history.pop()
        return None
