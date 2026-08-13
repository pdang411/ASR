from dataclasses import dataclass, field
from time import monotonic


@dataclass(slots=True)
class ProviderState:
    provider_id: str
    endpoint: str
    status: str = "UNKNOWN"

    models: list[str] = field(default_factory=list)
    active_model: str | None = None
    capabilities: list[str] = field(default_factory=list)

    active_requests: int = 0
    queue_depth: int = 0

    avg_latency_ms: float = 0.0
    avg_tokens_per_sec: float = 0.0
    success_rate: float = 1.0
    provider_score: float = 0.0

    last_request: float = 0.0
    last_health: float = 0.0
    last_model_query: float = 0.0
    last_active_model_query: float = 0.0
    last_keep_alive: float = 0.0
    model_query_count: int = 0
    model_query_failures: int = 0
    health_failures: int = 0

    def health_stale(self, now: float, interval: int = 30) -> bool:
        return not self.last_health or (now - self.last_health) >= interval

    def model_state_stale(self, now: float, interval: int = 30) -> bool:
        return not self.last_model_query or (now - self.last_model_query) >= interval

    def idle(self) -> bool:
        return self.active_requests == 0

    # Backward-compatible aliases used by existing runtime code and tests.
    @property
    def available_models(self) -> list[str]:
        return self.models

    @available_models.setter
    def available_models(self, value):
        self.models = list(value or [])

    @property
    def loaded_model(self) -> str | None:
        return self.active_model

    @loaded_model.setter
    def loaded_model(self, value):
        self.active_model = value

    @property
    def last_model_scan(self) -> float:
        return self.last_model_query

    @last_model_scan.setter
    def last_model_scan(self, value):
        self.last_model_query = float(value or 0.0)

    @property
    def last_warm(self) -> float:
        return self.last_keep_alive

    @last_warm.setter
    def last_warm(self, value):
        self.last_keep_alive = float(value or 0.0)

    @property
    def discovery_required(self) -> bool:
        return True

    def should_scan_models(self) -> bool:
        return True

    def should_warm(self, now: float, idle_seconds: int = 120) -> bool:
        if not self.idle():
            return False
        if self.last_keep_alive and (now - self.last_keep_alive) < idle_seconds:
            return False
        return True
