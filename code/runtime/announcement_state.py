from dataclasses import dataclass, field
from time import monotonic


@dataclass(slots=True)
class MCPConnectionState:
    service_id: str
    endpoint: str
    status: str = "UNKNOWN"
    port: int | None = None
    last_heartbeat: float = 0.0
    tool_count: int = 0
    resource_count: int = 0
    prompt_count: int = 0

    def heartbeat_age(self) -> float:
        if not self.last_heartbeat:
            return float("inf")
        return monotonic() - self.last_heartbeat


@dataclass(slots=True)
class ToolState:
    service_id: str
    name: str
    capability: str
    description: str
    status: str = "READY"


@dataclass(slots=True)
class FeatureState:
    name: str
    status: str
    description: str = ""


@dataclass(slots=True)
class AgentState:
    agent_id: str
    status: str
    task_id: str | None = None
    progress: float = 0.0


@dataclass(slots=True)
class TaskState:
    task_id: str
    status: str
    agent_id: str | None = None
    progress: float = 0.0
    dependencies: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReasoningServiceState:
    provider: str
    model: str
    status: str
    queue_depth: int = 0
    avg_latency_ms: float = 0.0
    tokens_per_sec: float = 0.0


@dataclass(slots=True)
class RuntimeAnnouncementState:
    runtime_status: str = "STARTING"
    sap_running: bool = False
    smart_preemption_status: str = "UNKNOWN"
    ai_kb_status: str = "UNKNOWN"
    executor_registry_status: str = "UNKNOWN"

    providers: dict[str, dict] = field(default_factory=dict)
    mcp_connections: dict[str, MCPConnectionState] = field(default_factory=dict)
    tools: dict[str, ToolState] = field(default_factory=dict)
    features: dict[str, FeatureState] = field(default_factory=dict)
    agents: dict[str, AgentState] = field(default_factory=dict)
    tasks: dict[str, TaskState] = field(default_factory=dict)
    reasoning_services: dict[str, ReasoningServiceState] = field(default_factory=dict)

    version: int = 0
    last_change: float = field(default_factory=monotonic)

    @property
    def announcement_version(self) -> int:
        return self.version
