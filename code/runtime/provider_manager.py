import asyncio

class ProviderManager:

    def __init__(self, providers):
        self._providers = providers

    async def startup(self):
        await asyncio.gather(*(p.connect() for p in self._providers))
        await asyncio.gather(*(p.query_models() for p in self._providers))
        await asyncio.gather(*(p.query_loaded_model() for p in self._providers))

    def providers(self):
        return self._providers

    def next_interval(self):
        if any(p.state.active_requests for p in self._providers):
            return 30
        if any(p.state.status != "READY" for p in self._providers):
            return 30
        return 60