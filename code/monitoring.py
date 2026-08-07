from __future__ import annotations

import time
from typing import Any


class Metrics:
    def __init__(self):
        self._samples: dict[str, list[dict[str, Any]]] = {}

    def record(self, name, value, tags=None):
        metric = str(name)
        self._samples.setdefault(metric, []).append(
            {
                "value": value,
                "timestamp": time.time(),
                "tags": tags if isinstance(tags, dict) else {},
            }
        )

    def increment(self, name, amount=1, tags=None):
        self.record(name, amount, tags=tags)

    def snapshot(self):
        summary = {}
        for name, values in self._samples.items():
            numeric = [entry["value"] for entry in values if isinstance(entry.get("value"), (int, float))]
            summary[name] = {
                "count": len(values),
                "last": values[-1]["value"] if values else None,
                "min": min(numeric) if numeric else None,
                "max": max(numeric) if numeric else None,
            }
        return summary