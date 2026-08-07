# Runtime integration

from agent_task.task_request import TaskRequest
from agent_task.task_classifier import TaskClassifier
from agent_task.fast_dispatcher import FastDispatcher
from agent_task.smart_pipeline import SmartPipeline
from runtime.executor_registry import ExecutorRegistry
from performance.runtime_profiler import RuntimeProfiler
from performance.intent_optimizer import IntentOptimizer
from performance.provider_health import ProviderHealth
from llm.session_manager import SessionManager
from llm.keepalive import KeepAlive
from llm.provider_pool import ProviderPool
from llm.warmup import Warmup
from llm.session_pool import SessionPool
from llm.model_switch import ModelSwitcher
from llm.session_state import SessionState

# AI.KB components
from ai_kb.knowledge_service import KnowledgeService
from ai_kb.task_memory import TaskMemory
from ai_kb.workflow_memory import WorkflowMemory
from ai_kb.capability_index import CapabilityIndex
from ai_kb.memory_router import MemoryRouter
from ai_kb.knowledge_cards import KnowledgeCards
from ai_kb.decision_context import DecisionContext
from ai_kb.decision_weights import DECISION_WEIGHTS
from ai_kb.runtime_metrics import RuntimeMetrics, tune_weights, evaluate_request, update_runtime_metrics
from ai_kb.runtime_optimizer import RuntimeState, RuntimeOptimizer
from ai_kb.protocol_handler import UniversalProtocolHandler
from ai_kb.universal_task import UniversalTask
from ai_kb.runtime_state import RuntimeState

# Visualization engine components
from visualization.visualization import VisualizationLevel, VisualizationType
from visualization.visualization_state import VisualizationState
from visualization.visualization_selector import VisualizationSelector
from visualization.markdown_renderer import MarkdownRenderer
from visualization.chart_dispatch import ChartDispatcher

# Agent Network components
from agent_network.agent_registry import AgentRegistry
from agent_network.network_controller import NetworkController
from agent_network.shared_context import SharedContext
from agent_network.role_models import AgentRole
from agent_network.guidance_agent import GuidanceAgent
from agent_network.event_bus import EventBus
from agent_network.proactive_rules import RULES

# Global components for LLM session management
provider_pool = ProviderPool()
session_manager = None
keepalive = None
session_pool = SessionPool()
model_switcher = ModelSwitcher()

def setup_llm_session(provider):
    """Setup LLM session management at startup"""
    global session_manager, keepalive
    
    # Register provider in pool
    provider_pool.register("default", provider)
    
    # Create session manager
    session_manager = SessionManager(provider)
    
    # Warm up the session
    Warmup().initialize(session_manager)
    
    # Start keep-alive thread
    keepalive = KeepAlive(provider, interval=30)
    keepalive.start()
    
    return True

def process_task_with_performance_monitoring(prompt):
    """Process a task using fast path optimization with performance monitoring"""
    
    # Initialize performance components
    profiler = RuntimeProfiler()
    optimizer = IntentOptimizer()
    health = ProviderHealth()
    
    # Initialize AI.KB components
    knowledge_service = KnowledgeService(None, None)  # These would be real implementations
    task_memory = TaskMemory()
    workflow_memory = WorkflowMemory()  
    capability_index = CapabilityIndex()
    memory_router = MemoryRouter()
    
    # Start profiling
    profiler.start("request")
    
    # Parse the prompt into a task request (simplified)
    task = TaskRequest(
        intent="task",
        goal=prompt,
        capabilities=[],  # Default empty capabilities
        mode="smart"  # Default to smart path, will be updated below
    )
    
    # Classify the task based on intent
    classifier = TaskClassifier()
    task.mode = classifier.classify(task)
    
    # Build context using AI.KB components
    context = memory_router.build_context(task)
    
    # Query knowledge service for additional information
    knowledge_result = knowledge_service.query(prompt)
    context["knowledge"] = knowledge_result
    
    # Add to context from task memory and workflow memory
    context["history"] = task_memory.similar(task.goal)
    context["workflow"] = workflow_memory.load_template(task.intent)
    
    # Get capabilities from index
    capabilities = capability_index.lookup(task.intent)
    context["capabilities"] = capabilities
    
    # Update task with context for additional processing
    task.context = context
    
    # Create components
    dispatcher = FastDispatcher()
    smart_pipeline = SmartPipeline()
    runtime = ExecutorRegistry()  # Using registry as a mock runtime
    
    # Profile task classification
    profiler.start("classification")
    task.mode = classifier.classify(task)
    profiler.stop("classification")
    
    # Dispatch using appropriate pipeline
    profiler.start("dispatch")
    if optimizer.use_fast_path(task.intent):
        result = runtime.execute(task)
        # Update metrics - this would increment fast_count in real implementation
    else:
        result = smart_pipeline.execute(task)
        # Update metrics - this would increment smart_count in real implementation
    
    profiler.stop("dispatch")
    
    # Calculate total elapsed time
    total_elapsed = profiler.stop("request")
    
    # Update health status (mock update)
    health.update("runtime", total_elapsed, True)
    
    # Save to task memory
    task_memory.save(task, result)
    
    return {
        "task": task.dict(),
        "mode": task.mode,
        "dispatched_to": "runtime" if task.mode == "fast" else "smart_pipeline",
        "result": result,
        "profiling": profiler.get_stage_times(),
        "total_latency_ms": total_elapsed
    }

# Integration with the architecture as described:
# LLM
#  ↓
# Agent Task Compiler
#  ↓
# AI.KB Knowledge Service
#  ↓
# Task Context Builder  
#  ↓
# Workflow Engine
#  ↓
# Runtime
#  ↓
# Executor Registry
#  ↓
# MCP Providers

def process_with_ai_kb_integration(prompt):
    """Execute the complete task processing pipeline with AI.KB integration"""
    
    # Initialize AI.KB components
    knowledge_service = KnowledgeService(None, None)  # These would be real implementations
    task_memory = TaskMemory()
    workflow_memory = WorkflowMemory()  
    capability_index = CapabilityIndex()
    memory_router = MemoryRouter()
    
    # Compile the prompt into a task using Agent Task Compiler (simplified)
    task = TaskRequest(
        intent="task",
        goal=prompt,
        capabilities=[],  # Default empty capabilities
        mode="smart"  # Default to smart path, will be updated below
    )
    
    # Build context using AI.KB components
    task.context = memory_router.build_context(task)
    
    # Query knowledge service 
    knowledge_result = knowledge_service.query(prompt)
    task.context["knowledge"] = knowledge_result
    
    # Get capabilities from index
    capabilities = capability_index.lookup(task.intent)
    task.context["capabilities"] = capabilities
    
    # For the workflow engine execution, we'll use the runtime here
    runtime = ExecutorRegistry()
    
    # Execute the task through the workflow engine (mocked)
    result = runtime.execute(task)
    
    # Save to task memory
    task_memory.save(task, result)
    
    return result

def process_llm_request(prompt):
    """Process an LLM request using session manager"""
    global session_manager
    
    if session_manager is None:
        raise Exception("LLM session not initialized. Call setup_llm_session first.")
    
    # Use the session manager to generate response
    result = session_manager.generate(prompt)
    return result

def switch_model(provider, model):
    """Switch to a different model/provider"""
    global session_pool, model_switcher
    
    # Perform model switching
    session = model_switcher.switch(runtime, provider, model)
    
    # Return the new active session
    return session

def process_llm_request(prompt):
    """Process an LLM request using session manager"""
    global session_manager
    
    if session_manager is None:
        raise Exception("LLM session not initialized. Call setup_llm_session first.")
    
    # Use the session manager to generate response
    result = session_manager.generate(prompt)
    return result

# Agent Network Integration
def process_with_agent_network(prompt):
    """Execute task through agent network"""
    
    # Initialize components
    registry = AgentRegistry()
    runtime = ExecutorRegistry()
    
    # For demonstration, creating mock agent objects as they'd be in real system
    # In practice these will be proper agent instances
    
    # This would be where you actually import and instantiate the agents properly
    # researcher = ResearcherAgent() 
    # analyst = AnalystAgent()
    # coder = CoderAgent()  
    # reviewer = ReviewerAgent()
    
    # For now we'll use placeholders to demonstrate integration
    try:
        from agent_task.researcher import ResearcherAgent
        from agent_task.analyst import AnalystAgent
        from agent_task.coder import CoderAgent
        from agent_task.reviewer import ReviewerAgent
        
        researcher = ResearcherAgent()
        analyst = AnalystAgent() 
        coder = CoderAgent()
        reviewer = ReviewerAgent()
    except:
        # Fall back to None agents for demonstration
        researcher = None
        analyst = None
        coder = None
        reviewer = None
    
    controller = NetworkController(registry, runtime)
    
    # Register the agents  
    registry.register("researcher", researcher)
    registry.register("analyst", analyst)
    registry.register("coder", coder)
    registry.register("reviewer", reviewer)
    
    # Create task with roles
    task = TaskRequest(
        intent="task",
        goal=prompt,
        capabilities=[],
        mode="smart"
    )
    task.roles = ["researcher","analyst","coder","reviewer"]
    
    # Execute through network
    results = controller.execute(task)
    
    # Return aggregate result - in real implementation this would be more sophisticated
    return results


# Guidance Agent Integration
def setup_guidance_agent():
    """Initialize and configure the autonomous guidance agent"""
    # Create AI.KB knowledge cards instance 
    knowledge_cards = KnowledgeCards()
    
    # Create guidance agent with knowledge base
    guidance_agent = GuidanceAgent(knowledge_cards)
    
    # Create event bus 
    event_bus = EventBus()
    
    # Subscribe guidance agent to event bus
    event_bus.subscribe(guidance_agent)
    
    return guidance_agent, event_bus


def process_with_guidance(prompt):
    """Process task with guidance agent support"""
    
    # Initialize guidance components
    guidance_agent, event_bus = setup_guidance_agent()
    
    # Publish first run event for onboarding
    event_bus.publish({"type":"first_run"})
    
    # Compile and execute task as normal
    task = TaskRequest(
        intent="task",
        goal=prompt,
        capabilities=[],
        mode="smart"
    )
    result = runtime.execute(task)
    
    # Check for MCP errors and publish appropriate event
    if hasattr(result, 'status') and result.status == "mcp_error":
        event_bus.publish({"type":"mcp_failure"})
    
    return result