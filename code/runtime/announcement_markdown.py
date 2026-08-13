class RuntimeAnnouncementMarkdown:
    def __init__(self, registry):
        self.registry = registry

    def build(self):
        state = self.registry.state
        lines = [
            "# ASR AI Services Runtime",
            "",
            f"**Runtime:** {state.runtime_status}",
            f"**Smart Active Polling:** {'RUNNING' if state.sap_running else 'STOPPED'}",
            f"**Announcement Version:** {state.version}",
            "",
            "ASR dynamically reports connected MCP services, runtime state, tools, features, agents, tasks, and reasoning services.",
            "",
            "## MCP Connections",
            "",
            "| Service | Endpoint | Port | Status | Heartbeat | Tools | Resources | Prompts |",
            "|---|---|---:|---|---|---:|---:|---:|",
        ]

        for connection in sorted(state.mcp_connections.values(), key=lambda item: item.service_id):
            heartbeat = "OK" if connection.heartbeat_age() <= 30 else "STALE"
            lines.append(
                f"| {connection.service_id} | {connection.endpoint} | {connection.port or '-'} | "
                f"{connection.status} | {heartbeat} | {connection.tool_count} | "
                f"{connection.resource_count} | {connection.prompt_count} |"
            )

        lines += [
            "",
            "## Runtime",
            "",
            "| Component | Status |",
            "|---|---|",
            f"| ASR Runtime | {state.runtime_status} |",
            f"| Smart Active Polling | {'RUNNING' if state.sap_running else 'STOPPED'} |",
            f"| Smart Preemption | {state.smart_preemption_status} |",
            f"| AI.KB | {state.ai_kb_status} |",
            f"| Executor Registry | {state.executor_registry_status} |",
            "",
            "## Tools & Capabilities",
            "",
            "| Service | Capability | Tool | Status |",
            "|---|---|---|---|",
        ]

        for tool in sorted(state.tools.values(), key=lambda item: (item.service_id, item.name)):
            lines.append(f"| {tool.service_id} | {tool.capability} | `{tool.name}` | {tool.status} |")

        lines += [
            "",
            "## Features",
            "",
            "| Feature | Status | Description |",
            "|---|---|---|",
        ]

        for feature in sorted(state.features.values(), key=lambda item: item.name):
            lines.append(f"| {feature.name} | {feature.status} | {feature.description} |")

        lines += [
            "",
            "## Agents",
            "",
            "| Agent | Status | Task | Progress |",
            "|---|---|---|---:|",
        ]

        for agent in sorted(state.agents.values(), key=lambda item: item.agent_id):
            lines.append(f"| {agent.agent_id} | {agent.status} | {agent.task_id or '-'} | {agent.progress:.0f}% |")

        lines += [
            "",
            "## Tasks",
            "",
            "| Task | Agent | Status | Progress | Dependencies |",
            "|---|---|---|---:|---|",
        ]

        for task in sorted(state.tasks.values(), key=lambda item: item.task_id):
            lines.append(
                f"| {task.task_id} | {task.agent_id or '-'} | {task.status} | "
                f"{task.progress:.0f}% | {', '.join(task.dependencies) or '-'} |"
            )

        lines += [
            "",
            "## Reasoning Providers",
            "",
            "| Provider | Endpoint | Status | Models | Active Model | Last Query | Queries | Failures |",
            "|---|---|---|---|---|---:|---:|---:|",
        ]

        for provider in sorted(state.providers.values(), key=lambda item: item.get("provider_id", "")):
            models = ", ".join(provider.get("models", [])) or "-"
            active_model = provider.get("active_model") or "-"
            last_query = float(provider.get("last_model_query", 0.0) or 0.0)
            lines.append(
                f"| {provider.get('provider_id', '-')} | {provider.get('endpoint', '-')} | "
                f"{provider.get('status', 'UNKNOWN')} | {models} | {active_model} | "
                f"{last_query:.3f} | {int(provider.get('model_query_count', 0) or 0)} | "
                f"{int(provider.get('model_query_failures', 0) or 0)} |"
            )

        lines += [
            "",
            "## Reasoning Services",
            "",
            "| Provider | Model | Status | Queue | Latency ms | Tokens/sec |",
            "|---|---|---|---:|---:|---:|",
        ]

        for service in sorted(state.reasoning_services.values(), key=lambda item: (item.provider, item.model)):
            lines.append(
                f"| {service.provider} | {service.model} | {service.status} | {service.queue_depth} | "
                f"{service.avg_latency_ms:.1f} | {service.tokens_per_sec:.1f} |"
            )

        lines += [
            "",
            "## Rules",
            "",
            "MCP schemas remain authoritative for exact tool execution.",
            "This Markdown is a live capability and runtime summary.",
            "Do not invent tools, services, agents, or task states.",
        ]

        return "\n".join(lines)


# Compatibility alias used by runtime wiring that imports RuntimeAnnouncement.
RuntimeAnnouncement = RuntimeAnnouncementMarkdown
