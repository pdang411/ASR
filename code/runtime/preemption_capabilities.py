SMART_PREEMPTION_CAPABILITIES = {
    "Deterministic Routing": "READY",
    "O(1) Cached Dispatch": "READY",
    "AI.KB Context Reuse": "READY",
    "Result Cache Reuse": "READY",
    "Reasoning Reuse": "READY",
    "Request Merging": "READY",
    "Duplicate Work Prevention": "READY",
    "Dependency Tracking": "READY",
    "Dependency Waiting": "READY",
    "Parallel Execution": "READY",
    "Agent Coordination": "READY",
    "Task Coordination": "READY",
    "Provider Selection": "READY",
    "Model Selection": "READY",
    "Queue Management": "READY",
    "Runtime State Access": "READY",
    "Performance Tracking": "READY",
    "Failure Recovery": "READY",
}


DECISION_PRIORITY = (
    "EXISTING_RESULT",
    "AI_KB",
    "CACHED_CONTEXT",
    "REUSABLE_REASONING",
    "MERGE_REQUEST",
    "WAIT_DEPENDENCY",
    "SELECT_PROVIDER",
    "SELECT_MODEL",
    "REQUEST_REASONING",
    "DISPATCH",
)