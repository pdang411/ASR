import hashlib
from typing import Dict, Any, Optional
from .protocol_parser import UniversalTask, create_universal_task, parse_universal_task

class UniversalProtocolHandler:
    """Handles universal internal communication protocol"""
    
    def __init__(self):
        self.task_templates = {}
        self.context_references = {}
        self.media_cache = {}
    
    def process_task(self, input_data: Dict[str, Any], media_type: str) -> str:
        """
        Process task through universal protocol
        Returns markdown task string for dispatch
        """
        # Create unique task ID
        task_hash = hashlib.md5(str(input_data).encode()).hexdigest()
        
        # Determine task intent based on content
        intent = self._determine_intent(input_data)
        
        # Create universal task
        task_markdown = create_universal_task(
            task_id=task_hash,
            intent=intent,
            task_type=self._determine_task_type(input_data),
            priority=self._calculate_priority(input_data),
            executor=self._select_executor(input_data),
            input_ref=self._create_input_reference(input_data),
            output_format=self._determine_output_format(input_data),
            media_type=media_type,
            next_pipeline=self._select_next_pipeline(input_data)
        )
        
        return task_markdown
    
    def _determine_intent(self, input_data: Dict[str, Any]) -> str:
        """Determine task intent based on data type"""
        if 'source_code' in input_data:
            return 'code_generation'
        elif 'configuration' in input_data:
            return 'config_management'
        elif 'media_file' in input_data:
            return 'media_processing'
        else:
            return 'task_processing'
    
    def _determine_task_type(self, input_data: Dict[str, Any]) -> str:
        """Determine task type based on data content"""
        if 'source_code' in input_data:
            return 'code'
        elif 'config_file' in input_data:
            return 'configuration'
        elif 'image' in input_data or 'video' in input_data:
            return 'media'
        elif 'sql_query' in input_data:
            return 'database'
        else:
            return 'generic'
    
    def _calculate_priority(self, input_data: Dict[str, Any]) -> int:
        """Calculate task priority based on data characteristics"""
        # Simple priority calculation
        if 'urgent' in input_data:
            return 5
        elif 'important' in input_data:
            return 4
        elif 'normal' in input_data:
            return 3
        else:
            return 2
    
    def _select_executor(self, input_data: Dict[str, Any]) -> str:
        """Select appropriate executor based on task type"""
        if 'source_code' in input_data:
            return 'code_executor'
        elif 'config_file' in input_data:
            return 'config_executor'
        elif 'image' in input_data or 'video' in input_data:
            return 'media_executor'
        elif 'sql_query' in input_data:
            return 'database_executor'
        else:
            return 'generic_executor'
    
    def _create_input_reference(self, input_data: Dict[str, Any]) -> str:
        """Create reference for large inputs (never inline)"""
        # Create hash of input data and store reference
        input_hash = hashlib.md5(str(input_data).encode()).hexdigest()
        self.context_references[input_hash] = input_data.copy()
        return f"ref://{input_hash}"
    
    def _determine_output_format(self, input_data: Dict[str, Any]) -> str:
        """Determine output format for task"""
        if 'source_code' in input_data or 'config_file' in input_data:
            return 'markdown'
        elif 'image' in input_data:
            return 'image'
        elif 'video' in input_data:
            return 'video'
        elif 'sql_query' in input_data:
            return 'sql'
        else:
            return 'text'
    
    def _select_next_pipeline(self, input_data: Dict[str, Any]) -> str:
        """Select next pipeline based on task type"""
        if 'source_code' in input_data:
            return 'code_pipeline'
        elif 'config_file' in input_data:
            return 'config_pipeline'  
        elif 'media_file' in input_data:
            return 'media_pipeline'
        else:
            return 'default_pipeline'
    
    def process_result(self, result_markdown: str) -> Dict[str, Any]:
        """Process universal result and convert back to structured data"""
        task = parse_universal_task(result_markdown)
        
        # Convert back to structured format
        result_data = {
            'task_id': task.task_id,
            'intent': task.intent,
            'type': task.type,
            'priority': task.priority,
            'executor': task.executor,
            'input_ref': task.input_ref,
            'output_format': task.output_format,
            'media_type': task.media_type,
            'next_pipeline': task.next_pipeline,
            'payload': self._get_payload_from_reference(task.input_ref)
        }
        
        return result_data
    
    def _get_payload_from_reference(self, reference: str) -> Dict[str, Any]:
        """Get payload data from reference"""
        # Extract hash from reference
        if reference.startswith('ref://'):
            ref_hash = reference[6:]  # Remove 'ref://' prefix
            return self.context_references.get(ref_hash, {})
        return {}