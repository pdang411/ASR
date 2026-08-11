def _read_attr(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def build_module_list(runtime):
    modules = []
    module_registry = getattr(runtime, "module_registry", None)
    if module_registry is not None and hasattr(module_registry, "list"):
        for module in module_registry.list():
            modules.append(
                {
                    "id": _read_attr(module, "id", _read_attr(module, "name", "module")),
                    "name": _read_attr(module, "name", "module"),
                    "status": _read_attr(module, "status", "READY"),
                    "capabilities": list(_read_attr(module, "capabilities", []) or []),
                }
            )

    preemption = getattr(runtime, "smart_preemption", None)
    if preemption is not None:
        state = getattr(preemption, "state", None)
        if state is None:
            state = getattr(preemption, "preemption_state", None)
        modules.append(
            {
                "id": "smart_preemption",
                "name": "Smart Preemption",
                "status": _read_attr(state, "status", "UNKNOWN"),
                "capabilities": list(getattr(preemption, "capabilities", {}) or getattr(state, "capabilities", {}) or {}),
                "announcement_version": _read_attr(state, "announcement_version", 0),
            }
        )

    sap = getattr(runtime, "smart_active_polling", None)
    if sap is not None:
        state = getattr(sap, "state", None)
        modules.append(
            {
                "id": "smart_active_polling",
                "name": "Smart Active Polling",
                "status": _read_attr(state, "status", "UNKNOWN"),
                "capabilities": list(getattr(sap, "capabilities", {}) or getattr(state, "capabilities", {}) or {}),
                "announcement_version": _read_attr(state, "announcement_version", 0),
                "providers": list(getattr(sap, "providers", []) or _read_attr(state, "providers", {}).values() if isinstance(_read_attr(state, "providers", {}), dict) else _read_attr(state, "providers", []) or []),
            }
        )

    return modules