from .task_capabilities import Capability


class ResearchAgent:
    def execute(self, task):
        if not hasattr(task, "capabilities") or task.capabilities is None:
            task.capabilities = []

        required = [
            Capability.KNOWLEDGE_SEARCH.value,
            Capability.REPOSITORY_SEARCH.value,
        ]

        for capability in required:
            if capability not in task.capabilities:
                task.capabilities.append(capability)

        return task
