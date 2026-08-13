from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PersistentMemory:
    def __init__(self, storage_path: str = "./data/memory_store.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    async def save(self, key, value):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")
        data = self._read_all()
        data[key] = value
        self._write_all(data)
        return {"saved": key}

    async def load(self, key):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")
        data = self._read_all()
        return data.get(key)

    async def delete(self, key):
        data = self._read_all()
        removed = key in data
        if removed:
            data.pop(key, None)
            self._write_all(data)
        return {"deleted": removed}

    async def list_keys(self):
        data = self._read_all()
        return sorted(data.keys())

    def _read_all(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return {}
        raw = self.storage_path.read_text(encoding="utf-8", errors="ignore").strip()
        if not raw:
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if isinstance(payload, dict):
            return payload
        return {}

    def _write_all(self, data: dict[str, Any]):
        serialized = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True)
        self.storage_path.write_text(serialized, encoding="utf-8")