from pydantic import BaseModel
from typing import List

class ResearchResult(BaseModel):
    query:str
    summary:str
    sources:List[str]
    capabilities:List[str]