from __future__ import annotations

import threading
import time


class KeepAlive:
    def __init__(self, provider, interval: float = 30):
        self.provider = provider
        self.interval = max(1.0, float(interval))
        self.running = False
        self._thread: threading.Thread | None = None

    def _loop(self):
        while self.running:
            try:
                self.provider.keepalive()
            except Exception:
                pass
            time.sleep(self.interval)

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False