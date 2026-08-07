from typing import Any, Dict
from .task_capabilities import Capability

class ResearchAgent:
    def __init__(self, aikb, executor_registry):
        self.aikb = aikb
        self.registry = executor_registry

    def execute(self, task) -> Dict[str, Any]:
        knowledge = self.aikb.search(task.goal)
        # Extend capabilities with research-related ones
        task.capabilities.extend([
            Capability.KNOWLEDGE_SEARCH,
            Capability.REPOSITORY_SEARCH
        ])
        return {
            'role':'researcher',
            'intent':task.intent,
            'goal':task.goal,
            'knowledge':knowledge,
            'recommended_executor':self.registry.best_executor(task.capabilities),
            'confidence':0.95
        }