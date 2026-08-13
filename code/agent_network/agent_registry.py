class AgentRegistry:
    def __init__(self):
        self._agents = {}

    def register(self, role, agent):
        self._agents[role] = agent

    def get(self, role):
        return self._agents[role]