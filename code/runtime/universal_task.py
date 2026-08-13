from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class UniversalTask:
    task_id: str
    task_type: str
    intent: str
    priority: int
    executor: str
    pipeline: str = ""
    input_ref: str = ""
    kb_ref: str = ""
    output_format: str = ""
    media_type: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
