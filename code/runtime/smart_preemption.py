from dataclasses import dataclass
from typing import Any

from runtime.chart_dispatch import ChartDispatcher
from runtime.markdown_renderer import MarkdownRenderer
from runtime.visualization import VisualizationLevel
from runtime.visualization_selector import VisualizationSelector
from runtime.visualization_state import VisualizationState


@dataclass
class RuntimeMetrics:
    cache_hit_rate: float = 0.0
    merge_success_rate: float = 0.0
    reasoning_success_rate: float = 0.0
    avg_token_cost: float = 0.0
    avg_latency_ms: float = 0.0
    parallel_utilization: float = 0.0


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


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _normalized_to_score(value: float) -> int:
    return int(round(_clamp01(value) * 10.0))


def ensure_runtime_cache(runtime_state: dict[str, Any]) -> dict[str, Any]:
    runtime_state.setdefault("runtime_metrics", RuntimeMetrics())
    runtime_state.setdefault("decision_history", [])
    runtime_state.setdefault("weight_history", [])
    runtime_state.setdefault("scores", RuntimeState())
    runtime_state.setdefault("last_update", 0.0)
    runtime_state.setdefault("decision_cache", {})
    runtime_state.setdefault("context_cache", {})
    return runtime_state


class RuntimeOptimizer:
    def compute_knowledge(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics")
        hit_rate = getattr(metrics, "cache_hit_rate", 0.0) if metrics is not None else 0.0
        return _normalized_to_score(hit_rate)

    def compute_context(self, runtime_cache: dict[str, Any]) -> int:
        context_cache = runtime_cache.get("context_cache", {})
        value = context_cache.get("context_fill_rate", 0.0) if isinstance(context_cache, dict) else 0.0
        return _normalized_to_score(float(value) if isinstance(value, (int, float)) else 0.0)

    def compute_confidence(self, runtime_cache: dict[str, Any]) -> int:
        context_cache = runtime_cache.get("context_cache", {})
        value = context_cache.get("confidence", 0.0) if isinstance(context_cache, dict) else 0.0
        return _normalized_to_score(float(value) if isinstance(value, (int, float)) else 0.0)

    def compute_dependency(self, runtime_cache: dict[str, Any]) -> int:
        context_cache = runtime_cache.get("context_cache", {})
        value = context_cache.get("dependency_completion", 1.0) if isinstance(context_cache, dict) else 1.0
        return _normalized_to_score(float(value) if isinstance(value, (int, float)) else 1.0)

    def compute_reuse(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics")
        value = getattr(metrics, "cache_hit_rate", 0.0) if metrics is not None else 0.0
        return _normalized_to_score(value)

    def compute_merge(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics")
        value = getattr(metrics, "merge_success_rate", 0.0) if metrics is not None else 0.0
        return _normalized_to_score(value)

    def compute_parallel(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics")
        value = getattr(metrics, "parallel_utilization", 0.0) if metrics is not None else 0.0
        return _normalized_to_score(value)

    def compute_prediction(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics")
        context_cache = runtime_cache.get("context_cache", {})
        success = getattr(metrics, "reasoning_success_rate", 0.0) if metrics is not None else 0.0
        bias = 0.0
        if isinstance(context_cache, dict):
            raw = context_cache.get("prediction_quality", 0.0)
            if isinstance(raw, (int, float)):
                bias = float(raw)
        return _normalized_to_score((float(success) + bias) / 2.0)

    def compute_token(self, runtime_cache: dict[str, Any]) -> int:
        metrics = runtime_cache.get("runtime_metrics")
        avg_token_cost = getattr(metrics, "avg_token_cost", 0.0) if metrics is not None else 0.0
        normalized = min(1.0, max(0.0, float(avg_token_cost) / 5000.0))
        return _normalized_to_score(normalized)

    def compute_resource(self, runtime_cache: dict[str, Any]) -> int:
        context_cache = runtime_cache.get("context_cache", {})
        if isinstance(context_cache, dict):
            available = context_cache.get("resource_available")
            if isinstance(available, bool):
                return 10 if available else 0
        return 10

    def update(self, aikb) -> RuntimeState:
        runtime_cache = ensure_runtime_cache(getattr(aikb, "runtime_state", {}))
        state = runtime_cache["scores"]

        state.knowledge_score = self.compute_knowledge(runtime_cache)
        state.context_score = self.compute_context(runtime_cache)
        state.confidence_score = self.compute_confidence(runtime_cache)
        state.dependency_score = self.compute_dependency(runtime_cache)
        state.reuse_score = self.compute_reuse(runtime_cache)
        state.merge_score = self.compute_merge(runtime_cache)
        state.parallel_score = self.compute_parallel(runtime_cache)
        state.prediction_score = self.compute_prediction(runtime_cache)
        state.token_score = self.compute_token(runtime_cache)
        state.resource_score = self.compute_resource(runtime_cache)
        return state


def tune_weights(weights: dict[str, float], metrics: RuntimeMetrics) -> dict[str, float]:
    tuned = dict(weights)

    def _add(key: str, delta: float) -> None:
        if key in tuned and isinstance(tuned[key], (int, float)):
            tuned[key] = float(tuned[key]) + float(delta)

    if metrics.cache_hit_rate > 0.80:
        _add("knowledge_factor", 0.10)
        _add("reuse_factor", 0.15)

    if metrics.parallel_utilization < 0.60:
        _add("parallel_factor", 0.20)

    if metrics.avg_token_cost > 2500:
        _add("token_factor", 0.20)

    if metrics.merge_success_rate > 0.50:
        _add("merge_factor", 0.15)

    return tuned


def next_best_action(score: float) -> str:
    if score >= 0.85:
        return "complete"
    if score >= 0.7:
        return "reuse_context"
    if score >= 0.55:
        return "merge_requests"
    if score >= 0.35:
        return "continue"
    if score >= 0.2:
        return "wait"
    return "request_llm"


def compute_decision_score(ctx: dict[str, Any]) -> float:
    factors = ctx.get("factors") if isinstance(ctx, dict) else None
    weights = ctx.get("weights") if isinstance(ctx, dict) else None
    if not isinstance(factors, dict) or not isinstance(weights, dict):
        return 0.0

    score = 0.0
    total_weight = 0.0
    for key, value in factors.items():
        if not isinstance(value, (int, float)):
            continue
        weight = weights.get(key, 0.0)
        if not isinstance(weight, (int, float)):
            continue
        score += float(value) * float(weight)
        total_weight += float(weight)

    if total_weight <= 0.0:
        return 0.0
    normalized = score / total_weight
    return max(0.0, min(1.0, normalized))


def evaluate_request(ctx: dict[str, Any], metrics: RuntimeMetrics) -> dict[str, Any]:
    base_weights = ctx.get("weights") if isinstance(ctx, dict) and isinstance(ctx.get("weights"), dict) else {}
    weights = tune_weights(base_weights, metrics)
    score = compute_decision_score({"factors": ctx.get("factors", {}), "weights": weights})
    return {
        "score": score,
        "weights": weights,
        "action": next_best_action(score),
    }


def update_runtime_metrics(metrics: RuntimeMetrics, result: Any) -> None:
    if isinstance(result, dict):
        for name in [
            "reasoning_success_rate",
            "avg_latency_ms",
            "avg_token_cost",
            "cache_hit_rate",
            "parallel_utilization",
            "merge_success_rate",
        ]:
            value = result.get(name)
            if isinstance(value, (int, float)):
                setattr(metrics, name, float(value))
        return

    for name in [
        "reasoning_success_rate",
        "avg_latency_ms",
        "avg_token_cost",
        "cache_hit_rate",
        "parallel_utilization",
        "merge_success_rate",
    ]:
        value = getattr(result, name, None)
        if isinstance(value, (int, float)):
            setattr(metrics, name, float(value))


def fast_decision(state: RuntimeState) -> str:
    score = (
        state.knowledge_score
        + state.context_score
        + state.confidence_score
        + state.dependency_score
        + state.reuse_score
        + state.merge_score
        + state.parallel_score
        + state.prediction_score
        + state.resource_score
        - state.token_score
    )

    normalized = max(0.0, min(1.0, (float(score) + 10.0) / 90.0))
    return next_best_action(normalized)


@dataclass
class SmartPreemptionDecision:
    score: float
    next_action: str
    factors: dict[str, float]
    weights: dict[str, float]
    token_estimate: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 6),
            "next_action": self.next_action,
            "factors": {k: round(v, 6) for k, v in self.factors.items()},
            "weights": {k: round(v, 6) for k, v in self.weights.items()},
            "token_estimate": self.token_estimate,
        }


class SmartPreemption:
    DEFAULT_WEIGHTS = {
        "task_factor": 0.08,
        "knowledge_factor": 0.14,
        "context_factor": 0.1,
        "confidence_factor": 0.08,
        "dependency_factor": 0.1,
        "reuse_factor": 0.1,
        "merge_factor": 0.08,
        "parallel_factor": 0.08,
        "prediction_factor": 0.07,
        "token_factor": 0.09,
        "resource_factor": 0.08,
    }

    def __init__(
        self,
        default_weights: dict[str, float] | None = None,
        runtime_state: Any | None = None,
        registry: Any | None = None,
    ):
        self.default_weights = dict(self.DEFAULT_WEIGHTS)
        self.state = runtime_state
        self.registry = registry
        self.visualization_selector = VisualizationSelector()
        self.markdown_renderer = MarkdownRenderer()
        self.chart_dispatcher = ChartDispatcher()
        if isinstance(default_weights, dict):
            for key, value in default_weights.items():
                if key in self.default_weights and isinstance(value, (int, float)):
                    self.default_weights[key] = float(value)

    def _visualization_requested(self, task) -> bool:
        media_type = str(getattr(task, "media_type", "") or "").strip().lower()
        output_format = str(getattr(task, "output_format", "") or "").strip().lower()
        if media_type in {"chart", "graph", "diagram", "dashboard"}:
            return True
        if output_format in {"chart", "graph", "diagram", "dashboard", "markdown", "ascii", "unicode"}:
            return True

        metadata = getattr(task, "metadata", None)
        if isinstance(metadata, dict):
            mode = str(metadata.get("visualization", "") or "").strip().lower()
            if mode in {"text", "rich", "interactive"}:
                return True
        return False

    def _series_for_task(self, task):
        if hasattr(task, "data"):
            return getattr(task, "data")
        metadata = getattr(task, "metadata", None)
        if isinstance(metadata, dict) and "series" in metadata:
            return metadata.get("series")
        return []

    def handle(self, task):
        """Dispatch UniversalTask via adapter registry using O(1) cache lookup only."""
        if self.state is None or self.registry is None:
            raise RuntimeError("SmartPreemption handle() requires runtime_state and registry")

        pipeline_cache = getattr(self.state, "pipeline_cache", {})
        if isinstance(pipeline_cache, dict):
            cached = pipeline_cache.get(getattr(task, "intent", ""))
            if isinstance(cached, str) and cached:
                task.pipeline = cached

        if self._visualization_requested(task):
            state = getattr(self.state, "visualization_state", None)
            if state is None:
                state = VisualizationState()
                setattr(self.state, "visualization_state", state)

            level = self.visualization_selector.select(task, state)
            state.cache_hits += 1

            if level is VisualizationLevel.TEXT:
                return self.markdown_renderer.render_unicode_chart(self._series_for_task(task))

            if level is VisualizationLevel.RICH:
                return self.chart_dispatcher.dispatch(task)

            return {
                "executor": "browser_dashboard",
                "dataset": getattr(task, "input_ref", ""),
            }

        return self.registry.dispatch(task)

    def _weights_for_task(self, task, metrics: RuntimeMetrics | None = None) -> dict[str, float]:
        weights = dict(self.default_weights)
        context = getattr(task, "context", {})
        override = context.get("preemption_weights") if isinstance(context, dict) else None
        if isinstance(override, dict):
            for key, value in override.items():
                if key in weights and isinstance(value, (int, float)):
                    weights[key] = float(value)
        if isinstance(metrics, RuntimeMetrics):
            weights = tune_weights(weights, metrics)
        return weights

    def _estimate_tokens(self, task) -> int:
        goal = str(getattr(task, "goal", ""))
        # Cheap deterministic approximation: 1 token ~= 4 chars.
        return max(1, len(goal) // 4)

    def _factor_task(self, task) -> float:
        capabilities = list(getattr(task, "capabilities", []) or [])
        flags = sum(
            [
                bool(getattr(task, "requires_research", False)),
                bool(getattr(task, "requires_analysis", False)),
                bool(getattr(task, "requires_planning", False)),
                bool(getattr(task, "requires_multi_agent", False)),
            ]
        )
        token_load = min(1.0, self._estimate_tokens(task) / 1200.0)
        capability_load = min(1.0, len(capabilities) / 8.0)
        flag_load = min(1.0, flags / 4.0)
        return (token_load + capability_load + flag_load) / 3.0

    def _factor_knowledge(self, task) -> float:
        context = getattr(task, "context", {})
        knowledge = context.get("knowledge") if isinstance(context, dict) else None
        if isinstance(knowledge, list):
            return min(1.0, len(knowledge) / 5.0)
        return 0.0

    def _factor_context(self, task) -> float:
        context = getattr(task, "context", {})
        if not isinstance(context, dict):
            return 0.0
        keys = ["knowledge", "history", "workflow", "capabilities", "research", "plan"]
        filled = 0
        for key in keys:
            value = context.get(key)
            if value not in (None, [], {}, ""):
                filled += 1
        return filled / float(len(keys))

    def _factor_confidence(self, task) -> float:
        context = getattr(task, "context", {})
        if isinstance(context, dict):
            confidence = context.get("confidence")
            if isinstance(confidence, (int, float)):
                return max(0.0, min(1.0, float(confidence)))
        return 0.5

    def _factor_dependency(self, task) -> float:
        context = getattr(task, "context", {})
        deps = context.get("dependencies") if isinstance(context, dict) else None
        if isinstance(deps, list) and deps:
            complete = 0
            for dep in deps:
                if isinstance(dep, dict):
                    if dep.get("complete") is True:
                        complete += 1
                elif dep is True:
                    complete += 1
            return complete / float(len(deps))
        return 1.0

    def _factor_reuse(self, task) -> float:
        context = getattr(task, "context", {})
        history = context.get("history") if isinstance(context, dict) else None
        if isinstance(history, list):
            return min(1.0, len(history) / 5.0)
        return 0.0

    def _factor_merge(self, task) -> float:
        context = getattr(task, "context", {})
        candidates = context.get("merge_candidates") if isinstance(context, dict) else None
        if isinstance(candidates, list):
            return min(1.0, len(candidates) / 4.0)
        roles = list(getattr(task, "roles", []) or [])
        return 0.8 if len(roles) > 1 else 0.2

    def _factor_parallel(self, task) -> float:
        context = getattr(task, "context", {})
        parallelizable = context.get("parallelizable") if isinstance(context, dict) else None
        if isinstance(parallelizable, bool):
            return 1.0 if parallelizable else 0.0
        roles = list(getattr(task, "roles", []) or [])
        return 1.0 if len(roles) > 1 else 0.4

    def _factor_prediction(self, factors: dict[str, float]) -> float:
        # If context/reuse/parallel are strong, delaying expensive reasoning often helps throughput.
        return (factors["context_factor"] + factors["reuse_factor"] + factors["parallel_factor"]) / 3.0

    def _factor_token(self, task) -> float:
        tokens = self._estimate_tokens(task)
        # Lower score means cheaper to reason now.
        normalized = min(1.0, tokens / 4000.0)
        return 1.0 - normalized

    def _factor_resource(self, task) -> float:
        context = getattr(task, "context", {})
        available = context.get("reasoning_resource_available") if isinstance(context, dict) else None
        if isinstance(available, bool):
            return 1.0 if available else 0.0
        return 1.0

    def _next_action(self, factors: dict[str, float], score: float, task) -> str:
        context = getattr(task, "context", {})
        if factors["dependency_factor"] < 0.5:
            return "wait"
        if factors["reuse_factor"] >= 0.7:
            return "reuse_context"
        if factors["merge_factor"] >= 0.75 and factors["parallel_factor"] >= 0.7:
            return "merge_requests"
        if factors["resource_factor"] < 0.5:
            return "wait"
        if isinstance(context, dict) and context.get("allow_preempt_complete") is True and score >= 0.85:
            return "complete"
        if score < 0.45 and factors["token_factor"] >= 0.4:
            return "request_llm"
        return "continue"

    def decide(self, task, metrics: RuntimeMetrics | None = None) -> SmartPreemptionDecision:
        factors: dict[str, float] = {
            "task_factor": self._factor_task(task),
            "knowledge_factor": self._factor_knowledge(task),
            "context_factor": self._factor_context(task),
            "confidence_factor": self._factor_confidence(task),
            "dependency_factor": self._factor_dependency(task),
            "reuse_factor": self._factor_reuse(task),
            "merge_factor": self._factor_merge(task),
            "parallel_factor": self._factor_parallel(task),
            "token_factor": self._factor_token(task),
            "resource_factor": self._factor_resource(task),
        }
        factors["prediction_factor"] = self._factor_prediction(factors)

        weights = self._weights_for_task(task, metrics=metrics)
        score = 0.0
        for key, value in factors.items():
            score += value * weights.get(key, 0.0)

        total_weight = sum(weights.values()) or 1.0
        score = max(0.0, min(1.0, score / total_weight))
        action = self._next_action(factors, score, task)

        return SmartPreemptionDecision(
            score=score,
            next_action=action,
            factors=factors,
            weights=weights,
            token_estimate=self._estimate_tokens(task),
        )
