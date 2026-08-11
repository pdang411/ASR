class SAPFlash:
    def __init__(self, state):
        self.state = state

    def build(self):
        s = self.state
        m = s.metrics

        lines = [
            "# ASR SMART ACTIVE POLLING - FLASH ANNOUNCEMENT",
            "",
            f"**Status:** {s.status}",
            f"**Mode:** {s.mode}",
            f"**Hot Path:** {s.hot_path}",
            f"**Polling Interval:** {s.poll_interval_seconds} seconds",
            f"**Idle Keep-Alive:** {s.idle_keep_alive_seconds} seconds",
            f"**Polling Cycle:** {s.cycle_count}",
            f"**Announcement Version:** {s.announcement_version}",
            "",
            "## Purpose",
            "",
            "Smart Active Polling maintains current awareness of local reasoning services without performing LLM reasoning.",
            "",
            "## Capabilities",
            "",
            "| Capability | Status |",
            "|---|---|",
        ]

        for name, status in s.capabilities.items():
            lines.append(f"| {name} | {status} |")

        lines += [
            "",
            "## Provider State",
            "",
            "| Provider | Endpoint | Status | Models | Active Model | Last Model Query |",
            "|---|---|---|---|---|---:|",
        ]

        for provider in sorted(s.providers.values(), key=lambda item: item.get("provider_id", "")):
            models = ", ".join(provider.get("models", [])) or "-"
            active = provider.get("active_model") or "-"
            last_query = float(provider.get("last_model_query", 0.0) or 0.0)
            lines.append(
                f"| {provider.get('provider_id', '-')} | {provider.get('endpoint', '-')} | {provider.get('status', 'UNKNOWN')} | "
                f"{models} | {active} | {last_query:.3f} |"
            )

        lines += [
            "",
            "## Runtime Metrics",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Poll Cycles | {m.poll_cycles} |",
            f"| Provider Queries | {m.provider_queries} |",
            f"| Provider Query Failures | {m.provider_query_failures} |",
            f"| Health Checks | {m.health_checks} |",
            f"| Health Failures | {m.health_failures} |",
            f"| Model Discoveries | {m.model_discoveries} |",
            f"| Model Discovery Failures | {m.model_discovery_failures} |",
            f"| Active Model Checks | {m.active_model_checks} |",
            f"| Keep-Alive Requests | {m.keep_alive_requests} |",
            f"| Keep-Alive Failures | {m.keep_alive_failures} |",
            "",
            "## Provider Rules",
            "",
            "- Never hardcode model names.",
            "- Query configured providers concurrently.",
            "- Do not perform inference during discovery.",
            "- Do not interrupt active inference.",
            "- Keep keep-alive separate from model discovery.",
            "",
            "## Performance Rules",
            "",
            "- SAP remains off the Smart Preemption hot path.",
            "- Provider polling runs asynchronously.",
            "- Independent providers are polled in parallel.",
            "- Runtime state is cached.",
            "- FLASH Markdown is generated only at boot or after meaningful state changes.",
            "",
            "## LLM Operating Instructions",
            "",
            "Treat this FLASH as the current Smart Active Polling capability announcement.",
            "Do not invent providers, models, endpoints, or capabilities.",
            "MCP tool schemas remain authoritative for exact tool execution.",
        ]

        return "\n".join(lines)

    def render(self):
        return self.build()
