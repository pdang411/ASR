from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from embedding_engine import EmbeddingEngine
from vector_store import VectorStore


class DocumentIndexer:
    def __init__(self, embedding_engine: EmbeddingEngine, vector_store: VectorStore, chunk_size: int = 500):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        self.embedding_engine = embedding_engine
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self._documents: dict[str, dict[str, Any]] = {}

    async def index_file(self, path):
        doc_path = Path(path)
        if not doc_path.exists() or not doc_path.is_file():
            raise FileNotFoundError(str(doc_path))

        text = doc_path.read_text(encoding="utf-8", errors="ignore")
        chunks = _chunk_text(text, self.chunk_size)
        records = []
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            key = _chunk_key(doc_path, idx, chunk)
            embedding = await self.embedding_engine.encode(chunk)
            metadata = {
                "path": str(doc_path),
                "chunk_index": idx,
                "text": chunk,
            }
            await self.vector_store.add(key, embedding, metadata=metadata)
            records.append({"key": key, "chunk_index": idx})

        entry = {
            "path": str(doc_path),
            "chunks": len(records),
            "records": records,
        }
        self._documents[str(doc_path)] = entry
        return entry

    async def rebuild(self):
        rebuilt = []
        paths = list(self._documents.keys())
        self._documents.clear()
        for path in paths:
            rebuilt.append(await self.index_file(path))
        return rebuilt

    def indexed_documents(self) -> list[dict[str, Any]]:
        return [self._documents[path] for path in sorted(self._documents.keys())]


def _chunk_text(text: str, chunk_size: int) -> list[str]:
    if not text:
        return []
    compact = " ".join(text.split())
    if len(compact) <= chunk_size:
        return [compact]
    chunks = []
    start = 0
    while start < len(compact):
        end = start + chunk_size
        chunks.append(compact[start:end])
        start = end
    return chunks


def _chunk_key(path: Path, idx: int, chunk: str) -> str:
    digest = hashlib.sha1(f"{path}:{idx}:{chunk}".encode("utf-8")).hexdigest()[:12]
    return f"{path.name}:{idx}:{digest}"