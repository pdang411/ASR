from time import monotonic

import httpx

from runtime.provider import ReasoningProvider


class OpenAICompatibleProvider(ReasoningProvider):
    def __init__(self, state, timeout=5.0):
        super().__init__(state)
        self.client = httpx.AsyncClient(
            base_url=state.endpoint.rstrip("/"),
            timeout=timeout,
        )

    async def connect(self):
        self.state.status = "READY"

    async def refresh_health(self):
        response = await self.client.get("/models")
        response.raise_for_status()
        self.state.status = "READY"
        self.state.last_health = monotonic()

    async def discover_models(self) -> list[str]:
        response = await self.client.get("/models")
        response.raise_for_status()

        data = response.json()
        models = [
            item["id"]
            for item in data.get("data", [])
            if isinstance(item, dict) and item.get("id")
        ]
        self.state.last_model_query = monotonic()
        return models

    async def active_model(self) -> str | None:
        # OpenAI-compatible endpoints generally do not expose loaded model state.
        return None

    async def keep_alive(self):
        response = await self.client.get("/models")
        response.raise_for_status()

    async def infer(self, request):
        response = await self.client.post("/chat/completions", json=request)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
