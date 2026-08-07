# Decision factors for enhanced Smart Preemption

class DependencyGate:
    def evaluate(self, runtime_state):
        """Check if all prerequisites are complete"""
        dependencies = runtime_state.get("dependency_status", {})
        return all(dep.get("completed", False) for dep in dependencies.values())

class KnowledgeGate:
    def evaluate(self, runtime_state):
        """Check how much knowledge is already available"""
        knowledge = runtime_state.get("knowledge_score", 0.0)
        return knowledge > 0.7  # High knowledge availability

class ContextGate:
    def evaluate(self, runtime_state):
        """Check if shared context is sufficient"""
        context = runtime_state.get("context_score", 0.0)
        return context > 0.6  # Sufficient context available

class ConfidenceGate:
    def evaluate(self, runtime_state):
        """Check current confidence level"""
        confidence = runtime_state.get("confidence", {})
        avg_confidence = sum(confidence.values()) / len(confidence) if confidence else 0
        return avg_confidence > 0.7

class TokenCostGate:
    def evaluate(self, runtime_state):
        """Estimate token cost"""
        token_cost = runtime_state.get("token_score", 0.0)
        return token_cost < 1000  # Low token cost threshold

class ParallelOpportunityGate:
    def evaluate(self, runtime_state):
        """Check if parallel execution is possible"""
        agents = runtime_state.get("agent_state", {})
        running_agents = [a for a in agents.values() if a.get("status") == "running"]
        return len(running_agents) < 5  # Multiple agents can run concurrently

class MergeOpportunityGate:
    def evaluate(self, runtime_state):
        """Check if merging is beneficial"""
        requests = runtime_state.get("pending_requests", [])
        return len(requests) > 1  # Multiple pending requests

class PredictionGate:
    def evaluate(self, runtime_state):
        """Predict if delay improves throughput"""
        progress = runtime_state.get("progress", {})
        # Simple prediction based on how much work is done
        completed_tasks = sum(1 for p in progress.values() if p >= 1.0)
        total_tasks = len(progress)
        return (completed_tasks / total_tasks) < 0.5 if total_tasks > 0 else False

class DecisionGate:
    def evaluate(self, ctx):
        """Final decision based on computed score"""
        score = self.compute_decision_score(ctx)
        return self.next_best_action(score)

    @staticmethod
    def compute_decision_score(ctx):
        """Compute weighted score from all factors"""
        # Use the weights as provided in v3 specification
        return (
            ctx.task_score * 1.20 +
            ctx.knowledge_score * 1.40 +
            ctx.context_score * 1.20 +
            ctx.confidence_score * 1.10 +
            ctx.dependency_score * 1.30 +
            ctx.reuse_score * 1.50 +
            ctx.merge_score * 1.40 +
            ctx.parallel_score * 1.60 +
            ctx.prediction_score * 1.10 -
            ctx.token_score * 1.50 +
            ctx.resource_score * 1.00
        )

    @staticmethod
    def next_best_action(score):
        """Determine action based on score"""
        if score >= 90:
            return "REQUEST_LLM"
        if score >= 70:
            return "MERGE"
        if score >= 50:
            return "REUSE_CONTEXT"
        if score >= 30:
            return "USE_AIKB"
        if score >= 10:
            return "WAIT"
        return "CONTINUE"