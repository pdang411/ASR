class ResourceManager:
    def __init__(self):
        self.resources=[]

    def register(self, resource):
        self.resources.append(resource)

    def close_all(self):
        for r in reversed(self.resources):
            try:
                r.close()
            except Exception:
                pass