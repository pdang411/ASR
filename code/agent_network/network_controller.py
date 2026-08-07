class NetworkController:
    def __init__(self, registry, runtime):
        self.registry = registry
        self.runtime = runtime

    def execute(self, task):
        results = []
        for role in task.roles:
            agent = self.registry.get(role)
            updated = agent.execute(task)
            results.append(self.runtime.execute(updated))
        return results