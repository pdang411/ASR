from dataclasses import dataclass


@dataclass(slots=True)
class VisualizationState:
    preferred_level: str = "text"
    preferred_type: str = "markdown"
    chart_available: bool = False
    dashboard_available: bool = False
    cache_hits: int = 0
