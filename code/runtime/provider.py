from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    def __init__(self, state):
        self.state = state

    @abstractmethod
    async def connect(self):
        ...

    @abstractmethod
    async def discover_models(self) -> list[str]:
        ...

    async def active_model(self) -> str | None:
        return None

    @abstractmethod
    async def refresh_health(self):
        ...

    async def benchmark(self):
        return None

    async def keep_alive(self):
        return None

    @abstractmethod
    async def infer(self, request):
        ...

    def idle(self) -> bool:
        return self.state.active_requests == 0

    # Backward-compatible wrappers for older runtime integrations.
    async def query_models(self):
        models = await self.discover_models()
        self.state.models = list(models or [])
        return self.state.models

    async def query_loaded_model(self):
        model = await self.active_model()
        self.state.active_model = model
        return model

    def snapshot(self):
        return {
            "provider_id": self.state.provider_id,
            "endpoint": self.state.endpoint,
            "status": self.state.status,
            "models": list(self.state.models),
            "available_models": list(self.state.models),
            "active_model": self.state.active_model,
            "active_requests": self.state.active_requests,
            "queue_depth": self.state.queue_depth,
            "avg_latency_ms": self.state.avg_latency_ms,
            "avg_tokens_per_sec": self.state.avg_tokens_per_sec,
            "success_rate": self.state.success_rate,
            "provider_score": self.state.provider_score,
            "last_request": self.state.last_request,
            "last_health": self.state.last_health,
            "last_model_query": self.state.last_model_query,
            "last_model_scan": self.state.last_model_query,
            "last_active_model_query": self.state.last_active_model_query,
            "last_keep_alive": self.state.last_keep_alive,
            "last_warm": self.state.last_keep_alive,
            "model_query_count": self.state.model_query_count,
            "model_query_failures": self.state.model_query_failures,
            "health_failures": self.state.health_failures,
            "capabilities": list(getattr(self.state, "capabilities", [])),
        }
