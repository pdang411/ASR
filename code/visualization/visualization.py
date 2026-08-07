from enum import Enum

class VisualizationLevel(Enum):
    TEXT='text'
    RICH='rich'
    INTERACTIVE='interactive'

class VisualizationType(Enum):
    MARKDOWN='markdown'
    ASCII='ascii'
    UNICODE='unicode'
    CHART='chart'
    GRAPH='graph'
    DASHBOARD='dashboard'