from __future__ import annotations

import time


class ProviderHealth:
    def __init__(self):
        self.status = {}

    def update(self, name, ok, latency_ms):
        self.status[name] = {
            "healthy": bool(ok),
            "latency_ms": float(latency_ms),
            "last_seen": time.time(),
        }

    def snapshot(self):
        return {key: dict(value) for key, value in self.status.items()}