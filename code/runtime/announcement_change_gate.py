class AnnouncementChangeGate:
    def __init__(self):
        self.last_version = -1
        self.last_markdown = ""

    def get_if_changed(self, registry, markdown_builder):
        version = registry.state.version
        if version == self.last_version:
            return None

        self.last_version = version
        self.last_markdown = markdown_builder.build()
        return self.last_markdown
