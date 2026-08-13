def select_reasoning_service(task, registry):
    ready = [
        service
        for service in registry.ready()
        if (
            not getattr(task, "required_capability", None)
            or getattr(task, "required_capability", None)
            in service.get("capabilities", [])
        )
    ]

    if not ready:
        return None

    ready.sort(
        key=lambda r: (
            r.get("queue_depth", 0),
            r.get("avg_latency_ms", 0),
            -r.get("avg_tokens_per_sec", 0),
            -r.get("success_rate", 0),
            -r.get("provider_score", 0),
        ),
    )

    return ready[0]
