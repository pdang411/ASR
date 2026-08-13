from dataclasses import dataclass

@dataclass(slots=True)
class RuntimeState:
    executor_cache: dict
    pipeline_cache: dict
    media_cache: dict
    context_cache: dict