class CapabilityAnnouncement:
    URI = "asr://capabilities"

    def __init__(self, capability_registry):
        self.registry = capability_registry

    def markdown(self) -> str:
        return self.registry.build_markdown()

    def capability_for(self, tool_name: str):
        return self.registry.get(tool_name)