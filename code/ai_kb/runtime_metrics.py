from dataclasses import dataclass

@dataclass
class RuntimeMetrics:
    cache_hit_rate: float = 0.0
    merge_success_rate: float = 0.0
    reasoning_success_rate: float = 0.0
    avg_token_cost: float = 0.0
    avg_latency_ms: float = 0.0
    parallel_utilization: float = 0.0

def tune_weights(weights, metrics):
    tuned = weights.copy()

    if metrics.cache_hit_rate > 0.80:
        tuned["knowledge"] += 0.10
        tuned["reuse"] += 0.15

    if metrics.parallel_utilization < 0.60:
        tuned["parallel"] += 0.20

    if metrics.avg_token_cost > 2500:
        tuned["token"] += 0.20

    if metrics.merge_success_rate > 0.50:
        tuned["merge"] += 0.15

    return tuned

def evaluate_request(ctx, metrics):
    weights = tune_weights(DECISION_WEIGHTS, metrics)
    score = compute_decision_score(ctx)

    return {
        "score": score,
        "weights": weights,
        "action": next_best_action(score)
    }

def update_runtime_metrics(metrics, result):
    metrics.reasoning_success_rate = result.reasoning_success_rate
    metrics.avg_latency_ms = result.avg_latency_ms
    metrics.avg_token_cost = result.avg_token_cost
    metrics.cache_hit_rate = result.cache_hit_rate
    metrics.parallel_utilization = result.parallel_utilization
    metrics.merge_success_rate = result.merge_success_rate