def select_reasoning_service(task, registry):
    ready = [
        r for r in registry.ready()
        if task.required_capability in r["capabilities"]
    ]

    ready.sort(
        key=lambda r: (
            r["provider_score"],
            -r["avg_tokens_per_sec"],
            r["avg_latency_ms"],
            r["queue_depth"],
            -r["success_rate"]
        ),
        reverse=True
    )

    return ready[0] if ready else None