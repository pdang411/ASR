def _flash_version(runtime, name):
    flash = getattr(runtime, "flash", None)
    if flash is None:
        return 0

    version = getattr(flash, "version", None)
    if callable(version):
        try:
            return version(name)
        except Exception:
            return 0
    return 0


def _flash_get(runtime, name):
    flash = getattr(runtime, "flash", None)
    if flash is None:
        return None

    getter = getattr(flash, "get", None)
    if callable(getter):
        try:
            return getter(name)
        except Exception:
            return None
    return None


def _engine_status(engine):
    if engine is None:
        return {}

    status_fn = getattr(engine, "status", None)
    if callable(status_fn):
        try:
            payload = status_fn()
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass

    state = getattr(engine, "state", None)
    if state is not None:
        payload = {
            "status": getattr(state, "status", "UNKNOWN"),
            "mode": getattr(state, "mode", "UNKNOWN"),
            "hot_path": getattr(state, "hot_path", "UNKNOWN"),
            "announcement_version": getattr(state, "announcement_version", 0),
            "capabilities": dict(getattr(state, "capabilities", {}) or {}),
        }

        if hasattr(state, "poll_interval_seconds"):
            payload["poll_interval"] = getattr(state, "poll_interval_seconds")
        if hasattr(state, "idle_keep_alive_seconds"):
            payload["keep_alive"] = getattr(state, "idle_keep_alive_seconds")
        if hasattr(state, "providers"):
            providers = getattr(state, "providers")
            payload["providers"] = list(providers.values()) if isinstance(providers, dict) else list(providers or [])
        return payload

    return {}


def build_runtime_status(runtime):
    preemption = getattr(runtime, "smart_preemption", None)
    sap = getattr(runtime, "smart_active_polling", None)

    runtime_status = getattr(runtime, "status", None)
    if callable(runtime_status):
        try:
            runtime_status = runtime_status()
        except Exception:
            runtime_status = None
    if not isinstance(runtime_status, dict):
        runtime_state = getattr(runtime, "runtime_state", None)
        if runtime_state is not None:
            runtime_status = {
                "status": getattr(runtime_state, "runtime_status", getattr(runtime_state, "status", "UNKNOWN")),
            }
        else:
            runtime_status = {}

    return {
        "runtime": runtime_status,
        "smart_preemption": {
            **_engine_status(preemption),
            "announcement_version": _flash_version(runtime, "smart_preemption"),
            "announcement": _flash_get(runtime, "smart_preemption"),
        },
        "smart_active_polling": {
            **_engine_status(sap),
            "announcement_version": _flash_version(runtime, "smart_active_polling"),
            "announcement": _flash_get(runtime, "smart_active_polling"),
        },
    }