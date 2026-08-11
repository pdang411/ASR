class PreemptionFlash:
    def __init__(self, state):
        self.state = state

    def build(self):
        s = self.state
        m = s.metrics

        lines = [
            "# ASR SMART PREEMPTION - FLASH ANNOUNCEMENT",
            "",
            f"**Status:** {s.status}",
            f"**Mode:** {s.mode}",
            f"**Hot Path:** {s.hot_path}",
            f"**Cycle:** {s.cycle_count}",
            f"**Announcement Version:** {s.announcement_version}",
            "",
            "## Purpose",
            "",
            "Smart Preemption is the deterministic orchestration engine inside ASR Runtime.",
            "",
            "The LLM performs reasoning. Smart Preemption determines when reasoning is required and how execution should be coordinated.",
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
            "## Decision Priority",
            "",
            "EXISTING_RESULT -> AI.KB -> CACHED_CONTEXT -> REUSABLE_REASONING -> "
            "MERGE_REQUEST -> WAIT_DEPENDENCY -> SELECT_PROVIDER -> SELECT_MODEL -> "
            "REQUEST_REASONING -> DISPATCH",
            "",
            "## Available Decisions",
            "",
            "- REUSE_RESULT",
            "- REUSE_AI_KB",
            "- REUSE_REASONING",
            "- MERGE_REQUEST",
            "- WAIT_DEPENDENCY",
            "- QUEUE",
            "- SELECT_PROVIDER",
            "- SELECT_MODEL",
            "- REQUEST_REASONING",
            "- DISPATCH",
            "- COMPLETE",
            "- RETRY",
            "- FAIL",
            "",
            "## Current Decision",
            "",
            f"**Decision:** {s.last_decision}",
            f"**Reason:** {s.last_reason or 'NONE'}",
            f"**Task:** {s.last_task_id or 'NONE'}",
            "",
            "## Runtime Metrics",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Active Demands | {m.active_demands} |",
            f"| Queued Demands | {m.queued_demands} |",
            f"| Waiting Dependencies | {m.waiting_dependencies} |",
            f"| Cache Hits | {m.cache_hits} |",
            f"| Cache Misses | {m.cache_misses} |",
            f"| AI.KB Reuses | {m.ai_kb_reuses} |",
            f"| Reasoning Reuses | {m.reasoning_reuses} |",
            f"| Requests Merged | {m.requests_merged} |",
            f"| Duplicate Work Avoided | {m.duplicate_work_avoided} |",
            f"| LLM Requests | {m.llm_requests} |",
            f"| Completed Tasks | {m.completed_tasks} |",
            f"| Failed Tasks | {m.failed_tasks} |",
            f"| Total Decisions | {m.decisions_total} |",
            f"| Retries | {m.retries} |",
            "",
            "## Execution Rules",
            "",
            "- Prefer existing results before new reasoning.",
            "- Prefer AI.KB and cached context before new reasoning.",
            "- Reuse compatible reasoning whenever possible.",
            "- Merge compatible demands.",
            "- Keep independent work parallel.",
            "- Wait for required dependencies.",
            "- Select providers/models from current runtime state.",
            "- Keep Smart Preemption decisions deterministic.",
            "- Do not ask an LLM to make Smart Preemption decisions.",
            "- Do not perform network discovery on the dispatch hot path.",
            "",
            "## LLM Operating Instructions",
            "",
            "Treat this FLASH as current Smart Preemption runtime state.",
            "Do not invent capabilities, providers, models, agents, tasks, or decisions.",
            "Use MCP tool schemas as the authority for exact tool execution.",
            "When Smart Preemption reports a decision, treat that decision as authoritative orchestration state.",
        ]

        return "\n".join(lines)

    def render(self):
        return self.build()