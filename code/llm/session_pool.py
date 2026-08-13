class SessionPool:
    def __init__(self):
        self.sessions = {}
        self.active = None

    def get(self, provider, model):
        return self.sessions.get((provider, model))

    def register(self, provider, model, session):
        self.sessions[(provider, model)] = session

    def activate(self, provider, model):
        self.active = (provider, model)
        return self.sessions[(provider, model)]