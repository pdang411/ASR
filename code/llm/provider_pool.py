class ProviderPool:
    def __init__(self):
        self.providers = {}

    def register(self, name, provider):
        self.providers[name] = provider

    def get(self, name):
        return self.providers[name]

    def snapshot(self):
        return sorted(self.providers.keys())