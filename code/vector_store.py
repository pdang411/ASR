from __future__ import annotations

import math
from typing import Any


class VectorStore:
    def __init__(self):
        self._items: dict[str, tuple[list[float], dict[str, Any]]] = {}

    async def add(self, key, vector, metadata=None):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")
        normalized = [float(v) for v in vector]
        if not normalized:
            raise ValueError("vector must contain at least one value")
        meta = metadata if isinstance(metadata, dict) else {}
        self._items[key] = (normalized, meta)

    async def search(self, vector, limit=10):
        query = [float(v) for v in vector]
        if not query:
            return []
        max_results = max(1, int(limit))

        scored = []
        for key, (item_vec, meta) in self._items.items():
            score = _cosine_similarity(query, item_vec)
            scored.append(
                {
                    "key": key,
                    "score": round(score, 6),
                    "metadata": meta,
                }
            )

        scored.sort(key=lambda row: (-row["score"], row["key"]))
        return scored[:max_results]

    def count(self) -> int:
        return len(self._items)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    size = min(len(a), len(b))
    if size == 0:
        return 0.0
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for idx in range(size):
        av = a[idx]
        bv = b[idx]
        dot += av * bv
        norm_a += av * av
        norm_b += bv * bv
    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))