import asyncio
from time import monotonic

from runtime.sap_capabilities import SMART_ACTIVE_POLLING_CAPABILITIES
from runtime.sap_flash import SAPFlash
from runtime.sap_state import SAPState


class SmartActivePolling:
    def __init__(
        self,
        manager,
        registry=None,
        interval_seconds=30,
        idle_keep_alive_seconds=60,
        on_provider_state=None,
    ):
        self.manager = manager
        self.registry = registry
        self.interval_seconds = max(5, int(interval_seconds))
        self.idle_keep_alive_seconds = max(self.interval_seconds, int(idle_keep_alive_seconds))
        self.state = SAPState(
            poll_interval_seconds=self.interval_seconds,
            idle_keep_alive_seconds=self.idle_keep_alive_seconds,
        )
        self.state.capabilities = dict(SMART_ACTIVE_POLLING_CAPABILITIES)
        self.flash = SAPFlash(self.state)
        self._cached_flash = ""
        self.on_provider_state = on_provider_state
        self.running = False
        self._task = None

    @property
    def capabilities(self):
        return dict(self.state.capabilities)

    @property
    def providers(self):
        return list(self.state.providers.values())

    async def initialize(self):
        self.state.status = "READY"
        self.state.hot_path = "OFF_HOT_PATH"
        self.state.mark_changed()
        self._refresh_flash()

    def _refresh_flash(self):
        self._cached_flash = self.flash.build()

    async def start(self):
        if self.running:
            return

        await self.initialize()

        self.running = True
        self.state.status = "RUNNING"
        self.state.mark_changed()
        self._refresh_flash()
        self._task = asyncio.create_task(self._loop())

    async def _loop(self):
        # Query immediately at startup.
        await self.poll_cycle()

        while self.running:
            await asyncio.sleep(self.interval_seconds)
            if not self.running:
                break

            try:
                await self.poll_cycle()
            except asyncio.CancelledError:
                raise
            except Exception:
                # Polling must never terminate the ASR Runtime.
                pass

    async def poll_cycle(self):
        self.state.cycle_count += 1
        self.state.metrics.poll_cycles += 1
        self.state.last_poll = monotonic()
        before = self._provider_snapshot()

        await asyncio.gather(
            *(self._poll_provider(provider) for provider in self.manager.providers()),
            return_exceptions=True,
        )

        after = self._provider_snapshot()
        if after != before:
            self.state.metrics.state_changes += 1
            self.state.mark_changed()
            self._refresh_flash()

        if self.registry is not None:
            self.registry.refresh(self.manager.providers())

    async def _publish(self, provider):
        if self.on_provider_state is None:
            return

        result = self.on_provider_state(provider.state)
        if hasattr(result, "__await__"):
            await result

    async def _poll_provider(self, provider):
        state = provider.state
        now = monotonic()

        # Never interfere with active inference.
        if state.active_requests:
            return

        if state.health_stale(now, self.interval_seconds):
            try:
                self.state.metrics.health_checks += 1
                await provider.refresh_health()
            except Exception:
                self.state.metrics.health_failures += 1
                state.health_failures += 1

        if state.model_state_stale(now, self.interval_seconds):
            try:
                self.state.metrics.provider_queries += 1
                models = await provider.discover_models()
                state.models = list(models or [])
                state.last_model_query = monotonic()
                state.model_query_count += 1
                self.state.metrics.model_discoveries += 1
            except Exception:
                self.state.metrics.provider_query_failures += 1
                self.state.metrics.model_discovery_failures += 1
                state.model_query_failures += 1

        try:
            self.state.metrics.active_model_checks += 1
            state.active_model = await provider.active_model()
            state.last_active_model_query = monotonic()
        except Exception:
            pass

        if provider.idle():
            await self._keep_alive_if_due(provider)

        await self._publish_provider_state(provider)
        await self._publish(provider)

    async def _keep_alive_if_due(self, provider):
        state = provider.state
        now = monotonic()
        if state.last_keep_alive and (now - state.last_keep_alive) < self.idle_keep_alive_seconds:
            return

        try:
            self.state.metrics.keep_alive_requests += 1
            await provider.keep_alive()
            state.last_keep_alive = monotonic()
        except Exception:
            self.state.metrics.keep_alive_failures += 1
            pass

    async def _publish_provider_state(self, provider):
        state = provider.state
        self.state.providers[state.provider_id] = {
            "provider_id": state.provider_id,
            "endpoint": state.endpoint,
            "status": state.status,
            "models": list(state.models),
            "active_model": state.active_model,
            "queue_depth": state.queue_depth,
            "avg_latency_ms": state.avg_latency_ms,
            "tokens_per_sec": state.avg_tokens_per_sec,
            "success_rate": state.success_rate,
            "last_health": state.last_health,
            "last_model_query": state.last_model_query,
            "model_query_count": state.model_query_count,
            "model_query_failures": state.model_query_failures,
        }

    def _provider_snapshot(self):
        return tuple(
            (
                p.state.provider_id,
                p.state.status,
                tuple(p.state.models),
                p.state.active_model,
                p.state.last_model_query,
                p.state.model_query_count,
                p.state.model_query_failures,
            )
            for p in self.manager.providers()
        )

    def status(self) -> dict:
        return {
            "sap_running": bool(self.running),
            "status": self.state.status,
            "mode": self.state.mode,
            "hot_path": self.state.hot_path,
            "poll_interval_seconds": self.interval_seconds,
            "model_poll_interval_seconds": self.interval_seconds,
            "idle_keep_alive_seconds": self.idle_keep_alive_seconds,
            "cycle_count": self.state.cycle_count,
            "announcement_version": self.state.announcement_version,
            "capabilities": dict(self.state.capabilities),
            "providers": list(self.state.providers.values()),
            "metrics": {
                "poll_cycles": self.state.metrics.poll_cycles,
                "provider_queries": self.state.metrics.provider_queries,
                "provider_query_failures": self.state.metrics.provider_query_failures,
                "health_checks": self.state.metrics.health_checks,
                "health_failures": self.state.metrics.health_failures,
                "model_discoveries": self.state.metrics.model_discoveries,
                "model_discovery_failures": self.state.metrics.model_discovery_failures,
                "active_model_checks": self.state.metrics.active_model_checks,
                "keep_alive_requests": self.state.metrics.keep_alive_requests,
                "keep_alive_failures": self.state.metrics.keep_alive_failures,
                "state_changes": self.state.metrics.state_changes,
            },
            "announcement": self._cached_flash,
        }

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        self.state.status = "STOPPED"
        self.state.mark_changed()
        self._refresh_flash()
