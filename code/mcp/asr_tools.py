from runtime.asr_runtime_status import build_runtime_status
from runtime.module_discovery import build_module_list


async def asr_runtime_status(runtime):
    return build_runtime_status(runtime)


async def asr_module_list(runtime):
    return {
        "modules": build_module_list(runtime)
    }


async def asr_runtime_polling(runtime, action):
    sap = getattr(runtime, "smart_active_polling", None)
    if sap is None:
        raise RuntimeError("smart_active_polling is not available")

    if action == "status":
        return sap.status()

    if action == "flash_announcement":
        flash = getattr(runtime, "flash", None)
        return {
            "status": getattr(getattr(sap, "state", None), "status", "UNKNOWN"),
            "announcement_version": getattr(flash, "version", lambda *_: 0)("smart_active_polling") if flash is not None else 0,
            "format": "markdown",
            "announcement": getattr(flash, "get", lambda *_: None)("smart_active_polling") if flash is not None else None,
        }

    if action == "start":
        return await sap.start()

    if action == "stop":
        return await sap.stop()

    raise ValueError(f"Unsupported runtime polling action: {action}")


async def smart_preemption_flash(runtime):
    preemption = getattr(runtime, "smart_preemption", None)
    if preemption is None:
        raise RuntimeError("smart_preemption is not available")

    flash = getattr(runtime, "flash", None)
    return {
        "status": getattr(getattr(preemption, "state", None), "status", "UNKNOWN"),
        "mode": getattr(getattr(preemption, "state", None), "mode", "UNKNOWN"),
        "hot_path": getattr(getattr(preemption, "state", None), "hot_path", "UNKNOWN"),
        "announcement_version": getattr(flash, "version", lambda *_: 0)("smart_preemption") if flash is not None else 0,
        "format": "markdown",
        "announcement": getattr(flash, "get", lambda *_: None)("smart_preemption") if flash is not None else None,
    }