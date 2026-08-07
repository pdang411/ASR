from pydantic import BaseModel
from typing import List
from .task_capabilities import Capability

class TaskRequest(BaseModel):
    intent:str
    goal:str
    capabilities:List[Capability]
    mode: str = "smart"  # Default to smart path