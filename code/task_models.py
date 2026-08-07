from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class AgentTask(BaseModel):
    intent:str
    goal:str
    executor:Optional[str]=None
    capabilities:List[str]=[]
    context:Dict[str,Any]={}
    payload:Dict[str,Any]={}