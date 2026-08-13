from time import monotonic

from runtime.announcement_state import RuntimeAnnouncementState


class RuntimeStateRegistry:
    def __init__(self):
        self.state = RuntimeAnnouncementState()

    def mark_changed(self):
        self.state.version += 1
        self.state.last_change = monotonic()

    # Compatibility alias used by newer runtime wiring.
    def changed(self):
        self.mark_changed()

    def update_mcp_connection(self, connection):
        existing = self.state.mcp_connections.get(connection.service_id)
        if existing == connection:
            return
        self.state.mcp_connections[connection.service_id] = connection
        self.mark_changed()

    def remove_mcp_connection(self, service_id):
        if self.state.mcp_connections.pop(service_id, None):
            self.mark_changed()

    def update_tool(self, tool):
        key = f"{tool.service_id}:{tool.name}"
        existing = self.state.tools.get(key)
        if existing == tool:
            return
        self.state.tools[key] = tool
        self.mark_changed()

    def update_feature(self, feature):
        existing = self.state.features.get(feature.name)
        if existing == feature:
            return
        self.state.features[feature.name] = feature
        self.mark_changed()

    def update_agent(self, agent):
        existing = self.state.agents.get(agent.agent_id)
        if existing == agent:
            return
        self.state.agents[agent.agent_id] = agent
        self.mark_changed()

    def update_task(self, task):
        existing = self.state.tasks.get(task.task_id)
        if existing == task:
            return
        self.state.tasks[task.task_id] = task
        self.mark_changed()

    def update_reasoning_service(self, service):
        key = f"{service.provider}:{service.model}"
        existing = self.state.reasoning_services.get(key)
        if existing == service:
            return
        self.state.reasoning_services[key] = service
        self.mark_changed()

    def update_provider(self, provider_state):
        value = {
            "provider_id": str(getattr(provider_state, "provider_id", "")),
            "endpoint": str(getattr(provider_state, "endpoint", "")),
            "status": str(getattr(provider_state, "status", "UNKNOWN")),
            "models": list(getattr(provider_state, "models", []) or []),
            "active_model": getattr(provider_state, "active_model", None),
            "queue_depth": int(getattr(provider_state, "queue_depth", 0) or 0),
            "avg_latency_ms": float(getattr(provider_state, "avg_latency_ms", 0.0) or 0.0),
            "tokens_per_sec": float(getattr(provider_state, "avg_tokens_per_sec", 0.0) or 0.0),
            "success_rate": float(getattr(provider_state, "success_rate", 1.0) or 0.0),
            "last_health": float(getattr(provider_state, "last_health", 0.0) or 0.0),
            "last_model_query": float(getattr(provider_state, "last_model_query", 0.0) or 0.0),
            "model_query_count": int(getattr(provider_state, "model_query_count", 0) or 0),
            "model_query_failures": int(getattr(provider_state, "model_query_failures", 0) or 0),
        }
        key = value["provider_id"] or value["endpoint"]
        if not key:
            return

        if self.state.providers.get(key) != value:
            self.state.providers[key] = value
            self.mark_changed()

    def set_runtime_state(self, **values):
        changed = False
        for key, value in values.items():
            if hasattr(self.state, key) and getattr(self.state, key) != value:
                setattr(self.state, key, value)
                changed = True
        if changed:
            self.mark_changed()

    # Compatibility alias used by newer runtime wiring.
    def set_runtime(self, **values):
        self.set_runtime_state(**values)
