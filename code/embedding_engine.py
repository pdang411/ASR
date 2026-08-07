from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Return a deterministic numeric vector for text."""


class HashEmbeddingProvider(EmbeddingProvider):
    """Lightweight deterministic embedding provider based on SHA-256."""

    def __init__(self, dimensions: int = 32):
        if dimensions <= 0:
            raise ValueError("dimensions must be > 0")
        self.dimensions = dimensions

    async def embed(self, text: str) -> list[float]:
        payload = (text or "").encode("utf-8")
        vector: list[float] = []
        seed = 0
        while len(vector) < self.dimensions:
            digest = hashlib.sha256(payload + seed.to_bytes(4, "big")).digest()
            seed += 1
            for byte in digest:
                # Normalize to [-1.0, 1.0]
                vector.append((byte / 127.5) - 1.0)
                if len(vector) >= self.dimensions:
                    break
        return vector


class EmbeddingEngine:
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    async def encode(self, text: str) -> list[float]:
        if not isinstance(text, str):
            text = str(text)
        return await self.provider.embed(text)