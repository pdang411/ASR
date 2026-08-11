class ReasoningRegistry:

    def __init__(self):
        self.providers = {}

    def refresh(self, providers):
        self.providers = {
            p.state.provider_id: p.snapshot()
            for p in providers
        }

    def ready(self):
        return [
            p for p in self.providers.values()
            if p["status"] == "READY"
        ]