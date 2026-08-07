class LifecycleManager:

    def __init__(self):
        self.state = "initialized"
        self.active_requests = 0
        self.providers = []
        self.executors = []

    def begin_shutdown(self, reason):
        print(f"Beginning shutdown due to: {reason}")
        self.stop_accepting_requests()
        self.wait_for_active_tasks()
        self.shutdown()

    def stop_accepting_requests(self):
        print("Stopping accepting new requests")
        self.state = "stopping"

    def wait_for_active_tasks(self):
        print("Waiting for active tasks to complete")
        # Simulate waiting
        import time
        time.sleep(0.1)
        self.state = "draining"

    def shutdown(self):
        print("Shutting down runtime")
        self.state = "shutdown"

    def reload(self):
        print("Reloading runtime")
        self.state = "reloading"

    def status(self):
        return {
            "state": self.state,
            "active_requests": self.active_requests,
            "providers": self.providers,
            "executors": self.executors,
            "uptime": 0
        }