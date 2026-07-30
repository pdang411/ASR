#!/usr/bin/env python3
"""Minimal ASR MCP server over stdio.

This process is launched by OpenCode via MCP local transport.
"""

import json
import os
import time
import anyio
import urllib.request
import urllib.error
import urllib.parse
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

ASR_BASE_URL = os.environ.get("ASR_MCP_BASE_URL", "http://asr-mcp-server:8600").rstrip("/")
ASR_HTTP_TIMEOUT_SECONDS = float(os.environ.get("ASR_HTTP_TIMEOUT_SECONDS", "8"))
ASR_HTTP_RETRIES = max(0, int(os.environ.get("ASR_HTTP_RETRIES", "1")))
ASR_CACHE_TTL_SECONDS = max(0.0, float(os.environ.get("ASR_CACHE_TTL_SECONDS", "1.5")))
ASR_CACHE_MAX_ENTRIES = max(1, int(os.environ.get("ASR_CACHE_MAX_ENTRIES", "256")))

TOOL_ALIASES = {
    "memory.build": "asr.memory.build",
    "reference.get": "asr.search.reference",
    "reference.search": "asr.search.query",
    "task.get": "asr.task.get",
    "workflow.get": "asr.workflow.get",
    "module.list": "asr.module.list",
    # Compatibility with underscore-style invocations seen in prompts/older configs.
    "asr_build_memory": "asr.memory.build",
    "asr_reference_get": "asr.search.reference",
    "asr_search_query": "asr.search.query",
    "asr_task_get": "asr.task.get",
    "asr_workflow_get": "asr.workflow.get",
    "asr_module_list": "asr.module.list",
}

_CACHE: dict[str, tuple[float, dict]] = {}


def _cache_get(key: str) -> dict | None:
    record = _CACHE.get(key)
    if record is None:
        return None
    expires_at, value = record
    if time.monotonic() >= expires_at:
        _CACHE.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: dict) -> None:
    if ASR_CACHE_TTL_SECONDS <= 0:
        return
    if len(_CACHE) >= ASR_CACHE_MAX_ENTRIES:
        # Deterministically evict the oldest expiring entry.
        oldest_key = min(_CACHE, key=lambda k: _CACHE[k][0])
        _CACHE.pop(oldest_key, None)
    _CACHE[key] = (time.monotonic() + ASR_CACHE_TTL_SECONDS, value)


def _request_json(method: str, url: str, payload: dict | None = None, timeout_seconds: float | None = None) -> dict:
    if timeout_seconds is None:
        timeout_seconds = ASR_HTTP_TIMEOUT_SECONDS

    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    last_error: Exception | None = None
    for attempt in range(ASR_HTTP_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
            return json.loads(raw)
        except urllib.error.HTTPError as exc:
            # Do not retry deterministic client errors.
            if 400 <= exc.code < 500:
                raise
            last_error = exc
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = exc

        if attempt < ASR_HTTP_RETRIES:
            time.sleep(0.1 * (attempt + 1))

    if last_error is not None:
        raise last_error
    raise RuntimeError("request failed without explicit error")


def _post_json(url: str, payload: dict, timeout_seconds: float | None = None, cache_key: str | None = None) -> dict:
    if cache_key:
        hit = _cache_get(cache_key)
        if hit is not None:
            return hit
    result = _request_json("POST", url, payload=payload, timeout_seconds=timeout_seconds)
    if cache_key:
        _cache_set(cache_key, result)
    return result


def _get_json(url: str, timeout_seconds: float | None = None, cache_key: str | None = None) -> dict:
    if cache_key:
        hit = _cache_get(cache_key)
        if hit is not None:
            return hit
    result = _request_json("GET", url, timeout_seconds=timeout_seconds)
    if cache_key:
        _cache_set(cache_key, result)
    return result


def _canonical_text(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


async def on_list_tools(_ctx, _params):
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="memory.build",
                description="Build a deterministic memory package.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "query": {"type": "string"},
                        "references": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="reference.get",
                description="Get a reference by id.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="reference.search",
                description="Search references by query.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="task.get",
                description="Get a task by id.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="workflow.get",
                description="Get a workflow by id.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="module.list",
                description="List core modules.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            # Backward-compatible internal aliases
            types.Tool(
                name="asr.memory.build",
                description="Alias for memory.build.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "query": {"type": "string"},
                        "references": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr.search.reference",
                description="Alias for reference.get.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr.search.query",
                description="Alias for reference.search.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr.task.get",
                description="Alias for task.get.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr.workflow.get",
                description="Alias for workflow.get.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr.module.list",
                description="Alias for module.list.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            # Underscore-style compatibility aliases.
            types.Tool(
                name="asr_build_memory",
                description="Alias for memory.build.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "query": {"type": "string"},
                        "references": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr_reference_get",
                description="Alias for reference.get.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr_search_query",
                description="Alias for reference.search.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr_task_get",
                description="Alias for task.get.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr_workflow_get",
                description="Alias for workflow.get.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"}
                    },
                    "required": ["id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr_module_list",
                description="Alias for module.list.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            # Existing ASR passthrough tool kept for compatibility
            types.Tool(
                name="asr.transcribe",
                description="Proxy transcription request to ASR HTTP service.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "audio_url": {"type": "string"},
                        "language": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
            ),
        ]
    )


async def on_call_tool(_ctx, params):
    name = params.name
    if name in TOOL_ALIASES:
        name = TOOL_ALIASES[name]

    args = params.arguments if isinstance(params.arguments, dict) else {}

    if name == "asr.memory.build":
        payload = {}
        if isinstance(args.get("task"), str):
            payload["task"] = args["task"]
        if isinstance(args.get("query"), str):
            payload["query"] = args["query"]
        if isinstance(args.get("references"), list):
            payload["references"] = args["references"]
        try:
            cache_key = f"POST:{ASR_BASE_URL}/memory:{json.dumps(payload, sort_keys=True, separators=(',', ':'))}"
            result = _post_json(f"{ASR_BASE_URL}/memory", payload, cache_key=cache_key)
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"memory.build failure: {e}")], isError=True)

    if name == "asr.search.reference":
        ref_id = args.get("id", "")
        if not isinstance(ref_id, str) or not ref_id:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: id")], isError=True)
        try:
            ref_url = f"{ASR_BASE_URL}/reference/{urllib.parse.quote(ref_id, safe='')}"
            result = _get_json(ref_url, cache_key=f"GET:{ref_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"reference.get failure: {e}")], isError=True)

    if name == "asr.search.query":
        query = args.get("query", "")
        if not isinstance(query, str):
            query = str(query)
        limit = args.get("limit", 5)
        try:
            limit_value = max(1, min(20, int(limit)))
        except (TypeError, ValueError):
            limit_value = 5
        try:
            q = urllib.parse.quote(query, safe='')
            search_url = f"{ASR_BASE_URL}/reference/search?q={q}&limit={limit_value}"
            result = _get_json(search_url, cache_key=f"GET:{search_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"reference.search failure: {e}")], isError=True)

    if name == "asr.task.get":
        task_id = args.get("id", "")
        if not isinstance(task_id, str) or not task_id:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: id")], isError=True)
        try:
            task_url = f"{ASR_BASE_URL}/task/{urllib.parse.quote(task_id, safe='')}"
            result = _get_json(task_url, cache_key=f"GET:{task_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"task.get failure: {e}")], isError=True)

    if name == "asr.workflow.get":
        workflow_id = args.get("id", "")
        if not isinstance(workflow_id, str) or not workflow_id:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: id")], isError=True)
        try:
            workflow_url = f"{ASR_BASE_URL}/workflow/{urllib.parse.quote(workflow_id, safe='')}"
            result = _get_json(workflow_url, cache_key=f"GET:{workflow_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"workflow.get failure: {e}")], isError=True)

    if name == "asr.module.list":
        try:
            module_url = f"{ASR_BASE_URL}/module/list"
            result = _get_json(module_url, cache_key=f"GET:{module_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"module.list failure: {e}")], isError=True)

    if name == "asr.transcribe":
        payload = {}
        if isinstance(args.get("text"), str):
            payload["text"] = args["text"]
        if isinstance(args.get("audio_url"), str):
            payload["audio_url"] = args["audio_url"]
        if isinstance(args.get("language"), str):
            payload["language"] = args["language"]

        try:
            # Cache identical text requests briefly to avoid duplicate round-trips.
            cache_key = None
            if isinstance(payload.get("text"), str) and payload["text"].strip():
                cache_key = f"POST:{ASR_BASE_URL}/asr/transcribe:{json.dumps(payload, sort_keys=True, separators=(',', ':'))}"
            result = _post_json(f"{ASR_BASE_URL}/asr/transcribe", payload, cache_key=cache_key)
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except urllib.error.HTTPError as e:
            message = e.read().decode("utf-8", errors="replace")
            return types.CallToolResult(
                content=[types.TextContent(text=f"ASR HTTP error {e.code}: {message}")],
                isError=True,
            )
        except Exception as e:
            return types.CallToolResult(
                content=[types.TextContent(text=f"ASR proxy failure: {e}")],
                isError=True,
            )

    return types.CallToolResult(
        content=[types.TextContent(text=f"Unknown tool: {params.name}")],
        isError=True,
    )


server = Server(
    name="asr",
    version="0.1.0",
    on_list_tools=on_list_tools,
    on_call_tool=on_call_tool,
)


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    anyio.run(main)
