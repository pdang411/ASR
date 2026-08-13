from pydantic import BaseModel, Field
from typing import Dict, List, Any

class AgentTask(BaseModel):
    id:str
    intent:str
    goal:str
    role:str
    executor:str=""
    capabilities:List[str]=Field(default_factory=list)
    context:Dict[str,Any]=Field(default_factory=dict)