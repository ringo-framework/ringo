class History:

    def __init__(self, history):
        self.history = history

    def push(self, url):
        self.history.append(url)

    def pop(self):
        return self.history.pop()
