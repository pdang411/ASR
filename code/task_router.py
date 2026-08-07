class TaskRouter:
    def select_executor(self,task):
        if "cad" in task.capabilities:
            return "freecad"
        if "planning" in task.capabilities:
            return "deepagents"
        return "default"