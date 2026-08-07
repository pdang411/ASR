class RuntimeStatus:

    def snapshot(self):
        return {
            "state":"running",
            "active_requests":0,
            "providers":[],
            "executors":[],
            "uptime":0
        }