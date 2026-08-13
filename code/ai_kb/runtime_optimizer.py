from dataclasses import dataclass
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _normalized_to_score(value: float) -> int:
    return int(round(_clamp01(value) * 10.0))


def _read_metric(metrics: Any, name: str) -> float:
    if isinstance(metrics, dict):
        value = metrics.get(name, 0.0)
    else:
        value = getattr(metrics, name, 0.0)
    return float(value) if isinstance(value, (int, float)) else 0.0


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


def ensure_runtime_cache(runtime_state: dict[str, Any]) -> dict[str, Any]:
    runtime_state.setdefault("runtime_metrics", {})
    runtime_state.setdefault("decision_history", [])
    runtime_state.setdefault("weight_history", [])
    runtime_state.setdefault("scores", RuntimeState())
    runtime_state.setdefault("last_update", 0.0)
    runtime_state.setdefault("decision_cache", {})
    runtime_state.setdefault("context_cache", {})
    return runtime_state


class RuntimeOptimizer:
    def update(self, aikb) -> RuntimeState:
        runtime_cache = ensure_runtime_cache(getattr(aikb, "runtime_state", {}))
        scores = runtime_cache["scores"]

        scores.knowledge_score = self.compute_knowledge(runtime_cache)
        scores.context_score = self.compute_context(runtime_cache)
        scores.confidence_score = self.compute_confidence(runtime_cache)
        scores.dependency_score = self.compute_dependency(runtime_cache)
        scores.reuse_score = self.compute_reuse(runtime_cache)
        scores.merge_score = self.compute_merge(runtime_cache)
        scores.parallel_score = self.compute_parallel(runtime_cache)
        scores.prediction_score = self.compute_prediction(runtime_cache)
        scores.token_score = self.compute_token(runtime_cache)
        scores.resource_score = self.compute_resource(runtime_cache)

        import time

        runtime_cache["last_update"] = time.time()
        return scores

    def compute_knowledge(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics", {})
        return _normalized_to_score(_read_metric(metrics, "cache_hit_rate"))

    def compute_context(self, runtime_cache: dict[str, Any]) -> int:
        context_cache = runtime_cache.get("context_cache", {})
        fill_rate = context_cache.get("context_fill_rate", runtime_cache.get("context_score", 0.0))
        return _normalized_to_score(float(fill_rate) if isinstance(fill_rate, (int, float)) else 0.0)

    def compute_confidence(self, runtime_cache: dict[str, Any]) -> int:
        context_cache = runtime_cache.get("context_cache", {})
        if isinstance(context_cache, dict) and isinstance(context_cache.get("confidence"), (int, float)):
            return _normalized_to_score(float(context_cache["confidence"]))

        confidence = runtime_cache.get("confidence", {})
        if isinstance(confidence, dict) and confidence:
            values = [float(v) for v in confidence.values() if isinstance(v, (int, float))]
            if values:
                return _normalized_to_score(sum(values) / len(values))
        return 0

    def compute_dependency(self, runtime_cache: dict[str, Any]) -> int:
        context_cache = runtime_cache.get("context_cache", {})
        completion = context_cache.get("dependency_completion") if isinstance(context_cache, dict) else None
        if isinstance(completion, (int, float)):
            return _normalized_to_score(float(completion))

        dependencies = runtime_cache.get("dependency_status", {})
        if isinstance(dependencies, dict) and dependencies:
            completed = sum(1 for dep in dependencies.values() if isinstance(dep, dict) and dep.get("completed", False))
            return _normalized_to_score(completed / float(len(dependencies)))
        return 10

    def compute_reuse(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics", {})
        hit_rate = _read_metric(metrics, "cache_hit_rate")
        if hit_rate > 0.0:
            return _normalized_to_score(hit_rate)
        raw = runtime_cache.get("reuse_score", 0.0)
        return _normalized_to_score(float(raw) if isinstance(raw, (int, float)) else 0.0)

    def compute_merge(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics", {})
        success_rate = _read_metric(metrics, "merge_success_rate")
        if success_rate > 0.0:
            return _normalized_to_score(success_rate)
        raw = runtime_cache.get("merge_score", 0.0)
        return _normalized_to_score(float(raw) if isinstance(raw, (int, float)) else 0.0)

    def compute_parallel(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics", {})
        utilization = _read_metric(metrics, "parallel_utilization")
        if utilization > 0.0:
            return _normalized_to_score(utilization)

        agents = runtime_cache.get("agent_state", {})
        if isinstance(agents, dict) and agents:
            running_agents = [a for a in agents.values() if isinstance(a, dict) and a.get("status") == "running"]
            return min(10, len(running_agents) * 2)
        return 0

    def compute_prediction(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics", {})
        success = _read_metric(metrics, "reasoning_success_rate")

        context_cache = runtime_cache.get("context_cache", {})
        bias = 0.0
        if isinstance(context_cache, dict):
            value = context_cache.get("prediction_quality", runtime_cache.get("prediction_score", 0.0))
            if isinstance(value, (int, float)):
                bias = float(value)

        if success > 0.0 or bias > 0.0:
            return _normalized_to_score((success + bias) / 2.0)
        return 0

    def compute_token(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics", {})
        avg_token_cost = _read_metric(metrics, "avg_token_cost")
        if avg_token_cost > 0.0:
            normalized = min(1.0, max(0.0, avg_token_cost / 5000.0))
            return _normalized_to_score(normalized)

        raw = runtime_cache.get("token_score", 0.0)
        if isinstance(raw, (int, float)):
            if raw > 10.0:
                normalized = min(1.0, max(0.0, raw / 5000.0))
                return _normalized_to_score(normalized)
            return int(max(0.0, min(10.0, float(raw))))
        return 0

    def compute_resource(self, runtime_cache: dict[str, Any]) -> int:
        context_cache = runtime_cache.get("context_cache", {})
        if isinstance(context_cache, dict):
            available = context_cache.get("resource_available")
            if isinstance(available, bool):
                return 10 if available else 0

        raw = runtime_cache.get("resource_score", 1.0)
        return _normalized_to_score(float(raw) if isinstance(raw, (int, float)) else 1.0)