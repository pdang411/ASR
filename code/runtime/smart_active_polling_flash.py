from runtime.capabilities import SMART_ACTIVE_POLLING_CAPABILITIES


class SmartActivePollingFlash:
    """Build the LLM-readable SAP announcement."""

    def __init__(self, state, capabilities=None):
        self.state = state
        self.capabilities = dict(capabilities or SMART_ACTIVE_POLLING_CAPABILITIES)

    def render(self):
        s = self.state

        def _field(*names, default="UNKNOWN"):
            for name in names:
                value = getattr(s, name, None)
                if value is not None:
                    return value
            return default

        providers = getattr(s, "providers", {})
        provider_values = providers.values() if isinstance(providers, dict) else list(providers or [])

        lines = [
            "# ASR SMART ACTIVE POLLING - FLASH ANNOUNCEMENT",
            "",
            f"**Status:** {_field('status')}",
            f"**Mode:** {_field('mode')}",
            f"**Hot Path:** {_field('hot_path')}",
            f"**Polling Interval:** {_field('poll_interval_seconds', 'poll_interval', default=30)}s",
            f"**Idle Keep-Alive:** {_field('idle_keep_alive_seconds', 'keep_alive', default=60)}s",
            f"**Polling Cycle:** {_field('cycle_count', 'cycle', default=0)}",
            f"**Announcement Version:** {_field('version', 'announcement_version', default=0)}",
            "",
            "## Capabilities",
            "",
            "| Capability | Status |",
            "|---|---|",
        ]

        for capability, status in self.capabilities.items():
            lines.append(f"| {capability} | {status} |")

        lines += [
            "",
            "## Polling Operations",
            "",
            "| Operation | Function |",
            "|---|---|",
            "| Provider Discovery | Discover reasoning services |",
            "| Local LLM Discovery | Discover local reasoning services |",
            "| Model Discovery | Query available models |",
            "| Active Model Detection | Detect loaded model when supported |",
            "| Health Check | Check provider health |",
            "| Registry Update | Update runtime provider/model state |",
            "| Idle Detection | Detect inactive services |",
            "| Keep-Alive | Maintain idle service readiness |",
            "",
            "## Provider / Model State",
            "",
            "| Field | Meaning |",
            "|---|---|",
            "| Provider | Runtime provider identifier |",
            "| Endpoint | Provider endpoint when reported |",
            "| Status | Current provider state |",
            "| Models | Discovered models |",
            "| Active Model | Active model when reported |",
            "| Queue Depth | Current queued work |",
            "| Latency | Observed response latency |",
            "| Throughput | Observed throughput |",
            "| Health | Latest health state |",
            "",
            "## Provider Snapshot",
            "",
            "| Provider | Endpoint | Status | Models | Active Model |",
            "|---|---|---|---|---|",
        ]

        for provider in provider_values:
            if isinstance(provider, dict):
                models = ", ".join(provider.get("models", [])) or "-"
                lines.append(
                    f"| {provider.get('provider_id', '-')} | {provider.get('endpoint', '-')} | {provider.get('status', 'UNKNOWN')} | {models} | {provider.get('active_model') or '-'} |"
                )

        lines += [
            "",
            "## Operating Rules",
            "",
            "- Do not hardcode model names.",
            "- Query configured providers concurrently.",
            "- Do not perform inference during discovery.",
            "- Do not interrupt active inference.",
            "- Keep polling off the Smart Preemption hot path.",
            "- Do not create a second keep-alive implementation.",
            "- Publish current runtime state through FLASH.",
        ]

        return "\n".join(lines)