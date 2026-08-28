import asyncio
import os
import signal
import time
import threading
from flask import Flask, request, jsonify, g
from runtime.lifecycle import LifecycleManager
from runtime.startup import startup
from runtime.shutdown import shutdown
from runtime.resource_manager import ResourceManager
from runtime.signal_handler import install
from runtime.sap_runtime import SAPRuntime
from runtime.smart_preemption import SmartPreemption
from runtime.flash_store import FlashStore
from runtime.runtime_state_registry import RuntimeStateRegistry
from runtime.capability_registry import MCPCapabilityRegistry
from runtime.capability_announcement import CapabilityAnnouncement
from runtime.module_announcement import build_module_announcement
from runtime.tool_registration import register_default_capabilities

# Initialize components
lifecycle = LifecycleManager()
resource_manager = ResourceManager()

# Mock runtime object for demonstration
class MockRuntime:
    def __init__(self):
        self.sap = None
        self.smart_preemption = None
        self.sap_running = False
        self.started_at = time.monotonic()
        self.runtime_registry = RuntimeStateRegistry()
        self.module_registry = _StaticModuleRegistry([])
        self.flash = FlashStore()

    def set_module_catalog(self, modules):
        self.module_registry = _StaticModuleRegistry(modules)

    @property
    def status(self):
        return self.runtime_status()

    def load_config(self):
        print("Loading configuration...")
        
    def init_database(self):
        print("Initializing database...")
        
    def init_executor_registry(self):
        print("Initializing executor registry...")
        if self.smart_preemption is None:
            self.smart_preemption = SmartPreemption()
            asyncio.run(self.smart_preemption.initialize())
            render = getattr(getattr(self.smart_preemption, "flash", None), "render", None)
            if callable(render):
                self.flash.publish("smart_preemption", render())
        
    def init_provider_pool(self):
        print("Initializing provider pool...")
        self.sap = SAPRuntime(runtime_registry=self.runtime_registry)
        self.sap_running = False
        
    def start_keepalive(self):
        print("Starting keep-alive...")

    def start_sap(self):
        if self.sap is None or self.sap_running:
            return
        print("Starting smart active polling...")
        self.sap_running = True
        self.runtime_registry.set_runtime_state(runtime_status="RUNNING", sap_running=True)
        self.sap.start()
        render = getattr(getattr(self.sap.poller, "flash", None), "render", None)
        if callable(render):
            self.flash.publish("smart_active_polling", render())

    def runtime_status(self):
        sap_snapshot = self.sap.snapshot() if self.sap is not None else {}
        return {
            "status": "running",
            "uptime_seconds": round(time.monotonic() - self.started_at, 3),
            "sap_running": self.sap_running,
            "sap": sap_snapshot,
        }

    def runtime_execute(self, payload):
        action = str(payload.get("action", "status")).strip().lower()

        if action in {"status", "snapshot"}:
            return self.runtime_status()

        if action in {"sap.start", "start", "polling.start"}:
            self.start_sap()
            return {"status": "ok", "action": action, "sap_running": self.sap_running}

        if action in {"sap.stop", "stop", "polling.stop"}:
            self.stop_sap()
            return {"status": "ok", "action": action, "sap_running": self.sap_running}

        if action in {"sap.prime", "prime", "polling.prime"}:
            if self.sap is None:
                return {"status": "error", "message": "SAP runtime is not initialized"}
            try:
                asyncio.run(self.sap.prime())
                return {"status": "ok", "action": action, "sap": self.sap.snapshot()}
            except Exception as exc:
                return {"status": "error", "message": str(exc)}

        return {
            "status": "error",
            "message": f"Unknown runtime action: {action}",
            "allowed_actions": ["status", "snapshot", "sap.start", "sap.stop", "sap.prime"],
        }
        
    def start_metrics(self):
        print("Starting metrics collection...")
        
    def stop_accepting_requests(self):
        print("Stopping request acceptance...")
        
    def wait_for_active_tasks(self):
        print("Waiting for active tasks to complete...")
        
    def stop_keepalive(self):
        print("Stopping keep-alive...")

    def stop_sap(self):
        if self.sap is None or not self.sap_running:
            return
        print("Stopping smart active polling...")
        asyncio.run(self.sap.stop())
        self.sap.join(timeout=1)
        self.sap_running = False
        self.runtime_registry.set_runtime_state(runtime_status="RUNNING", sap_running=False)
        
    def flush_metrics(self):
        print("Flushing metrics...")
        
    def flush_database(self):
        print("Flushing database...")
        
    def close_provider_pool(self):
        print("Closing provider pool...")
        
    def shutdown(self):
        print("Shutting down runtime...")


class _StaticModuleRegistry:
    def __init__(self, modules):
        self._modules = list(modules or [])

    def list(self):
        return list(self._modules)


def create_app(runtime_instance=None):
    app = Flask(__name__)
    capability_registry = register_default_capabilities(MCPCapabilityRegistry())
    capability_announcement = CapabilityAnnouncement(capability_registry)

    module_catalog = [
        {
            "id": "agent_task",
            "name": "agent_task",
            "status": "READY",
            "capabilities": ["task parsing", "task routing", "task execution"],
            "description": "Agent task parsing, routing, and execution helpers.",
        },
        {
            "id": "agent_network",
            "name": "agent_network",
            "status": "READY",
            "capabilities": ["role registry", "agent coordination"],
            "description": "Multi-agent role registry and coordination helpers.",
        },
        {
            "id": "ai_kb",
            "name": "ai_kb",
            "status": "READY",
            "capabilities": ["memory", "knowledge cache", "runtime optimization"],
            "description": "AI.KB memory, knowledge, and runtime optimization modules.",
        },
        {
            "id": "executors",
            "name": "executors",
            "status": "READY",
            "capabilities": ["executor adapters", "registry utilities"],
            "description": "Executor adapters and registry utilities.",
        },
        {
            "id": "llm",
            "name": "llm",
            "status": "READY",
            "capabilities": ["session management", "provider health", "keepalive"],
            "description": "LLM session, provider, warmup, and keepalive management.",
        },
        {
            "id": "mcp",
            "name": "mcp",
            "status": "READY",
            "capabilities": ["capability announcement", "tool registration"],
            "description": "MCP capability announcement and tool registration helpers.",
        },
        {
            "id": "performance",
            "name": "performance",
            "status": "READY",
            "capabilities": ["profiling", "metrics", "provider health"],
            "description": "Runtime profiling, metrics, and provider health modules.",
        },
        {
            "id": "runtime",
            "name": "runtime",
            "status": "READY",
            "capabilities": ["state management", "polling", "scheduling", "control"],
            "description": "ASR runtime state, polling, scheduling, and control modules.",
        },
        {
            "id": "visualization",
            "name": "visualization",
            "status": "READY",
            "capabilities": ["state selection", "rendering"],
            "description": "Visualization state, selection, and rendering helpers.",
        },
    ]

    if runtime_instance is not None and hasattr(runtime_instance, "set_module_catalog"):
        runtime_instance.set_module_catalog(module_catalog)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"})

    @app.route('/capabilities', methods=['GET'])
    def capabilities():
        tools = {
            tool.name: {
                "description": tool.description,
                "service": tool.service,
                "capability": tool.capability,
            }
            for tool in capability_registry.list()
        }
        return jsonify({
            "success": True,
            "result": {
                "tools": tools,
                "markdown": capability_announcement.markdown(),
            },
        })

    def _require_api_key():
        expected = os.environ.get("ARS_API_KEY")
        if not expected:
            return None

        supplied = request.headers.get("x-api-key", "")
        if supplied != expected:
            return jsonify({
                "success": False,
                "error": {
                    "code": "unauthorized",
                    "message": "Invalid or missing API key",
                },
            }), 401
        return None

    @app.route('/memory', methods=['POST'])
    def memory():
        auth = _require_api_key()
        if auth is not None:
            return auth

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({
                "success": False,
                "error": {
                    "code": "invalid_json",
                    "message": "Request body must be a JSON object",
                },
            }), 400

        task = str(payload.get("task", "")).strip()
        query = str(payload.get("query", "")).strip()
        references = payload.get("references") if isinstance(payload.get("references"), list) else []

        result = {
            "task": task,
            "query": query,
            "references": [ref for ref in references if isinstance(ref, str)],
            "summary": f"memory package built for {task or 'unknown task'}",
        }

        return jsonify({"success": True, "result": result})

    @app.route('/reference/search', methods=['GET'])
    def reference_search():
        query = str(request.args.get("q", "")).strip()
        limit_raw = request.args.get("limit", "5")
        try:
            limit = max(1, min(20, int(limit_raw)))
        except (TypeError, ValueError):
            limit = 5

        matches = [
            {
                "id": f"ref-{index + 1}",
                "title": f"{query or 'reference'} match {index + 1}",
            }
            for index in range(limit)
        ]

        return jsonify({
            "success": True,
            "result": {
                "query": query,
                "limit": limit,
                "matches": matches,
            },
        })

    @app.route('/module/list', methods=['GET'])
    def module_list():
        modules = module_catalog
        smart_preemption = None
        smart_active_polling = None

        if runtime_instance is not None:
            if hasattr(runtime_instance, "module_registry") and hasattr(runtime_instance.module_registry, "list"):
                modules = runtime_instance.module_registry.list()
            smart_preemption = getattr(runtime_instance, "smart_preemption", None)

            sap_wrapper = getattr(runtime_instance, "sap", None)
            smart_active_polling = getattr(sap_wrapper, "poller", sap_wrapper)

        return jsonify({
            "success": True,
            "result": {
                "modules": build_module_announcement(
                    modules=modules,
                    smart_preemption=smart_preemption,
                    smart_active_polling=smart_active_polling,
                ),
            },
        })

    return app

def register_runtime_routes(app, runtime_instance):
    @app.route('/runtime/status', methods=['GET'])
    def runtime_status():
        return jsonify(runtime_instance.runtime_status())

    @app.route('/runtime/execute', methods=['POST'])
    def runtime_execute():
        payload = request.get_json(silent=True) or {}
        return jsonify(runtime_instance.runtime_execute(payload))

    @app.route('/runtime/sap', methods=['GET', 'POST'])
    def runtime_sap():
        if request.method == 'GET':
            return jsonify(runtime_instance.sap.snapshot() if runtime_instance.sap is not None else {
                "sap_running": runtime_instance.sap_running,
                "model_poll_interval_seconds": 30,
                "providers": [],
            })

        payload = request.get_json(silent=True) or {}
        action = str(payload.get("action", "status")).strip().lower()

        if action in {"start", "sap.start", "polling.start"}:
            runtime_instance.start_sap()
        elif action in {"stop", "sap.stop", "polling.stop"}:
            runtime_instance.stop_sap()
        elif action in {"prime", "sap.prime", "polling.prime"} and runtime_instance.sap is not None:
            asyncio.run(runtime_instance.sap.prime())

        if action in {"flash_announcement", "sap.flash_announcement", "polling.flash_announcement"}:
            snapshot = runtime_instance.sap.snapshot() if runtime_instance.sap is not None else {
                "sap_running": runtime_instance.sap_running,
                "model_poll_interval_seconds": 30,
                "providers": [],
            }
            announcement = snapshot.get("sap_flash_markdown") or snapshot.get("announcement") or ""
            return jsonify(
                {
                    "status": "ok",
                    "action": "flash_announcement",
                    "announcement": announcement,
                    "announcement_version": snapshot.get("announcement_version", 0),
                    "sap_running": bool(snapshot.get("sap_running", runtime_instance.sap_running)),
                }
            )

        result = runtime_instance.sap.snapshot() if runtime_instance.sap is not None else {
            "sap_running": runtime_instance.sap_running,
            "model_poll_interval_seconds": 30,
            "providers": [],
        }
        result["status"] = "ok"
        result["action"] = action
        return jsonify(result)


# Create and register runtime
runtime = MockRuntime()

# Register lifecycle hooks
lifecycle.on_startup(lambda: startup(runtime))
lifecycle.on_shutdown(lambda: shutdown(runtime))


app = create_app(runtime)
register_runtime_routes(app, runtime)


def main():
    # Install signal handlers
    install(runtime)

    # Start up the system
    print("Starting ASR Runtime...")
    lifecycle.startup()


if __name__ == '__main__':
    main()
    port = int(os.getenv('PORT', '8700'))
    debug = os.getenv('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes'}
    app.run(debug=debug, host='0.0.0.0', port=port)