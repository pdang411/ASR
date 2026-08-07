from dataclasses import dataclass

@dataclass
class RuntimeState:
    knowledge_score: int = 0
    context_score: int = 0
    confidence_score: int = 0
    dependency_score: int = 0
    reuse_score: int = 0
    merge_score: int = 0
    parallel_score: int = 0
    prediction_score: int = 0
    token_score: int = 0
    resource_score: int = 0

class RuntimeOptimizer:

    def update(self, aikb):
        state = aikb.runtime_state

        # Precompute all scores and store in runtime state
        state["scores"] = RuntimeState(
            knowledge_score=self.compute_knowledge(state),
            context_score=self.compute_context(state),
            confidence_score=self.compute_confidence(state),
            dependency_score=self.compute_dependency(state),
            reuse_score=self.compute_reuse(state),
            merge_score=self.compute_merge(state),
            parallel_score=self.compute_parallel(state),
            prediction_score=self.compute_prediction(state),
            token_score=self.compute_token(state),
            resource_score=self.compute_resource(state)
        )

        # Update last update time
        import time
        state["last_update"] = time.time()

    def compute_knowledge(self, state):
        """Compute knowledge score based on available knowledge"""
        # Simplified implementation - in real ASR this would query AI.KB
        return int(state.get("knowledge_score", 0.0) * 100)

    def compute_context(self, state):
        """Compute context score based on shared context"""
        # Simplified implementation  
        return int(state.get("context_score", 0.0) * 100)

    def compute_confidence(self, state):
        """Compute confidence score based on current agent confidence"""
        # Simplified implementation
        confidence = state.get("confidence", {})
        avg_conf = sum(confidence.values()) / len(confidence) if confidence else 0
        return int(avg_conf * 100)

    def compute_dependency(self, state):
        """Compute dependency score based on completed prerequisites"""
        dependencies = state.get("dependency_status", {})
        completed = sum(1 for dep in dependencies.values() if dep.get("completed", False))
        total = len(dependencies)
        return int((completed / total * 100) if total > 0 else 0)

    def compute_reuse(self, state):
        """Compute reuse score based on previous results"""
        # Simplified implementation
        return int(state.get("reuse_score", 0.0) * 100)

    def compute_merge(self, state):
        """Compute merge score based on pending requests"""
        # Simplified implementation
        return int(state.get("merge_score", 0.0) * 100)

    def compute_parallel(self, state):
        """Compute parallel score based on concurrent agents"""
        # Simplified implementation
        agents = state.get("agent_state", {})
        running_agents = [a for a in agents.values() if a.get("status") == "running"]
        return int(len(running_agents) * 10)

    def compute_prediction(self, state):
        """Compute prediction score based on progress"""
        # Simplified implementation
        return int(state.get("prediction_score", 0.0) * 100)

    def compute_token(self, state):
        """Compute token score based on estimated cost"""
        # Simplified implementation  
        return int(state.get("token_score", 0.0))

    def compute_resource(self, state):
        """Compute resource score based on available resources"""
        # Simplified implementation
        return int(state.get("resource_score", 0.0) * 10)