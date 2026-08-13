def register_default_capabilities(registry):
    registry.register(
        "memory.build",
        "Build and store structured operational memory.",
        "AI.KB",
        "Memory",
    )

    registry.register(
        "asr.memory.build",
        "Build and store structured operational memory.",
        "AI.KB",
        "Memory",
    )

    registry.register(
        "asr_asr_build_memory",
        "Build and store structured operational memory.",
        "AI.KB",
        "Memory",
    )

    registry.register(
        "asr_asr_transcribe",
        "Convert audio into structured transcription results.",
        "Transcription",
        "Transcription",
    )

    registry.register(
        "asr_runtime_execute",
        "Execute a compiled ASR task through the runtime.",
        "Runtime",
        "Runtime Execution",
    )

    registry.register(
        "workflow_get",
        "Retrieve an ASR workflow definition.",
        "Workflow",
        "Workflow",
    )

    registry.register(
        "reference_search",
        "Search authoritative project references.",
        "Reference",
        "Reference Search",
    )

    registry.register(
        "reference.search",
        "Search authoritative project references.",
        "Reference",
        "Reference Search",
    )

    registry.register(
        "workflow.get",
        "Retrieve an ASR workflow definition.",
        "Workflow",
        "Workflow",
    )

    return registry