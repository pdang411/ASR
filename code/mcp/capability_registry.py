from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MCPCapability:
    name: str
    description: str
    service: str
    capability: str


class MCPCapabilityRegistry:
    def __init__(self):
        self._tools: dict[str, MCPCapability] = {}

    def register(
        self,
        tool_name: str,
        description: str,
        service: str,
        capability: str,
    ) -> None:
        self._tools[tool_name] = MCPCapability(
            name=tool_name,
            description=description,
            service=service,
            capability=capability,
        )

    def unregister(self, tool_name: str) -> None:
        self._tools.pop(tool_name, None)

    def get(self, tool_name: str):
        return self._tools.get(tool_name)

    def list(self) -> tuple[MCPCapability, ...]:
        return tuple(self._tools.values())

    def build_markdown(self) -> str:
        lines = [
            "# ASR MCP Capability Announcement",
            "",
            "ASR is connected and ready.",
            "ASR = AI Services Runtime; transcription is optional.",
            "",
            "| Capability | Service | MCP Tool | Purpose |",
            "|---|---|---|---|",
        ]

        preferred_order = [
            "asr_runtime_execute",
            "asr_asr_build_memory",
            "workflow_get",
            "reference_search",
        ]

        for name in preferred_order:
            tool = self._tools.get(name)
            if tool is None:
                continue
            lines.append(
                f"| {tool.capability} | {tool.service} | `{tool.name}` | {tool.description} |"
            )

        # Keep transcription available but present it as optional/non-core.
        transcription_tool = self._tools.get("asr_asr_transcribe")
        if transcription_tool is not None:
            lines.extend(
                [
                    "",
                    "## Optional Capabilities",
                    "",
                    "| Capability | Service | MCP Tool | Purpose |",
                    "|---|---|---|---|",
                    (
                        f"| {transcription_tool.capability} | {transcription_tool.service} | "
                        f"`{transcription_tool.name}` | {transcription_tool.description} |"
                    ),
                ]
            )

        return "\n".join(lines)