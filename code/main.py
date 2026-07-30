#!/usr/bin/env python3
"""
ARS MCP Server - Main entry point
This implements the core ARS MCP Server functionality as per documentation standards.
"""

import os
import logging
import re
import time
import uuid
import json
from typing import Any
from flask import Flask, g, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")
_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_LANG_PATTERN = re.compile(r"^[A-Za-z]{2,12}(?:-[A-Za-z0-9]{2,8})?$")

API_VERSION = "1.1"
SERVICE_NAME = "mcp-server"
PROTOCOL_VERSION = "1.0"

_REFERENCE_INDEX = [
    {
        "id": "ref-compiler",
        "title": "Compiler Module",
        "summary": "Transforms prompts and tool plans into executable runtime tasks.",
    },
    {
        "id": "ref-builder",
        "title": "Builder Module",
        "summary": "Builds deterministic memory packages and task artifacts.",
    },
    {
        "id": "ref-runtime",
        "title": "Runtime Module",
        "summary": "Executes workflows with stable envelopes and strict tool policy.",
    },
    {
        "id": "ref-search",
        "title": "Search Module",
        "summary": "Provides reference retrieval, ranking, and query normalization.",
    },
    {
        "id": "ref-knowledge-graph",
        "title": "Knowledge Graph Module",
        "summary": "Connects references, tasks, and workflows for answer grounding.",
    },
    {
        "id": "ref-rest-api",
        "title": "REST API Module",
        "summary": "Exposes HTTP endpoints for MCP-compatible ARS operations.",
    },
]

_TOOL_NAMES = [
    "memory.build",
    "reference.get",
    "reference.search",
    "task.get",
    "workflow.get",
    "module.list",
    "asr.transcribe",
]


def _tokenize(value: str) -> list[str]:
    return _TOKEN_PATTERN.findall(value.lower())


def _normalize_transcript(value: str) -> str:
    # Normalize whitespace while preserving content for deterministic outputs.
    return " ".join(value.strip().split())


def _valid_id(value: str) -> bool:
    return bool(_ID_PATTERN.fullmatch(value))


def _error_payload(code: str, message: str, details: Any = None) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "details": details,
    }


def _ensure_json_object(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        return payload
    return None


def _rank_references(query: str, limit: int = 5) -> list[dict[str, Any]]:
    tokens = _tokenize(query)
    qset = set(tokens)
    if not qset:
        return []

    scored: list[tuple[float, dict[str, Any]]] = []
    q_lower = query.lower().strip()
    for ref in _REFERENCE_INDEX:
        id_lower = ref["id"].lower()
        title_lower = ref["title"].lower()
        summary_lower = ref["summary"].lower()
        doc_tokens = set(_tokenize(f"{ref['title']} {ref['summary']} {ref['id']}"))
        overlap = len(qset.intersection(doc_tokens))
        if overlap == 0 and q_lower not in title_lower and q_lower not in summary_lower and q_lower not in id_lower:
            continue

        score = overlap / max(len(qset), 1)
        if q_lower and (q_lower in title_lower or q_lower in id_lower):
            score += 0.5
        if q_lower and q_lower == title_lower:
            score += 0.5

        scored.append((score, ref))

    scored.sort(key=lambda row: (-row[0], row[1]["id"]))
    return [
        {
            "id": item["id"],
            "title": item["title"],
            "summary": item["summary"],
            "score": round(score, 6),
        }
        for score, item in scored[: max(1, limit)]
    ]


def _response(tool: str, started_at: float, result: Any = None, error: Any = None, success: bool = True):
    duration_ms = int((time.perf_counter() - started_at) * 1000)
    request_id = getattr(g, "request_id", None)
    return {
        "version": PROTOCOL_VERSION,
        "success": success,
        "result": result if result is not None else {},
        "error": error,
        "meta": {
            "tool": tool,
            "duration_ms": max(duration_ms, 0),
            "request_id": request_id,
            "api_version": API_VERSION,
        },
    }


def _deterministic_response(tool: str, result: Any = None, error: Any = None, success: bool = True):
    """Return a deterministic envelope compatible with ARS MCP/REST rules."""
    return _response(tool, time.perf_counter(), result=result, error=error, success=success)


def _error_response(tool: str, started_at: float, status_code: int, code: str, message: str, details: Any = None):
    envelope = _response(
        tool,
        started_at,
        success=False,
        error=_error_payload(code, message, details),
    )
    return jsonify(envelope), status_code


def _require_api_key_if_configured(tool: str, started_at: float):
    expected = os.environ.get("ARS_API_KEY", "").strip()
    if not expected:
        return None
    supplied = request.headers.get("x-api-key", "").strip()
    if supplied == expected:
        return None
    return _error_response(
        tool,
        started_at,
        401,
        "unauthorized",
        "Valid API key required.",
        {"header": "x-api-key"},
    )

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config['ENV'] = os.environ.get('ENV', 'development')
    app.config['DEBUG'] = os.environ.get('DEBUG', False)

    @app.before_request
    def _before_request():
        request_id = request.headers.get("x-request-id", "").strip()
        if not request_id:
            request_id = str(uuid.uuid4())
        g.request_id = request_id
        g.request_started_at = time.perf_counter()
        g.tool_name = "http.request"
        g.response_success = True

    @app.after_request
    def _after_request(response):
        request_id = getattr(g, "request_id", None)
        duration_ms = 0
        started = getattr(g, "request_started_at", None)
        if isinstance(started, float):
            duration_ms = max(int((time.perf_counter() - started) * 1000), 0)

        response.headers["x-request-id"] = request_id or ""
        response.headers["x-ars-api-version"] = API_VERSION

        log_event = {
            "event": "ars.request",
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "tool": getattr(g, "tool_name", "http.request"),
            "success": bool(getattr(g, "response_success", response.status_code < 400)),
            "duration_ms": duration_ms,
        }
        logger.info(json.dumps(log_event, sort_keys=True, separators=(",", ":")))
        return response
    
    @app.route('/')
    def hello():
        return jsonify({
            "message": "ARS MCP Server is running",
            "status": "healthy",
            "service": SERVICE_NAME,
            "api_version": API_VERSION,
        })
        
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy", 
            "service": SERVICE_NAME,
            "api_version": API_VERSION,
        })

    @app.route('/capabilities', methods=['GET'])
    def capabilities():
        started_at = time.perf_counter()
        g.tool_name = "system.capabilities"
        result = {
            "service": SERVICE_NAME,
            "protocol_version": PROTOCOL_VERSION,
            "api_version": API_VERSION,
            "deterministic": True,
            "tools": _TOOL_NAMES,
            "features": {
                "request_ids": True,
                "machine_readable_errors": True,
                "auth_header": "x-api-key",
            },
        }
        g.response_success = True
        return jsonify(_response("system.capabilities", started_at, result=result))

    @app.route('/memory', methods=['POST'])
    def memory_build():
        started_at = time.perf_counter()
        g.tool_name = "memory.build"

        auth_error = _require_api_key_if_configured("memory.build", started_at)
        if auth_error is not None:
            g.response_success = False
            return auth_error

        payload = _ensure_json_object(request.get_json(silent=True))
        if payload is None:
            g.response_success = False
            return _error_response(
                "memory.build",
                started_at,
                400,
                "invalid_json",
                "Request body must be a JSON object.",
            )

        task = payload.get('task', 'default')
        query = payload.get('query', '')
        references = payload.get('references', [])

        if not isinstance(task, str):
            g.response_success = False
            return _error_response("memory.build", started_at, 400, "invalid_argument", "Field 'task' must be a string.")
        if not isinstance(query, str):
            g.response_success = False
            return _error_response("memory.build", started_at, 400, "invalid_argument", "Field 'query' must be a string.")
        if not isinstance(references, list):
            g.response_success = False
            return _error_response("memory.build", started_at, 400, "invalid_argument", "Field 'references' must be a list.")
        if not all(isinstance(item, str) for item in references):
            g.response_success = False
            return _error_response(
                "memory.build",
                started_at,
                400,
                "invalid_argument",
                "Field 'references' must contain only strings.",
            )

        package = {
            "id": "memory-default",
            "task": task.strip() or "default",
            "query": query.strip(),
            "references": references,
            "content": f"# Memory Package\\n\\nTask: {task}\\n\\nQuery: {query}",
        }
        g.response_success = True
        return jsonify(_response("memory.build", started_at, result=package))

    @app.route('/reference/<ref_id>', methods=['GET'])
    def reference_get(ref_id):
        started_at = time.perf_counter()
        g.tool_name = "reference.get"
        if not _valid_id(ref_id):
            g.response_success = False
            return _error_response(
                "reference.get",
                started_at,
                400,
                "invalid_argument",
                "Path parameter 'ref_id' is invalid.",
                {"allowed_pattern": _ID_PATTERN.pattern},
            )

        match = next((item for item in _REFERENCE_INDEX if item["id"] == ref_id), None)
        if match is None:
            result = {
                "id": ref_id,
                "title": f"Reference {ref_id}",
                "summary": f"Deterministic reference payload for {ref_id}.",
            }
        else:
            result = {
                "id": match["id"],
                "title": match["title"],
                "summary": match["summary"],
            }
        g.response_success = True
        return jsonify(_response("reference.get", started_at, result=result))

    @app.route('/reference/search', methods=['GET'])
    def reference_search():
        started_at = time.perf_counter()
        g.tool_name = "reference.search"
        query = request.args.get('q', '')
        if not isinstance(query, str):
            query = str(query)
        query = query.strip()
        raw_limit = request.args.get('limit', '5')
        try:
            limit = max(1, min(20, int(raw_limit)))
        except ValueError:
            g.response_success = False
            return _error_response(
                "reference.search",
                started_at,
                400,
                "invalid_argument",
                "Query parameter 'limit' must be an integer between 1 and 20.",
            )

        matches = _rank_references(query, limit=limit)
        if not matches:
            # Keep deterministic fallback for empty/no-match queries.
            matches = [
                {
                    "id": "ref-search",
                    "title": "Search Module",
                    "summary": "Provides reference retrieval, ranking, and query normalization.",
                    "score": 0.0,
                }
            ]

        result = {
            "query": query,
            "limit": limit,
            "matches": matches,
        }
        g.response_success = True
        return jsonify(_response("reference.search", started_at, result=result))

    @app.route('/task/<task_id>', methods=['GET'])
    def task_get(task_id):
        started_at = time.perf_counter()
        g.tool_name = "task.get"
        if not _valid_id(task_id):
            g.response_success = False
            return _error_response("task.get", started_at, 400, "invalid_argument", "Path parameter 'task_id' is invalid.")

        result = {
            "id": task_id,
            "name": f"Task {task_id}",
            "status": "ready",
        }
        g.response_success = True
        return jsonify(_response("task.get", started_at, result=result))

    @app.route('/workflow/<workflow_id>', methods=['GET'])
    def workflow_get(workflow_id):
        started_at = time.perf_counter()
        g.tool_name = "workflow.get"
        if not _valid_id(workflow_id):
            g.response_success = False
            return _error_response("workflow.get", started_at, 400, "invalid_argument", "Path parameter 'workflow_id' is invalid.")

        result = {
            "id": workflow_id,
            "name": f"Workflow {workflow_id}",
            "steps": ["resolve", "build", "return"],
        }
        g.response_success = True
        return jsonify(_response("workflow.get", started_at, result=result))

    @app.route('/module/list', methods=['GET'])
    def module_list():
        started_at = time.perf_counter()
        g.tool_name = "module.list"
        result = {
            "modules": [
                "compiler",
                "builder",
                "runtime",
                "search",
                "knowledge-graph",
                "rest-api",
            ]
        }
        g.response_success = True
        return jsonify(_response("module.list", started_at, result=result))

    @app.route('/asr/transcribe', methods=['POST'])
    def asr_transcribe():
        """Simple ASR-style JSON endpoint consumed by the stdio MCP proxy."""
        started_at = time.perf_counter()
        g.tool_name = "asr.transcribe"

        auth_error = _require_api_key_if_configured("asr.transcribe", started_at)
        if auth_error is not None:
            g.response_success = False
            return auth_error

        payload = _ensure_json_object(request.get_json(silent=True))
        if payload is None:
            g.response_success = False
            return _error_response(
                "asr.transcribe",
                started_at,
                400,
                "invalid_json",
                "Request body must be a JSON object.",
            )

        text = payload.get('text')
        audio_url = payload.get('audio_url')
        language = payload.get('language', 'en')
        if not isinstance(language, str) or not _LANG_PATTERN.fullmatch(language.strip()):
            g.response_success = False
            return _error_response(
                "asr.transcribe",
                started_at,
                400,
                "invalid_argument",
                "Field 'language' must be a language tag like 'en' or 'en-US'.",
            )

        if isinstance(text, str) and text.strip() and isinstance(audio_url, str) and audio_url.strip():
            g.response_success = False
            return _error_response(
                "asr.transcribe",
                started_at,
                400,
                "invalid_argument",
                "Provide exactly one of 'text' or 'audio_url'.",
            )

        if isinstance(text, str) and text.strip():
            transcript = _normalize_transcript(text)
            source = 'text'
            confidence = 0.99
        elif isinstance(audio_url, str) and audio_url.strip():
            # Placeholder behavior for URL mode until audio decoding is implemented.
            transcript = f"[simulated transcript from {audio_url.strip()}]"
            source = 'audio_url'
            confidence = 0.40
        else:
            g.response_success = False
            return _error_response(
                "asr.transcribe",
                started_at,
                400,
                "invalid_argument",
                "Provide either 'text' or 'audio_url'.",
            )

        words = len(transcript.split())
        g.response_success = True
        return jsonify(_response(
            "asr.transcribe",
            started_at,
            result={
                "service": SERVICE_NAME,
                "source": source,
                "language": language.strip(),
                "transcript": transcript,
                "word_count": words,
                "confidence": confidence,
            },
        ))
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Run on port 8600 for local development
    app.run(host='0.0.0.0', port=8600, debug=False)