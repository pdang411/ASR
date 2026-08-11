class CapabilityResource:
    URI = "asr://capabilities"

    def __init__(self, capability_registry):
        self.registry = capability_registry

    def read(self) -> str:
        """
        Always build the announcement from current runtime state.
        No static Markdown file is required.
        """
        return self.registry.build_markdown()