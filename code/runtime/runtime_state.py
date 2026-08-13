from dataclasses import dataclass, field
from typing import Any

from runtime.visualization_state import VisualizationState


@dataclass(slots=True)
class RuntimeState:
    executor_cache: dict[str, Any] = field(default_factory=dict)
    pipeline_cache: dict[str, str] = field(default_factory=dict)
    media_cache: dict[str, Any] = field(default_factory=dict)
    context_cache: dict[str, Any] = field(default_factory=dict)
    visualization_state: VisualizationState = field(default_factory=VisualizationState)
