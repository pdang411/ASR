"""
Agent Task Layer implementation for ASR MCP Server
This file contains all the agent task layer components that can be imported 
without causing circular imports in main.py
"""

import uuid
from task_parser import AgentTaskParser
from task_validator import TaskValidator
from task_router import TaskRouter
from task_executor import TaskExecutor
from workflow_engine import WorkflowEngine
from agent_task.task_models import AgentTask
from agent_task.task_decomposer import TaskDecomposer
from agent_task.executor_registry import ExecutorRegistry
from agent_task.analyst import Analyst
from agent_task.coder import Coder
from agent_task.controller import Controller
from agent_task.researcher import ResearchAgent
from agent_task.research_router import ResearchRouter
from agent_task.task_request import TaskRequest
from agent_task.task_capabilities import Capability
from agent_task.task_classifier import TaskClassifier
from agent_task.fast_dispatcher import FastDispatcher
from agent_task.smart_pipeline import SmartPipeline

# Initialize base components
parser = AgentTaskParser()
validator = TaskValidator()
router = TaskRouter()
workflow_engine = WorkflowEngine()
executor = TaskExecutor(workflow_engine)

# Initialize Agent Task Layer components
decomposer = TaskDecomposer()
registry = ExecutorRegistry()
analyst = Analyst()
coder = Coder()
controller = Controller()

# Initialize Research Agent components
research_router = ResearchRouter()

def process_agent_task(user_prompt):
    """Process an agent task through the full pipeline"""
    # Compile prompt into task
    task = parser.compile(user_prompt)
    
    # Validate task
    validator.validate(task)
    
    # Select executor based on capabilities
    task.executor = router.select_executor(task)
    
    # Execute task
    result = executor.execute(task)
    
    return result

def process_agent_task_layer(prompt):
    """Process an agent task through the agent task layer"""
    # Create initial task
    task = parser.compile(prompt)
    task.id = str(uuid.uuid4())  # Assign unique ID
    
    # Decompose into subtasks
    subtasks = decomposer.split(task)
    
    results = []
    
    # Execute each subtask with appropriate executor
    for subtask in subtasks:
        subtask.executor = registry.resolve(subtask.role)
        # This would be more complex in reality, but for simplicity we execute them directly
        if subtask.role == "analyst":
            result = analyst.execute(subtask, None)  # AI KB would be injected here
        elif subtask.role == "coder":
            result = coder.execute(subtask)
        elif subtask.role == "controller":
            # Controller is not executable but used for merging results
            result = {"role": "controller", "status": "processed"}
        
        results.append(result)
    
    # Merge results
    final_result = controller.merge(results)
    
    return final_result

def process_research_task(prompt, aikb):
    """
    Process a research task through the researcher agent
    This integrates with the main workflow engine
    """
    # Create a task request with capabilities
    task_request = TaskRequest(
        intent="research",
        goal=prompt,
        capabilities=[Capability.KNOWLEDGE_SEARCH]
    )
    
    # Execute research agent  
    research_agent = ResearchAgent(aikb, registry)
    research_result = research_agent.execute(task_request)
    
    # Add research to task context
    task_request.context['research'] = research_result
    
    # Execute using workflow engine - here we just return the result
    # In a real implementation this would connect back to the workflow
    return {
        "task": task_request.dict(),
        "research": research_result
    }

def process_capability_task(prompt):
    """
    Process a capability-based task through the system
    """
    # Create a task with capabilities
    task_request = TaskRequest(
        intent="capability",
        goal=prompt,
        capabilities=[Capability.KNOWLEDGE_SEARCH]
    )
    
    # Resolve capabilities to executors
    executors = []
    for cap in task_request.capabilities:
        executor = registry.resolve(cap)
        executors.append({
            "capability": cap,
            "executor": executor
        })
    
    return {
        "task": task_request.dict(),
        "executors": executors
    }