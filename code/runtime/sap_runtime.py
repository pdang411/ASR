from __future__ import annotations

import asyncio
import threading

from runtime.provider_manager import ProviderManager
from runtime.reasoning_registry import ReasoningRegistry
from runtime.smart_active_polling_status import build_polling_status, build_status
from runtime.smart_active_polling import SmartActivePolling


class SAPRuntime:
    def __init__(self, providers=None, runtime_registry=None):
        self._providers = list(providers or [])
        self.manager = ProviderManager(self._providers)
        self.registry = ReasoningRegistry()
        self.runtime_registry = runtime_registry
        self.poller = SmartActivePolling(
            self.manager,
            self.registry,
            interval_seconds=30,
            idle_keep_alive_seconds=60,
            on_provider_state=self._provider_state_changed,
        )
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def providers(self):
        return self.manager.providers()

    def set_providers(self, providers):
        with self._lock:
            self._providers = list(providers)
            self.manager._providers = self._providers

    def add_provider(self, provider):
        with self._lock:
            self._providers.append(provider)
            self.manager._providers = self._providers

    async def prime(self):
        await self.manager.startup()
        await self.poller.poll_cycle()

    async def startup(self):
        await self.manager.startup()
        await self.poller.poll_cycle()
        await self.poller.start()
        while self.poller.running:
            await asyncio.sleep(0.2)

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def _run(self):
        asyncio.run(self.startup())

    async def _provider_state_changed(self, provider_state):
        self.registry.update(provider_state)
        if self.runtime_registry is not None:
            self.runtime_registry.update_provider(provider_state)

    async def stop(self):
        await self.poller.stop()

    def join(self, timeout=None):
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)

    def snapshot(self):
        if self.runtime_registry is not None:
            return build_polling_status(self.runtime_registry, self.poller)

        return build_status(
            self.manager,
            sap_running=self.poller.running,
            model_poll_interval_seconds=self.poller.interval_seconds,
        )