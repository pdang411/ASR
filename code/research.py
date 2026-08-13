import time
from dataclasses import dataclass


@dataclass
class ResearchPolicyDecision:
    model_failure_count: int
    max_model_failures_before_webfetch: int
    llm_attempts_remaining_before_webfetch: int
    webfetch_allowed: bool
    next_action: str

    def to_dict(self) -> dict:
        return {
            "model_failure_count": self.model_failure_count,
            "max_model_failures_before_webfetch": self.max_model_failures_before_webfetch,
            "llm_attempts_remaining_before_webfetch": self.llm_attempts_remaining_before_webfetch,
            "webfetch_allowed": self.webfetch_allowed,
            "next_action": self.next_action,
        }


class ResearchPolicy:
    """Stateful policy gate for model-first research attempts.

    Policy:
    - Track consecutive no-match failures per normalized query.
    - Allow webfetch only after 3 model failures for the same query.
    - Reset failure count when the query gets a match.
    """

    def __init__(self, max_model_failures_before_webfetch: int = 3, ttl_seconds: float = 3600.0):
        self.max_model_failures_before_webfetch = max(1, int(max_model_failures_before_webfetch))
        self.ttl_seconds = max(60.0, float(ttl_seconds))
        self._state: dict[str, tuple[int, float]] = {}

    def _normalize_query(self, query: str) -> str:
        return " ".join(query.lower().strip().split())

    def _gc(self, now: float) -> None:
        expired = [key for key, (_, ts) in self._state.items() if now - ts > self.ttl_seconds]
        for key in expired:
            self._state.pop(key, None)

    def evaluate(self, query: str, has_matches: bool) -> ResearchPolicyDecision:
        now = time.monotonic()
        self._gc(now)

        key = self._normalize_query(query)
        if not key:
            return ResearchPolicyDecision(
                model_failure_count=0,
                max_model_failures_before_webfetch=self.max_model_failures_before_webfetch,
                llm_attempts_remaining_before_webfetch=self.max_model_failures_before_webfetch,
                webfetch_allowed=False,
                next_action="retry_model",
            )

        failures, _ = self._state.get(key, (0, now))
        if has_matches:
            self._state.pop(key, None)
            return ResearchPolicyDecision(
                model_failure_count=0,
                max_model_failures_before_webfetch=self.max_model_failures_before_webfetch,
                llm_attempts_remaining_before_webfetch=self.max_model_failures_before_webfetch,
                webfetch_allowed=False,
                next_action="use_matches",
            )

        failures += 1
        self._state[key] = (failures, now)
        llm_attempts_remaining = max(0, self.max_model_failures_before_webfetch - failures)
        webfetch_allowed = failures >= self.max_model_failures_before_webfetch
        return ResearchPolicyDecision(
            model_failure_count=failures,
            max_model_failures_before_webfetch=self.max_model_failures_before_webfetch,
            llm_attempts_remaining_before_webfetch=llm_attempts_remaining,
            webfetch_allowed=webfetch_allowed,
            next_action="allow_webfetch" if webfetch_allowed else "retry_model",
        )
