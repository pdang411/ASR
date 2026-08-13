import asyncio


class ProviderManager:
    def __init__(self, providers):
        self._providers = list(providers)

    async def startup(self):
        await asyncio.gather(
            *(provider.connect() for provider in self._providers),
            return_exceptions=True,
        )

    def providers(self):
        return self._providers

    def next_interval(self) -> int:
        return 30
