from ai_kb.universal_task import UniversalTask

class ExecutorRegistry:

    def __init__(self):
        self.adapters=[]

    def register(self, adapter):
        self.adapters.append(adapter)

    def dispatch(self, task):
        for adapter in self.adapters:
            if adapter.accepts(task):
                return adapter.dispatch(task)
        raise RuntimeError("No executor available")