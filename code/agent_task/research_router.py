class ResearchRouter:
    def route(self, task):
        if 'cad' in task.capabilities:
            return 'freecad'
        if 'coding' in task.capabilities:
            return 'agent-mcp'
        if 'planning' in task.capabilities:
            return 'deepagents'
        return 'runtime'