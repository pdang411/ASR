from dataclasses import dataclass, field
from time import monotonic

@dataclass(slots=True)
class ProviderState:
    provider_id: str
    endpoint: str

    status: str = "READY"

    available_models: list[str] = field(default_factory=list)
    loaded_model: str | None = None

    queue_depth: int = 0
    active_requests: int = 0

    avg_latency_ms: float = 0.0
    avg_tokens_per_sec: float = 0.0
    success_rate: float = 1.0

    provider_score: float = 0.0

    last_health: float = 0.0
    last_model_scan: float = 0.0
    last_request: float = 0.0

    discovery_required: bool = True

    def health_stale(self, now):
        return now - self.last_health >= 30

    def should_warm(self, now, idle_seconds=120):
        return (
            self.active_requests == 0 and
            self.loaded_model is not None and
            (now - self.last_request) >= idle_seconds
        )