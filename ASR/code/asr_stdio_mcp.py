#!/usr/bin/env python3
"""Minimal ASR MCP server over stdio.

This process is launched by OpenCode via MCP local transport.
"""

import json
import os
import anyio
import urllib.request
import urllib.error
import urllib.parse
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

ASR_BASE_URL = os.environ.get("ASR_MCP_BASE_URL", "http://asr-mcp-server:8600").rstrip("/")

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


def _post_json(url: str, payload: dict, timeout_seconds: float = 10.0) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def _get_json(url: str, timeout_seconds: float = 10.0) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


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
                        "query": {"type": "string"}
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
                        "query": {"type": "string"}
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
                        "query": {"type": "string"}
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
            result = _post_json(f"{ASR_BASE_URL}/memory", payload)
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"memory.build failure: {e}")], isError=True)

    if name == "asr.search.reference":
        ref_id = args.get("id", "")
        if not isinstance(ref_id, str) or not ref_id:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: id")], isError=True)
        try:
            result = _get_json(f"{ASR_BASE_URL}/reference/{urllib.parse.quote(ref_id, safe='')}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"reference.get failure: {e}")], isError=True)

    if name == "asr.search.query":
        query = args.get("query", "")
        if not isinstance(query, str):
            query = str(query)
        try:
            q = urllib.parse.quote(query, safe='')
            result = _get_json(f"{ASR_BASE_URL}/reference/search?q={q}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"reference.search failure: {e}")], isError=True)

    if name == "asr.task.get":
        task_id = args.get("id", "")
        if not isinstance(task_id, str) or not task_id:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: id")], isError=True)
        try:
            result = _get_json(f"{ASR_BASE_URL}/task/{urllib.parse.quote(task_id, safe='')}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"task.get failure: {e}")], isError=True)

    if name == "asr.workflow.get":
        workflow_id = args.get("id", "")
        if not isinstance(workflow_id, str) or not workflow_id:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: id")], isError=True)
        try:
            result = _get_json(f"{ASR_BASE_URL}/workflow/{urllib.parse.quote(workflow_id, safe='')}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"workflow.get failure: {e}")], isError=True)

    if name == "asr.module.list":
        try:
            result = _get_json(f"{ASR_BASE_URL}/module/list")
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
            result = _post_json(f"{ASR_BASE_URL}/asr/transcribe", payload)
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
