from dataclasses import dataclass

@dataclass
class DecisionContext:
    task_score: float = 0.0
    knowledge_score: float = 0.0
    context_score: float = 0.0
    confidence_score: float = 0.0
    dependency_score: float = 0.0
    reuse_score: float = 0.0
    merge_score: float = 0.0
    parallel_score: float = 0.0
    prediction_score: float = 0.0
    token_score: float = 0.0
    resource_score: float = 0.0

DECISION_WEIGHTS = {
    "task":1.20,
    "knowledge":1.40,
    "context":1.20,
    "confidence":1.10,
    "dependency":1.30,
    "reuse":1.50,
    "merge":1.40,
    "parallel":1.60,
    "prediction":1.10,
    "token":1.50,
    "resource":1.00,
}

def compute_decision_score(ctx):
    return (
        ctx.task_score * DECISION_WEIGHTS["task"] +
        ctx.knowledge_score * DECISION_WEIGHTS["knowledge"] +
        ctx.context_score * DECISION_WEIGHTS["context"] +
        ctx.confidence_score * DECISION_WEIGHTS["confidence"] +
        ctx.dependency_score * DECISION_WEIGHTS["dependency"] +
        ctx.reuse_score * DECISION_WEIGHTS["reuse"] +
        ctx.merge_score * DECISION_WEIGHTS["merge"] +
        ctx.parallel_score * DECISION_WEIGHTS["parallel"] +
        ctx.prediction_score * DECISION_WEIGHTS["prediction"] -
        ctx.token_score * DECISION_WEIGHTS["token"] +
        ctx.resource_score * DECISION_WEIGHTS["resource"]
    )

def next_best_action(score):
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

# Runtime metrics for adaptive scoring
from ai_kb.runtime_metrics import RuntimeMetrics, tune_weights, evaluate_request, update_runtime_metrics
from ai_kb.protocol_handler import UniversalProtocolHandler
from ai_kb.universal_task import UniversalTask
from ai_kb.runtime_state import RuntimeState

# Fast path decision logic
def fast_decision(state):
    """Constant-time decision making (O(1)) - no expensive calculations"""
    
    # Simple addition of precomputed scores (without weights for pure O(1) speed)
    score = (
        state.knowledge_score +
        state.context_score +
        state.confidence_score +
        state.dependency_score +
        state.reuse_score +
        state.merge_score +
        state.parallel_score +
        state.prediction_score +
        state.resource_score -
        state.token_score
    )

    return next_best_action(score)

class SmartPipeline:
    def __init__(self, runtime_state=None):
        self.protocol_handler = UniversalProtocolHandler()
        self.state = runtime_state or RuntimeState(
            executor_cache={},
            pipeline_cache={},
            media_cache={},
            context_cache={}
        )
        
    def execute(self, task):
        # This would be a full implementation in real ASR
        # For now we return a mock response to indicate the smart pipeline was called
        return {
            "status": "completed",
            "pipeline": "smart",
            "task": task.dict()
        }

    def preemption_decision(self, agent_request, runtime_state):
        """Make preemption decisions based on decision factors"""
        
        # Build decision context from the runtime state and request
        ctx = DecisionContext(
            task_score=runtime_state.get("task_score", 0.0),
            knowledge_score=runtime_state.get("knowledge_score", 0.0),
            context_score=runtime_state.get("context_score", 0.0),
            confidence_score=runtime_state.get("confidence_score", 0.0),
            dependency_score=runtime_state.get("dependency_score", 0.0),
            reuse_score=runtime_state.get("reuse_score", 0.0),
            merge_score=runtime_state.get("merge_score", 0.0),
            parallel_score=runtime_state.get("parallel_score", 0.0),
            prediction_score=runtime_state.get("prediction_score", 0.0),
            token_score=runtime_state.get("token_score", 0.0),
            resource_score=runtime_state.get("resource_score", 0.0)
        )
        
        # Compute the decision score
        score = compute_decision_score(ctx)
        
        # Determine next best action
        action = next_best_action(score)
        
        return action

    def execute_with_preemption(self, task, runtime_state):
        """Execute task with smart preemption"""
        
        # This shows how the preemption logic would integrate in full implementation
        # For now it demonstrates the complete flow
        decision_score = compute_decision_score(DecisionContext(
            task_score=runtime_state.get("task_score", 0.0),
            knowledge_score=runtime_state.get("knowledge_score", 0.0),
            context_score=runtime_state.get("context_score", 0.0),
            confidence_score=runtime_state.get("confidence_score", 0.0),
            dependency_score=runtime_state.get("dependency_score", 0.0),
            reuse_score=runtime_state.get("reuse_score", 0.0),
            merge_score=runtime_state.get("merge_score", 0.0),
            parallel_score=runtime_state.get("parallel_score", 0.0),
            prediction_score=runtime_state.get("prediction_score", 0.0),
            token_score=runtime_state.get("token_score", 0.0),
            resource_score=runtime_state.get("resource_score", 0.0)
        ))
        
        # In real system this would:
        # 1. Evaluate logic gates
        # 2. Determine final action
        # 3. Dispatch based on decision
        
        # Execute the actual task (this is where the existing logic would be)
        return self.execute(task)

    def adaptive_preemption_decision(self, agent_request, runtime_state):
        """Make preemption decisions with adaptive runtime scoring"""
        
        # Get current runtime metrics
        metrics = runtime_state.get("runtime_metrics", RuntimeMetrics())
        
        # Build decision context from the runtime state and request
        ctx = DecisionContext(
            task_score=runtime_state.get("task_score", 0.0),
            knowledge_score=runtime_state.get("knowledge_score", 0.0),
            context_score=runtime_state.get("context_score", 0.0),
            confidence_score=runtime_state.get("confidence_score", 0.0),
            dependency_score=runtime_state.get("dependency_score", 0.0),
            reuse_score=runtime_state.get("reuse_score", 0.0),
            merge_score=runtime_state.get("merge_score", 0.0),
            parallel_score=runtime_state.get("parallel_score", 0.0),
            prediction_score=runtime_state.get("prediction_score", 0.0),
            token_score=runtime_state.get("token_score", 0.0),
            resource_score=runtime_state.get("resource_score", 0.0)
        )
        
        # Evaluate request with adaptive scoring
        evaluation = evaluate_request(ctx, metrics)
        
        return evaluation

    def update_metrics_and_make_decision(self, runtime_state, result):
        """Update runtime metrics and make a decision based on current performance"""
        
        # Get current metrics
        metrics = runtime_state.get("runtime_metrics", RuntimeMetrics())
        
        # Update metrics with new results  
        update_runtime_metrics(metrics, result)
        
        # Update the runtime state with new metrics
        runtime_state["runtime_metrics"] = metrics
        
        # Get decision based on updated metrics
        decision = self.adaptive_preemption_decision(None, runtime_state)
        
        # Store in decision history (for learning purposes)
        if "decision_history" not in runtime_state:
            runtime_state["decision_history"] = []
        runtime_state["decision_history"].append(decision)
        
        return decision

    def fast_path_decision(self, runtime_state):
        """Zero-bottleneck constant-time decision making"""
        # Read only precomputed runtime values (O(1) decision)
        scores = runtime_state.get("scores", RuntimeState())
        
        action = fast_decision(scores)
        return action

    def run_optimizer_periodically(self, aikb):
        """Run the optimizer periodically to keep scores updated"""
        optimizer = RuntimeOptimizer()
        optimizer.update(aikb)
    
    def universal_protocol_dispatch(self, input_data: dict, media_type: str = 'text') -> str:
        """Dispatch task using universal protocol"""
        # Create universal task markdown
        task_markdown = self.protocol_handler.process_task(input_data, media_type)
        
        # Add to dispatch queue or process directly
        return task_markdown
    
    def universal_protocol_process_result(self, result_markdown: str) -> dict:
        """Process result using universal protocol"""
        return self.protocol_handler.process_result(result_markdown)
    
    def handle_universal_task(self, universal_task: UniversalTask, registry):
        """
        Handle universal task through smart preemption system
        O(1) cache lookups only
        """
        # O(1) cache lookups only
        cached_pipeline = self.state.pipeline_cache.get(universal_task.intent)
        if cached_pipeline:
            universal_task.pipeline = cached_pipeline

        # Dispatch through executor registry
        result = registry.dispatch(universal_task)
        
        return result
    
    def visualization_optimization(self, task, runtime_state):
        """
        Visualization Optimization Engine for Smart Preemption v11
        O(1) selection with cached capability flags
        """
        # Import visualization components
        from visualization.visualization_selector import VisualizationSelector
        from visualization.visualization_state import VisualizationState
        from visualization.markdown_renderer import MarkdownRenderer
        from visualization.chart_dispatch import ChartDispatcher
        
        # Get or create visualization state
        if not hasattr(runtime_state, 'visualization'):
            runtime_state['visualization'] = VisualizationState()
        
        state = runtime_state['visualization']
        selector = VisualizationSelector()
        
        # O(1) selection based on cached capability flags
        level = selector.select(task, state)
        
        # Apply visualization rules
        if level.value == 'text':
            renderer = MarkdownRenderer()
            return renderer.render_unicode_chart(task.data)
        elif level.value == 'rich':
            dispatcher = ChartDispatcher()
            return dispatcher.dispatch(task)
        else:  # interactive
            return {
                'executor':'browser_dashboard',
                'dataset':task.input_ref
            }

    def adaptive_preemption_decision(self, agent_request, runtime_state):
        """Make preemption decisions with adaptive runtime scoring"""
        
        # Get current runtime metrics
        metrics = runtime_state.get("runtime_metrics", RuntimeMetrics())
        
        # Build decision context from the runtime state and request
        ctx = DecisionContext(
            task_score=runtime_state.get("task_score", 0.0),
            knowledge_score=runtime_state.get("knowledge_score", 0.0),
            context_score=runtime_state.get("context_score", 0.0),
            confidence_score=runtime_state.get("confidence_score", 0.0),
            dependency_score=runtime_state.get("dependency_score", 0.0),
            reuse_score=runtime_state.get("reuse_score", 0.0),
            merge_score=runtime_state.get("merge_score", 0.0),
            parallel_score=runtime_state.get("parallel_score", 0.0),
            prediction_score=runtime_state.get("prediction_score", 0.0),
            token_score=runtime_state.get("token_score", 0.0),
            resource_score=runtime_state.get("resource_score", 0.0)
        )
        
        # Evaluate request with adaptive scoring
        evaluation = evaluate_request(ctx, metrics)
        
        return evaluation

    def update_metrics_and_make_decision(self, runtime_state, result):
        """Update runtime metrics and make a decision based on current performance"""
        
        # Get current metrics
        metrics = runtime_state.get("runtime_metrics", RuntimeMetrics())
        
        # Update metrics with new results  
        update_runtime_metrics(metrics, result)
        
        # Update the runtime state with new metrics
        runtime_state["runtime_metrics"] = metrics
        
        # Get decision based on updated metrics
        decision = self.adaptive_preemption_decision(None, runtime_state)
        
        # Store in decision history (for learning purposes)
        if "decision_history" not in runtime_state:
            runtime_state["decision_history"] = []
        runtime_state["decision_history"].append(decision)
        
        return decision


# Logic gate implementations for enhanced preemption
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