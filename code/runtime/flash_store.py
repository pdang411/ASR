class FlashStore:
    """Stores the latest generated FLASH for runtime discovery."""

    def __init__(self):
        self._announcements = {}
        self._versions = {}

    def publish(self, name, markdown):
        version = self._versions.get(name, 0) + 1
        self._versions[name] = version
        self._announcements[name] = markdown
        return version

    def get(self, name):
        return self._announcements.get(name)

    def version(self, name):
        return self._versions.get(name, 0)

    def all(self):
        return dict(self._announcements)