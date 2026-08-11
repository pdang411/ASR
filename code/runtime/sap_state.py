from dataclasses import dataclass, field
from time import monotonic


@dataclass(slots=True)
class SAPMetrics:
    poll_cycles: int = 0
    provider_queries: int = 0
    provider_query_failures: int = 0
    health_checks: int = 0
    health_failures: int = 0
    model_discoveries: int = 0
    model_discovery_failures: int = 0
    active_model_checks: int = 0
    keep_alive_requests: int = 0
    keep_alive_failures: int = 0
    state_changes: int = 0


@dataclass(slots=True)
class SAPState:
    status: str = "STARTING"
    mode: str = "ACTIVE_POLLING"
    hot_path: str = "OFF_HOT_PATH"

    poll_interval_seconds: int = 30
    idle_keep_alive_seconds: int = 60

    cycle_count: int = 0
    announcement_version: int = 0

    last_poll: float = 0.0
    last_change: float = field(default_factory=monotonic)

    capabilities: dict[str, str] = field(default_factory=dict)
    providers: dict[str, dict] = field(default_factory=dict)

    metrics: SAPMetrics = field(default_factory=SAPMetrics)

    def mark_changed(self):
        self.announcement_version += 1
        self.last_change = monotonic()
