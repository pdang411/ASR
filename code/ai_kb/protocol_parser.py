import re
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class UniversalTask:
    task_id: str
    intent: str
    type: str
    priority: int
    executor: str
    input_ref: str
    output_format: str
    media_type: str
    next_pipeline: str

def parse_universal_task(markdown_content: str) -> UniversalTask:
    """Parse universal task from markdown format"""
    # Extract sections
    task_match = re.search(r'#TASK(.*?)#INPUT', markdown_content, re.DOTALL)
    input_match = re.search(r'#INPUT(.*?)#OUTPUT', markdown_content, re.DOTALL)
    output_match = re.search(r'#OUTPUT(.*?)#MEDIA', markdown_content, re.DOTALL)
    media_match = re.search(r'#MEDIA(.*?)#NEXT', markdown_content, re.DOTALL)
    next_match = re.search(r'#NEXT(.*?)$', markdown_content, re.DOTALL)
    
    # Extract key-value pairs
    task_data = {}
    if task_match:
        for line in task_match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                task_data[key.strip()] = value.strip()
    
    input_data = {}
    if input_match:
        for line in input_match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                input_data[key.strip()] = value.strip()
    
    output_data = {}
    if output_match:
        for line in output_match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                output_data[key.strip()] = value.strip()
    
    media_data = {}
    if media_match:
        for line in media_match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                media_data[key.strip()] = value.strip()
    
    next_data = {}
    if next_match:
        for line in next_match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                next_data[key.strip()] = value.strip()
    
    return UniversalTask(
        task_id=task_data.get('id', ''),
        intent=task_data.get('intent', ''),
        type=task_data.get('type', ''),
        priority=int(task_data.get('priority', 0)),
        executor=task_data.get('executor', ''),
        input_ref=input_data.get('ref', ''),
        output_format=output_data.get('format', ''),
        media_type=media_data.get('type', ''),
        next_pipeline=next_data.get('pipeline', '')
    )

def create_universal_task(task_id: str, intent: str, task_type: str, priority: int,
                         executor: str, input_ref: str, output_format: str,
                         media_type: str, next_pipeline: str) -> str:
    """Create universal task in markdown format"""
    return f"""#TASK
id: {task_id}
intent: {intent}
type: {task_type}
priority: {priority}
executor: {executor}

#INPUT
ref: {input_ref}

#OUTPUT
format: {output_format}

#MEDIA
type: {media_type}

#NEXT
pipeline: {next_pipeline}
"""