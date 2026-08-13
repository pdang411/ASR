from __future__ import annotations

from hybrid_search import HybridSearch


class ContextBuilder:
    def __init__(self, search_engine: HybridSearch, max_chunks: int = 5):
        self.search_engine = search_engine
        self.max_chunks = max(1, max_chunks)

    async def build_context(self, query):
        search_result = await self.search_engine.search(query, limit=self.max_chunks)
        matches = search_result.get("matches", [])
        snippets = []
        for row in matches:
            metadata = row.get("metadata", {})
            text = str(metadata.get("text", "")).strip()
            if text:
                snippets.append(text)

        context_text = "\n\n".join(snippets)
        return {
            "query": search_result.get("query", ""),
            "items": len(matches),
            "context": context_text,
            "matches": matches,
        }