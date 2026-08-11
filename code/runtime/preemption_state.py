from dataclasses import dataclass, field
from time import monotonic


@dataclass(slots=True)
class PreemptionMetrics:
    active_demands: int = 0
    queued_demands: int = 0
    waiting_dependencies: int = 0

    cache_hits: int = 0
    cache_misses: int = 0
    ai_kb_reuses: int = 0
    reasoning_reuses: int = 0
    requests_merged: int = 0
    duplicate_work_avoided: int = 0

    llm_requests: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0

    decisions_total: int = 0
    retries: int = 0


@dataclass(slots=True)
class PreemptionState:
    status: str = "STARTING"
    mode: str = "DETERMINISTIC"
    hot_path: str = "STARTING"

    cycle_count: int = 0
    announcement_version: int = 0

    last_decision: str = "NONE"
    last_reason: str = ""
    last_task_id: str | None = None

    capabilities: dict[str, str] = field(default_factory=dict)
    metrics: PreemptionMetrics = field(default_factory=PreemptionMetrics)

    last_change: float = field(default_factory=monotonic)

    def mark_changed(self):
        self.announcement_version += 1
        self.last_change = monotonic()