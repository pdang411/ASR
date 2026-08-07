class ProviderHealth:
    def __init__(self):
        self.status={}

    def update(self,name,latency_ms,healthy):
        self.status[name]={
            "latency":latency_ms,
            "healthy":healthy
        }

    def get_status(self, name):
        return self.status.get(name, None)

    def get_all_status(self):
        return self.status

    def is_healthy(self, name):
        status = self.get_status(name)
        return status.get("healthy", True) if status else True