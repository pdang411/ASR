from runtime.capabilities import SMART_PREEMPTION_CAPABILITIES


class SmartPreemptionFlash:
    """Build the LLM-readable Smart Preemption announcement."""

    def __init__(self, state, capabilities=None):
        self.state = state
        self.capabilities = dict(capabilities or SMART_PREEMPTION_CAPABILITIES)

    def render(self):
        s = self.state

        def _field(*names, default="UNKNOWN"):
            for name in names:
                value = getattr(s, name, None)
                if value is not None:
                    return value
            return default

        metrics = getattr(s, "metrics", None)
        metrics_map = {}
        if metrics is not None:
            for name in dir(metrics):
                if name.startswith("_"):
                    continue
                value = getattr(metrics, name)
                if isinstance(value, (int, float, str)):
                    metrics_map[name] = value

        lines = [
            "# ASR SMART PREEMPTION - FLASH ANNOUNCEMENT",
            "",
            f"**Status:** {_field('status')}",
            f"**Mode:** {_field('mode')}",
            f"**Hot Path:** {_field('hot_path')}",
            f"**Cycle:** {_field('cycle', 'cycle_count', default=0)}",
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
            "## Decision Priority",
            "",
            "EXISTING_RESULT -> AI.KB -> CACHED_CONTEXT -> REUSABLE_REASONING -> MERGE_REQUEST -> WAIT_DEPENDENCY -> SELECT_PROVIDER -> SELECT_MODEL -> REQUEST_REASONING -> DISPATCH",
            "",
            "## Available Decisions",
            "",
            "| Decision | Purpose |",
            "|---|---|",
            "| REUSE_RESULT | Reuse an existing completed result |",
            "| REUSE_AI_KB | Reuse authoritative AI.KB context |",
            "| REUSE_REASONING | Reuse compatible reasoning |",
            "| MERGE_REQUEST | Merge compatible demands |",
            "| WAIT_DEPENDENCY | Wait for a required dependency |",
            "| QUEUE | Queue work until dispatch is possible |",
            "| SELECT_PROVIDER | Select a ready provider |",
            "| SELECT_MODEL | Select a compatible model |",
            "| REQUEST_REASONING | Request new reasoning |",
            "| DISPATCH | Dispatch execution |",
            "| RETRY | Retry recoverable work |",
            "| FAIL | Report unrecoverable failure |",
            "",
            "## Current Decision",
            "",
            f"**Decision:** {_field('decision', 'last_decision', default='NONE')}",
            f"**Reason:** {_field('reason', 'last_reason', default='') or 'NONE'}",
            f"**Task:** {_field('task', 'last_task_id', default='NONE')}",
            "",
            "## Runtime Metrics",
            "",
            "| Metric | Value |",
            "|---|---:|",
        ]

        for name, value in sorted(metrics_map.items()):
            lines.append(f"| {name} | {value} |")

        lines += [
            "",
            "## Operating Rules",
            "",
            "- Prefer existing results before new reasoning.",
            "- Prefer AI.KB and cached context before new reasoning.",
            "- Reuse compatible reasoning.",
            "- Merge compatible demands.",
            "- Keep independent work parallel.",
            "- Wait for required dependencies.",
            "- Use current runtime state for provider/model selection.",
            "- Keep deterministic decisions on the hot path.",
            "- Do not invent unavailable capabilities.",
        ]

        return "\n".join(lines)