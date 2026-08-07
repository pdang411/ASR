from dataclasses import dataclass

@dataclass(slots=True)
class VisualizationState:
    preferred_level='text'
    preferred_type='markdown'
    chart_available=False
    dashboard_available=False
    cache_hits=0