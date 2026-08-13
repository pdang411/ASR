class RuntimeControl:

    def __init__(self, lifecycle):
        self.lifecycle = lifecycle

    def request_shutdown(self, reason="manual"):
        self.lifecycle.begin_shutdown(reason)

    def request_reload(self):
        self.lifecycle.reload()

    def health(self):
        return self.lifecycle.status()