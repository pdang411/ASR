#!/usr/bin/env python3
"""Minimal ASR MCP server over stdio.

This process is launched by OpenCode via MCP local transport.
"""

import json
import hashlib
import os
import time
import anyio
import urllib.request
import urllib.error
import urllib.parse
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from runtime.capability_registry import MCPCapabilityRegistry
from runtime.tool_registration import register_default_capabilities
from runtime.announcement_state import (
    MCPConnectionState,
    ToolState,
    FeatureState,
    AgentState,
    TaskState,
    ReasoningServiceState,
)
from runtime.runtime_state_registry import RuntimeStateRegistry
from runtime.announcement_markdown import RuntimeAnnouncementMarkdown
from runtime.announcement_change_gate import AnnouncementChangeGate
from runtime.runtime_capability_resource import RuntimeCapabilityResource

from agent_task.task_classifier import TaskClassifier
from agent_task.task_capabilities import Capability
from agent_task.task_request import TaskRequest

ASR_BASE_URL = os.environ.get("ASR_MCP_BASE_URL", "http://mcp-server:8700").rstrip("/")
ASR_HTTP_TIMEOUT_SECONDS = float(os.environ.get("ASR_HTTP_TIMEOUT_SECONDS", "8"))
ASR_HTTP_RETRIES = max(0, int(os.environ.get("ASR_HTTP_RETRIES", "1")))
ASR_CACHE_TTL_SECONDS = max(0.0, float(os.environ.get("ASR_CACHE_TTL_SECONDS", "1.5")))
ASR_CACHE_MAX_ENTRIES = max(1, int(os.environ.get("ASR_CACHE_MAX_ENTRIES", "256")))
ASR_ANNOUNCEMENT_REFRESH_SECONDS = max(0.5, float(os.environ.get("ASR_ANNOUNCEMENT_REFRESH_SECONDS", "2")))

capability_registry = register_default_capabilities(MCPCapabilityRegistry())
runtime_state_registry = RuntimeStateRegistry()
runtime_markdown_builder = RuntimeAnnouncementMarkdown(runtime_state_registry)
announcement_change_gate = AnnouncementChangeGate()
runtime_capability_resource = RuntimeCapabilityResource(runtime_state_registry, runtime_markdown_builder)
_LAST_ANNOUNCEMENT_REFRESH = 0.0

TOOL_ALIASES = {
    "task.compile": "asr.task.compile",
    "task.roles": "asr.task.roles",
    "memory.build": "asr.memory.build",
    "reference.get": "asr.search.reference",
    "reference.search": "asr.search.query",
    "task.get": "asr.task.get",
    "workflow.get": "asr.workflow.get",
    "module.list": "asr.module.list",
    "runtime.status": "asr.runtime.status",
    "runtime.execute": "asr.runtime.execute",
    "runtime.polling": "asr.runtime.polling",
    "workflow.execute": "asr.workflow.execute",
    "plugin.list": "asr.plugin.list",
    "plugin.get": "asr.plugin.get",
    "plugin.manager": "asr.plugin.manager",
    "module.manager": "asr.module.manager",
    "asr.transcribe": "asr.transcribe",
    # Compatibility with underscore-style invocations seen in prompts/older configs.
    "asr_build_memory": "asr.memory.build",
    "asr_asr_build_memory": "asr.memory.build",
    "asr_task_compile": "asr.task.compile",
    "asr_asr_task_compile": "asr.task.compile",
    "asr_task_roles": "asr.task.roles",
    "asr_asr_task_roles": "asr.task.roles",
    "asr_reference_get": "asr.search.reference",
    "asr_asr_reference_get": "asr.search.reference",
    "asr_reference_search": "asr.search.query",
    "asr_asr_reference_search": "asr.search.query",
    "asr_search_query": "asr.search.query",
    "asr_asr_search_query": "asr.search.query",
    "asr_task_get": "asr.task.get",
    "asr_asr_task_get": "asr.task.get",
    "asr_workflow_get": "asr.workflow.get",
    "asr_asr_workflow_get": "asr.workflow.get",
    "asr_workflow_execute": "asr.workflow.execute",
    "asr_asr_workflow_execute": "asr.workflow.execute",
    "asr_module_list": "asr.module.list",
    "asr_asr_module_list": "asr.module.list",
    "asr_plugin_list": "asr.plugin.list",
    "asr_asr_plugin_list": "asr.plugin.list",
    "asr_runtime_status": "asr.runtime.status",
    "asr_asr_runtime_status": "asr.runtime.status",
    "asr_runtime_execute": "asr.runtime.execute",
    "asr_asr_runtime_execute": "asr.runtime.execute",
    "asr_runtime_polling": "asr.runtime.polling",
    "asr_asr_runtime_polling": "asr.runtime.polling",
    "asr_asr_transcribe": "asr.transcribe",
}

_CACHE: dict[str, tuple[float, dict]] = {}


def _service_id_from_base_url() -> tuple[str, str, int | None]:
    parsed = urllib.parse.urlparse(ASR_BASE_URL)
    host = parsed.hostname or "asr-mcp-server"
    endpoint = f"{parsed.scheme or 'http'}://{host}"
    return host, endpoint, parsed.port


def _seed_runtime_announcement_state() -> None:
    for tool in capability_registry.list():
        runtime_state_registry.update_tool(
            ToolState(
                service_id=str(tool.service),
                name=str(tool.name),
                capability=str(tool.capability),
                description=str(tool.description),
                status="READY",
            )
        )

    total_tools = len(runtime_state_registry.state.tools)
    runtime_state_registry.update_mcp_connection(
        MCPConnectionState(
            service_id="ASR",
            endpoint="stdio",
            status="CONNECTED",
            port=None,
            last_heartbeat=time.monotonic(),
            tool_count=total_tools,
            resource_count=1,
            prompt_count=0,
        )
    )

    service_id, endpoint, port = _service_id_from_base_url()
    runtime_state_registry.update_mcp_connection(
        MCPConnectionState(
            service_id=service_id,
            endpoint=endpoint,
            status="READY",
            port=port,
            last_heartbeat=time.monotonic(),
            tool_count=total_tools,
            resource_count=1,
            prompt_count=0,
        )
    )

    runtime_state_registry.update_feature(
        FeatureState(
            name="Smart Active Polling",
            status="UNKNOWN",
            description="Asynchronous polling that remains off the hot path.",
        )
    )
    runtime_state_registry.update_feature(
        FeatureState(
            name="Smart Preemption",
            status="READY",
            description="Deterministic preemption decisions from runtime cache.",
        )
    )
    runtime_state_registry.update_feature(
        FeatureState(
            name="AI.KB",
            status="READY",
            description="Operational memory and structured context store.",
        )
    )


def _refresh_reasoning_services_from_health() -> None:
    try:
        payload = _get_json(
            f"{ASR_BASE_URL}/llm/health",
            timeout_seconds=2.0,
            cache_key=f"GET:{ASR_BASE_URL}/llm/health",
        )
    except Exception:
        return

    providers = payload.get("providers")
    if isinstance(providers, dict):
        for provider, info in providers.items():
            if not isinstance(info, dict):
                continue
            runtime_state_registry.update_reasoning_service(
                ReasoningServiceState(
                    provider=str(provider),
                    model=str(info.get("model") or info.get("provider") or "unknown"),
                    status=str(info.get("status", "UNKNOWN")),
                    queue_depth=int(info.get("queue_depth", 0) or 0),
                    avg_latency_ms=float(info.get("avg_latency_ms", 0.0) or 0.0),
                    tokens_per_sec=float(info.get("tokens_per_sec", 0.0) or 0.0),
                )
            )
        return

    if isinstance(providers, list):
        for info in providers:
            if not isinstance(info, dict):
                continue
            provider = str(info.get("provider") or "unknown")
            model = str(info.get("model") or provider)
            runtime_state_registry.update_reasoning_service(
                ReasoningServiceState(
                    provider=provider,
                    model=model,
                    status=str(info.get("status", "UNKNOWN")),
                    queue_depth=int(info.get("queue_depth", 0) or 0),
                    avg_latency_ms=float(info.get("avg_latency_ms", 0.0) or 0.0),
                    tokens_per_sec=float(info.get("tokens_per_sec", 0.0) or 0.0),
                )
            )


def _update_provider_snapshots(provider_records) -> None:
    if not isinstance(provider_records, list):
        return

    for record in provider_records:
        if not isinstance(record, dict):
            continue
        provider_id = str(record.get("provider_id") or "")
        endpoint = str(record.get("endpoint") or "")
        if not provider_id and not endpoint:
            continue

        class _ProviderStateView:
            pass

        view = _ProviderStateView()
        view.provider_id = provider_id or endpoint
        view.endpoint = endpoint
        view.status = str(record.get("status", "UNKNOWN"))
        view.models = list(record.get("models") or [])
        view.active_model = record.get("active_model")
        view.queue_depth = int(record.get("queue_depth", 0) or 0)
        view.avg_latency_ms = float(record.get("avg_latency_ms", 0.0) or 0.0)
        view.avg_tokens_per_sec = float(record.get("avg_tokens_per_sec", 0.0) or 0.0)
        view.success_rate = float(record.get("success_rate", 1.0) or 0.0)
        view.last_health = float(record.get("last_health", 0.0) or 0.0)
        view.last_model_query = float(record.get("last_model_query", 0.0) or 0.0)
        view.model_query_count = int(record.get("model_query_count", 0) or 0)
        view.model_query_failures = int(record.get("model_query_failures", 0) or 0)
        runtime_state_registry.update_provider(view)


def _refresh_runtime_announcement_state(force: bool = False) -> None:
    global _LAST_ANNOUNCEMENT_REFRESH

    now = time.monotonic()
    if not force and (now - _LAST_ANNOUNCEMENT_REFRESH) < ASR_ANNOUNCEMENT_REFRESH_SECONDS:
        return
    _LAST_ANNOUNCEMENT_REFRESH = now

    service_id, endpoint, port = _service_id_from_base_url()
    try:
        runtime = _get_json(
            f"{ASR_BASE_URL}/runtime/status",
            timeout_seconds=2.0,
            cache_key=f"GET:{ASR_BASE_URL}/runtime/status",
        )

        runtime_status = str(runtime.get("status", "RUNNING")).upper()
        sap_running = bool(runtime.get("sap_running", False))
        smart_preemption_status = str(runtime.get("smart_preemption_status", "READY"))
        ai_kb_status = str(runtime.get("ai_kb_status", "READY"))
        executor_registry_status = str(runtime.get("executor_registry_status", "READY"))

        runtime_state_registry.set_runtime_state(
            runtime_status=runtime_status,
            sap_running=sap_running,
            smart_preemption_status=smart_preemption_status,
            ai_kb_status=ai_kb_status,
            executor_registry_status=executor_registry_status,
        )

        runtime_state_registry.update_feature(
            FeatureState(
                name="Smart Active Polling",
                status="RUNNING" if sap_running else "STOPPED",
                description="Asynchronous polling that remains off the hot path.",
            )
        )
        runtime_state_registry.update_feature(
            FeatureState(
                name="Smart Preemption",
                status=smart_preemption_status,
                description="Deterministic preemption decisions from runtime cache.",
            )
        )
        runtime_state_registry.update_feature(
            FeatureState(
                name="AI.KB",
                status=ai_kb_status,
                description="Operational memory and structured context store.",
            )
        )

        runtime_state_registry.update_mcp_connection(
            MCPConnectionState(
                service_id=service_id,
                endpoint=endpoint,
                status="CONNECTED",
                port=port,
                last_heartbeat=time.monotonic(),
                tool_count=len(runtime_state_registry.state.tools),
                resource_count=1,
                prompt_count=0,
            )
        )

        sap = runtime.get("sap") if isinstance(runtime, dict) else None
        if isinstance(sap, dict):
            _update_provider_snapshots(sap.get("providers"))
    except Exception:
        runtime_state_registry.update_mcp_connection(
            MCPConnectionState(
                service_id=service_id,
                endpoint=endpoint,
                status="UNREACHABLE",
                port=port,
                last_heartbeat=0.0,
                tool_count=len(runtime_state_registry.state.tools),
                resource_count=1,
                prompt_count=0,
            )
        )
        runtime_state_registry.set_runtime_state(runtime_status="DEGRADED")

    # Pull explicit SAP provider state when available.
    try:
        sap_payload = _get_json(
            f"{ASR_BASE_URL}/runtime/sap",
            timeout_seconds=2.0,
            cache_key=f"GET:{ASR_BASE_URL}/runtime/sap",
        )
        if isinstance(sap_payload, dict):
            _update_provider_snapshots(sap_payload.get("providers"))
            if "model_poll_interval_seconds" in sap_payload:
                runtime_state_registry.update_feature(
                    FeatureState(
                        name="Smart Active Polling",
                        status="RUNNING" if bool(sap_payload.get("sap_running", False)) else "STOPPED",
                        description=(
                            "Asynchronous polling every "
                            f"{int(sap_payload.get('model_poll_interval_seconds', 30) or 30)} seconds."
                        ),
                    )
                )
    except Exception:
        pass

    _refresh_reasoning_services_from_health()


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


async def capability_markdown() -> str:
    """
    Internal helper for tests and runtime diagnostics.
    """
    _refresh_runtime_announcement_state()
    changed = announcement_change_gate.get_if_changed(runtime_state_registry, runtime_markdown_builder)
    if changed is not None:
        return changed
    if announcement_change_gate.last_markdown:
        return announcement_change_gate.last_markdown
    rendered = await runtime_capability_resource.read()
    announcement_change_gate.last_markdown = rendered
    announcement_change_gate.last_version = runtime_state_registry.state.version
    return rendered


def _normalize_capabilities(values) -> list[str]:
    normalized = []
    if not isinstance(values, list):
        return normalized
    for value in values:
        if isinstance(value, str) and value.strip():
            normalized.append(value.strip())
    return normalized


def _infer_roles(prompt: str, capabilities: list[str]) -> list[str]:
    text = prompt.lower()
    capability_set = set(capabilities)

    if capability_set.intersection({"research", "planning", "multi_agent", "project", "workflow.plan"}) or any(
        token in text for token in ("research", "plan", "workflow", "project", "multi-agent")
    ):
        return ["researcher", "analyst", "coder", "reviewer"]

    if capability_set.intersection({"code.generate", "code.review", "repository.search"}) or any(
        token in text for token in ("code", "review", "repository", "search")
    ):
        return ["coder", "reviewer"]

    if capability_set.intersection({"knowledge.search", "lookup"}) or any(
        token in text for token in ("lookup", "knowledge", "search")
    ):
        return ["analyst"]

    return ["controller"]


def _infer_intent(prompt: str, capabilities: list[str]) -> str:
    text = prompt.lower()
    capability_set = set(capabilities)

    if capability_set.intersection({"research", "planning", "multi_agent", "project", "workflow.plan"}) or any(
        token in text for token in ("research", "plan", "workflow", "project", "multi-agent")
    ):
        return "planning"

    if capability_set.intersection({"knowledge.search", "lookup"}) or any(
        token in text for token in ("lookup", "knowledge", "search")
    ):
        return "lookup"

    if capability_set.intersection({"code.generate", "code.review", "repository.search"}) or any(
        token in text for token in ("code", "review", "repository")
    ):
        return "tool.call"

    return "chat"


def _compile_task(args: dict) -> dict:
    prompt = args.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Missing required field: prompt")

    capabilities = _normalize_capabilities(args.get("capabilities"))
    context = args.get("context") if isinstance(args.get("context"), dict) else {}
    payload = args.get("payload") if isinstance(args.get("payload"), dict) else {}
    intent = _infer_intent(prompt.strip(), capabilities)

    task = TaskRequest(
        intent=intent,
        goal=prompt.strip(),
        capabilities=[Capability(capability) for capability in capabilities if capability in Capability._value2member_map_],
        mode="smart",
    )

    classifier = TaskClassifier()
    mode = classifier.classify(task)
    roles = _infer_roles(task.goal, capabilities)

    return {
        "task": {
            "intent": task.intent,
            "goal": task.goal,
            "capabilities": capabilities,
            "mode": mode,
            "roles": roles,
            "context": context,
            "payload": payload,
        },
        "compiled": True,
    }


async def on_list_tools(_ctx, _params):
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="task.compile",
                description="Compile a prompt into an ASR task and infer execution mode and roles.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "capabilities": {"type": "array", "items": {"type": "string"}},
                        "context": {"type": "object"},
                        "payload": {"type": "object"},
                    },
                    "required": ["prompt"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="task.roles",
                description="Infer ASR execution roles for a prompt and capability set.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "capabilities": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["prompt"],
                    "additionalProperties": False,
                },
            ),
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
            types.Tool(
                name="runtime.status",
                description="Get ASR runtime and SAP polling status.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            types.Tool(
                name="runtime.execute",
                description="Execute a runtime control action such as status or SAP start/stop/prime.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "snapshot", "sap.start", "sap.stop", "sap.prime", "start", "stop", "prime"],
                        },
                        "data": {"type": "object"},
                    },
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="runtime.polling",
                description="Control SAP polling directly.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "start", "stop", "prime", "flash_announcement"],
                        }
                    },
                    "additionalProperties": False,
                },
            ),
            # Backward-compatible internal aliases
            types.Tool(
                name="asr.task.compile",
                description="Alias for task.compile.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "capabilities": {"type": "array", "items": {"type": "string"}},
                        "context": {"type": "object"},
                        "payload": {"type": "object"},
                    },
                    "required": ["prompt"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr.task.roles",
                description="Alias for task.roles.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "capabilities": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["prompt"],
                    "additionalProperties": False,
                },
            ),
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
                name="asr_workflow_execute",
                description="Alias for workflow.execute.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "data": {"type": "object"},
                    },
                    "required": ["workflow_id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr_module_list",
                description="Alias for module.list.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            types.Tool(
                name="asr_asr_module_list",
                description="Alias for module.list.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            types.Tool(
                name="asr_plugin_list",
                description="Alias for plugin.list.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            types.Tool(
                name="asr_asr_plugin_list",
                description="Alias for plugin.list.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            types.Tool(
                name="asr_reference_search",
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
                name="asr_asr_transcribe",
                description="Alias for asr.transcribe.",
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
            types.Tool(
                name="asr.runtime.status",
                description="Alias for runtime.status.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            types.Tool(
                name="asr.runtime.execute",
                description="Alias for runtime.execute.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "snapshot", "sap.start", "sap.stop", "sap.prime", "start", "stop", "prime"],
                        },
                        "data": {"type": "object"},
                    },
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr.runtime.polling",
                description="Alias for runtime.polling.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "start", "stop", "prime", "flash_announcement"],
                        }
                    },
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="asr_asr_runtime_polling",
                description="Alias for runtime.polling.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "start", "stop", "prime", "flash_announcement"],
                        }
                    },
                    "additionalProperties": False,
                },
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
            # ASR Foundation tools
            types.Tool(
                name="runtime.execute",
                description="Execute tasks in the ASR runtime environment.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "data": {"type": "object"}
                    },
                    "required": ["task_id"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="module.manager",
                description="Manage ASR modules and plugins.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "info"]},
                        "module_name": {"type": "string"}
                    },
                    "required": ["action"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="workflow.execute",
                description="Execute ASR workflows.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"}
                    },
                    "required": ["workflow_id"],
                    "additionalProperties": False,
                },
            ),
            # Plugin management tools
            types.Tool(
                name="plugin.list",
                description="List all ASR Foundation plugins.",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            types.Tool(
                name="plugin.get",
                description="Get information about a specific ASR plugin.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "plugin_name": {"type": "string"}
                    },
                    "required": ["plugin_name"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="plugin.manager",
                description="Manage ASR plugins.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "info", "enable", "disable"]},
                        "plugin_name": {"type": "string"}
                    },
                    "required": ["action"],
                    "additionalProperties": False,
                },
            ),
        ]
    )


async def on_list_resources(_ctx, _params):
    _refresh_runtime_announcement_state()
    return types.ListResourcesResult(
        resources=[
            types.Resource(
                uri=RuntimeCapabilityResource.URI,
                name="ASR 1.0 Live Runtime Announcement",
                description="Live runtime summary of MCP connections, tools, features, agents, tasks, and reasoning services.",
                mimeType="text/markdown",
            )
        ]
    )


async def on_read_resource(_ctx, params):
    uri = getattr(params, "uri", None)
    if uri != RuntimeCapabilityResource.URI:
        return types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=uri or RuntimeCapabilityResource.URI,
                    mimeType="text/plain",
                    text=f"Unknown resource: {uri}",
                )
            ]
        )

    return types.ReadResourceResult(
        contents=[
            types.TextResourceContents(
                uri=RuntimeCapabilityResource.URI,
                mimeType="text/markdown",
                text=await capability_markdown(),
            )
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

    if name == "asr.task.compile":
        try:
            compiled = _compile_task(args)
            task_hash = hashlib.md5(compiled["task"]["goal"].encode("utf-8")).hexdigest()[:10]
            task_id = f"task-{task_hash}"
            runtime_state_registry.update_task(
                TaskState(
                    task_id=task_id,
                    status="READY",
                    agent_id="agent-01",
                    progress=0.0,
                    dependencies=[],
                )
            )
            runtime_state_registry.update_agent(
                AgentState(
                    agent_id="agent-01",
                    status="RUNNING",
                    task_id=task_id,
                    progress=35.0,
                )
            )
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(compiled))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"task.compile failure: {e}")], isError=True)

    if name == "asr.task.roles":
        try:
            compiled = _compile_task(args)
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        text=_canonical_text(
                            {
                                "prompt": compiled["task"]["goal"],
                                "capabilities": compiled["task"]["capabilities"],
                                "roles": compiled["task"]["roles"],
                            }
                        )
                    )
                ]
            )
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"task.roles failure: {e}")], isError=True)

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

    if name == "asr.workflow.execute":
        workflow_id = args.get("workflow_id", "")
        if not isinstance(workflow_id, str) or not workflow_id:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: workflow_id")], isError=True)
        payload = {"workflow_id": workflow_id}
        if isinstance(args.get("data"), dict):
            payload["data"] = args["data"]
        try:
            workflow_url = f"{ASR_BASE_URL}/workflow/execute"
            result = _post_json(workflow_url, payload)
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"workflow.execute failure: {e}")], isError=True)

    if name == "asr.module.list":
        try:
            module_url = f"{ASR_BASE_URL}/module/list"
            result = _get_json(module_url, cache_key=f"GET:{module_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"module.list failure: {e}")], isError=True)

    if name == "asr.module.manager":
        action = args.get("action", "")
        if not isinstance(action, str) or action not in {"list", "info"}:
            return types.CallToolResult(content=[types.TextContent(text="Missing or invalid field: action")], isError=True)
        if action == "list":
            try:
                module_url = f"{ASR_BASE_URL}/module/list"
                result = _get_json(module_url, cache_key=f"GET:{module_url}")
                return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
            except Exception as e:
                return types.CallToolResult(content=[types.TextContent(text=f"module.manager failure: {e}")], isError=True)

        module_name = args.get("module_name", "")
        if not isinstance(module_name, str) or not module_name:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: module_name")], isError=True)
        try:
            info_url = f"{ASR_BASE_URL}/module/info/{urllib.parse.quote(module_name, safe='')}"
            result = _get_json(info_url, cache_key=f"GET:{info_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"module.manager failure: {e}")], isError=True)

    if name == "asr.runtime.status":
        try:
            runtime_url = f"{ASR_BASE_URL}/runtime/status"
            result = _get_json(runtime_url, cache_key=f"GET:{runtime_url}")
            _refresh_runtime_announcement_state(force=True)
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"runtime.status failure: {e}")], isError=True)

    if name == "asr.runtime.execute":
        payload = {}
        if isinstance(args.get("action"), str):
            payload["action"] = args["action"]
        if isinstance(args.get("data"), dict):
            payload["data"] = args["data"]
        try:
            runtime_url = f"{ASR_BASE_URL}/runtime/execute"
            result = _post_json(runtime_url, payload)
            _refresh_runtime_announcement_state(force=True)
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"runtime.execute failure: {e}")], isError=True)

    if name == "asr.runtime.polling":
        payload = {}
        if isinstance(args.get("action"), str):
            payload["action"] = args["action"]
        try:
            runtime_url = f"{ASR_BASE_URL}/runtime/sap"
            if payload.get("action") == "status":
                result = _get_json(runtime_url, cache_key=f"GET:{runtime_url}")
            else:
                result = _post_json(runtime_url, payload)
            _refresh_runtime_announcement_state(force=True)
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"runtime.polling failure: {e}")], isError=True)

    if name == "asr.plugin.list":
        try:
            plugin_url = f"{ASR_BASE_URL}/plugin/list"
            result = _get_json(plugin_url, cache_key=f"GET:{plugin_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"plugin.list failure: {e}")], isError=True)

    if name == "asr.plugin.get":
        plugin_name = args.get("plugin_name", "")
        if not isinstance(plugin_name, str) or not plugin_name:
            return types.CallToolResult(content=[types.TextContent(text="Missing required field: plugin_name")], isError=True)
        try:
            plugin_url = f"{ASR_BASE_URL}/plugin/get/{urllib.parse.quote(plugin_name, safe='')}"
            result = _get_json(plugin_url, cache_key=f"GET:{plugin_url}")
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"plugin.get failure: {e}")], isError=True)

    if name == "asr.plugin.manager":
        payload = {}
        if isinstance(args.get("action"), str):
            payload["action"] = args["action"]
        if isinstance(args.get("plugin_name"), str):
            payload["plugin_name"] = args["plugin_name"]
        try:
            result = _post_json(f"{ASR_BASE_URL}/plugin/manager", payload)
            return types.CallToolResult(content=[types.TextContent(text=_canonical_text(result))])
        except Exception as e:
            return types.CallToolResult(content=[types.TextContent(text=f"plugin.manager failure: {e}")], isError=True)

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
    on_list_resources=on_list_resources,
    on_read_resource=on_read_resource,
)


_seed_runtime_announcement_state()
_refresh_runtime_announcement_state(force=True)


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    anyio.run(main)
