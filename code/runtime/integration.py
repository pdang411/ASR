from runtime.chart_adapter import ChartAdapter
from runtime.executor_registry import ExecutorRegistry
from runtime.runtime_state import RuntimeState
from runtime.smart_preemption import SmartPreemption
from runtime.universal_task import UniversalTask
from runtime.voice_adapter import VoiceAdapter


def run_integration_example():
    state = RuntimeState(
        pipeline_cache={
            "runtime_metrics": "pipeline.metrics.default",
        }
    )

    registry = ExecutorRegistry()
    registry.register(ChartAdapter())
    registry.register(VoiceAdapter())

    smart_preemption = SmartPreemption(runtime_state=state, registry=registry)

    task = UniversalTask(
        task_id="T1001",
        task_type="analysis",
        intent="runtime_metrics",
        priority=1,
        executor="auto",
        input_ref="kb://runtime",
        media_type="chart",
    )

    return smart_preemption.handle(task)


if __name__ == "__main__":
    print(run_integration_example())
