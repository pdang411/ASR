from __future__ import annotations

import inspect
import time
from typing import Any

from monitoring import Metrics


class RuntimeIntegration:
    def __init__(self, components: dict[str, Any] | None = None, metrics: Metrics | None = None):
        self.components = components or {}
        self.metrics = metrics or Metrics()
        self.initialized = False

    async def initialize(self):
        started = time.perf_counter()
        results = {}

        for name, component in self.components.items():
            init_fn = getattr(component, "initialize", None)
            if callable(init_fn):
                value = init_fn()
                if inspect.isawaitable(value):
                    value = await value
                results[name] = value
            else:
                results[name] = {"initialized": False, "reason": "no_initialize_method"}

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        self.metrics.record("runtime.initialize.ms", elapsed_ms)
        self.metrics.record("runtime.components", len(self.components))
        self.initialized = True

        return {
            "initialized": True,
            "components": results,
            "duration_ms": elapsed_ms,
        }