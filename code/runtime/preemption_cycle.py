def preemption_cycle(runtime, request):
    engine = getattr(runtime, "smart_preemption", None)
    if engine is None:
        raise RuntimeError("smart_preemption is not available")

    decision = engine.decide(request)

    flash = getattr(runtime, "flash", None)
    render = getattr(getattr(engine, "flash", None), "render", None)
    if flash is not None and callable(getattr(flash, "publish", None)) and callable(render):
        flash.publish("smart_preemption", render())

    return {
        "decision": getattr(decision, "name", decision),
        "reason": getattr(decision, "reason", ""),
    }