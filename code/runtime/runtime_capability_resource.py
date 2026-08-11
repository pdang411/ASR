class RuntimeCapabilityResource:
    URI = "asr://capabilities"

    def __init__(self, registry_or_builder, announcement=None):
        # Backward-compatible form: RuntimeCapabilityResource(markdown_builder)
        if announcement is None:
            self.registry = None
            self.announcement = registry_or_builder
        else:
            self.registry = registry_or_builder
            self.announcement = announcement
        self._last_version = -1
        self._cached = ""

    async def read(self):
        if self.registry is None:
            return self.announcement.build()

        version = getattr(self.registry.state, "announcement_version", getattr(self.registry.state, "version", 0))
        if version != self._last_version:
            self._cached = self.announcement.build()
            self._last_version = version
        return self._cached
