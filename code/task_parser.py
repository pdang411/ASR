from .task_models import AgentTask

class AgentTaskParser:
    def compile(self,prompt:str)->AgentTask:
        return AgentTask(
            intent="general",
            goal=prompt,
            capabilities=[],
            payload={}
        )