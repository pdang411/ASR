from .task_models import AgentTask

class TaskDecomposer:
    def split(self, task:AgentTask)->list[AgentTask]:
        return [
            AgentTask(id=f"{task.id}-analysis", intent=task.intent, goal=task.goal, role="analyst"),
            AgentTask(id=f"{task.id}-coding", intent=task.intent, goal=task.goal, role="coder"),
            AgentTask(id=f"{task.id}-control", intent=task.intent, goal=task.goal, role="controller"),
        ]