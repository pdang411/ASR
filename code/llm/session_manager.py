class SessionManager:
    def __init__(self, provider):
        self.provider = provider
        self.connected = False

    def connect(self):
        if not self.connected:
            self.provider.connect()
            self.connected = True

    def generate(self, request):
        self.connect()
        return self.provider.generate(request)

    def close(self):
        if self.connected:
            self.provider.disconnect()
            self.connected = False