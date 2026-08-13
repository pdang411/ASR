class ReasoningServiceRegistry:
    def __init__(self):
        self._services = {}

    def update_provider(self, provider):
        state = provider.state
        key = f"{state.provider_id}:{state.endpoint}"

        self._services[key] = {
            "provider_id": state.provider_id,
            "endpoint": state.endpoint,
            "status": state.status,
            "models": list(state.models),
            "active_model": state.active_model,
            "queue_depth": state.queue_depth,
            "avg_latency_ms": state.avg_latency_ms,
            "avg_tokens_per_sec": state.avg_tokens_per_sec,
            "success_rate": state.success_rate,
            "last_health": state.last_health,
            "last_model_query": state.last_model_query,
            "model_query_count": state.model_query_count,
            "model_query_failures": state.model_query_failures,
        }

    def refresh(self, providers):
        self._services = {}
        for provider in providers:
            self.update_provider(provider)

    def ready(self):
        return [
            service
            for service in self._services.values()
            if service["status"] == "READY"
        ]

    def list(self):
        return tuple(self._services.values())

    def snapshot(self):
        return dict(self._services)

    def update(self, provider_state):
        key = f"{provider_state.provider_id}:{provider_state.endpoint}"
        self._services[key] = {
            "provider_id": provider_state.provider_id,
            "endpoint": provider_state.endpoint,
            "status": provider_state.status,
            "models": list(provider_state.models),
            "active_model": provider_state.active_model,
            "queue_depth": provider_state.queue_depth,
            "avg_latency_ms": provider_state.avg_latency_ms,
            "avg_tokens_per_sec": provider_state.avg_tokens_per_sec,
            "success_rate": provider_state.success_rate,
            "last_health": provider_state.last_health,
            "last_model_query": provider_state.last_model_query,
            "model_query_count": provider_state.model_query_count,
            "model_query_failures": provider_state.model_query_failures,
        }


ReasoningRegistry = ReasoningServiceRegistry
