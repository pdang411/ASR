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