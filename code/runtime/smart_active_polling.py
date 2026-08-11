import asyncio
from time import monotonic

class SmartActivePolling:

    def __init__(self, manager, registry):
        self.manager = manager
        self.registry = registry
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            await self.poll_cycle()
            await asyncio.sleep(self.manager.next_interval())

    async def poll_cycle(self):
        now = monotonic()
        jobs = []

        for provider in self.manager.providers():
            state = provider.state

            if state.should_scan_models():
                jobs.append(provider.query_models())

            jobs.append(provider.query_loaded_model())

            if state.health_stale(now):
                jobs.append(provider.refresh_health())

            if state.should_warm(now):
                jobs.append(provider.keep_alive())

            if state.active_requests == 0:
                jobs.append(provider.benchmark())

        if jobs:
            await asyncio.gather(*jobs)

        self.registry.refresh(self.manager.providers())

    async def stop(self):
        self.running = False