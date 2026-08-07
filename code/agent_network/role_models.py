from enum import Enum

class AgentRole(str, Enum):
    CONTROLLER="controller"
    PLANNER="planner"
    RESEARCHER="researcher"
    ANALYST="analyst"
    CODER="coder"
    REVIEWER="reviewer"
    TESTER="tester"
    CAD="cad"