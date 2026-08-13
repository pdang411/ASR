class GuidanceAgent:
    def __init__(self, aikb):
        self.aikb = aikb

    def on_event(self, event):
        if event["type"] == "unknown_command":
            return self.aikb.lookup("help.commands")

        if event["type"] == "mcp_failure":
            return self.aikb.lookup("troubleshooting.mcp")

        if event["type"] == "first_run":
            return self.aikb.lookup("getting_started")

        return None