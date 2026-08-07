class SharedContext(dict):
    def merge(self, key, value):
        self[key] = value