from __future__ import annotations

import re

from embedding_engine import EmbeddingEngine
from vector_store import VectorStore


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


class HybridSearch:
    def __init__(self, embedding_engine: EmbeddingEngine, vector_store: VectorStore):
        self.embedding_engine = embedding_engine
        self.vector_store = vector_store

    async def search(self, query, limit=10):
        query_text = str(query or "").strip()
        if not query_text:
            return {"query": "", "matches": []}

        query_embedding = await self.embedding_engine.encode(query_text)
        vector_matches = await self.vector_store.search(query_embedding, limit=limit * 2)
        qtokens = set(_TOKEN_RE.findall(query_text.lower()))

        merged = []
        for item in vector_matches:
            metadata = item.get("metadata", {})
            text = str(metadata.get("text", ""))
            dtokens = set(_TOKEN_RE.findall(text.lower()))
            overlap = len(qtokens.intersection(dtokens))
            keyword_score = overlap / max(len(qtokens), 1)
            hybrid_score = (0.7 * float(item.get("score", 0.0))) + (0.3 * keyword_score)
            merged.append(
                {
                    "key": item.get("key"),
                    "score": round(hybrid_score, 6),
                    "vector_score": item.get("score", 0.0),
                    "keyword_score": round(keyword_score, 6),
                    "metadata": metadata,
                }
            )

        merged.sort(key=lambda row: (-row["score"], str(row["key"])))
        return {
            "query": query_text,
            "matches": merged[: max(1, int(limit))],
        }