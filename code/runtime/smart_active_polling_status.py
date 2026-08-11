def build_status(manager, sap_running=True, model_poll_interval_seconds=30):
    providers = []

    for provider in manager.providers():
        state = provider.state
        providers.append(
            {
                "provider_id": state.provider_id,
                "endpoint": state.endpoint,
                "status": state.status,
                "models": list(state.models),
                "active_model": state.active_model,
                "last_model_query": state.last_model_query,
                "model_query_count": state.model_query_count,
                "model_query_failures": state.model_query_failures,
                "active_requests": state.active_requests,
                "last_health": state.last_health,
                "health_failures": state.health_failures,
            }
        )

    return {
        "sap_running": bool(sap_running),
        "model_poll_interval_seconds": int(model_poll_interval_seconds),
        "providers": providers,
    }


def build_polling_status(runtime_registry, sap):
    providers = []
    if runtime_registry is not None:
        providers = list(getattr(runtime_registry.state, "providers", {}).values())

    sap_status = {}
    status_fn = getattr(sap, "status", None)
    if callable(status_fn):
        try:
            sap_status = status_fn() or {}
        except Exception:
            sap_status = {}

    payload = {
        "sap_running": bool(getattr(sap, "running", False)),
        "model_poll_interval_seconds": int(getattr(sap, "interval_seconds", 30)),
        "providers": providers,
    }

    for key in [
        "status",
        "mode",
        "hot_path",
        "poll_interval_seconds",
        "idle_keep_alive_seconds",
        "cycle_count",
        "announcement_version",
        "capabilities",
        "metrics",
    ]:
        if key in sap_status:
            payload[key] = sap_status[key]

    if "announcement" in sap_status:
        payload["sap_flash_markdown"] = sap_status["announcement"]

    if runtime_registry is not None:
        payload["announcement"] = {
            "available": True,
            "resource": "asr://capabilities",
            "version": int(getattr(runtime_registry.state, "announcement_version", 0)),
        }

    return payload
