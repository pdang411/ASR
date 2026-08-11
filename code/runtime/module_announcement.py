def _read_attr(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _status_payload(engine):
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

    snapshot_fn = getattr(engine, "snapshot", None)
    if callable(snapshot_fn):
        try:
            payload = snapshot_fn()
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass

    return {}


def build_module_announcement(modules, smart_preemption=None, smart_active_polling=None):
    """Read existing runtime instances and expose their cached FLASH."""
    result = []

    for module in modules:
        module_id = _read_attr(module, "id") or _read_attr(module, "name") or "module"
        module_name = _read_attr(module, "name") or str(module_id)
        module_status = _read_attr(module, "status", "READY")
        capabilities = _read_attr(module, "capabilities", [])
        if isinstance(capabilities, dict):
            capabilities = list(capabilities.keys())

        result.append(
            {
                "id": str(module_id),
                "name": str(module_name),
                "status": str(module_status),
                "capabilities": list(capabilities or []),
            }
        )

    if smart_preemption is not None:
        status = _status_payload(smart_preemption)
        result.append(
            {
                "id": "smart_preemption",
                "name": "Smart Preemption",
                "status": status.get("status", "UNKNOWN"),
                "mode": status.get("mode", "UNKNOWN"),
                "hot_path": status.get("hot_path", "UNKNOWN"),
                "capabilities": status.get("capabilities", {}),
                "announcement_version": status.get("announcement_version", 0),
                "announcement": status.get("announcement", ""),
            }
        )

    if smart_active_polling is not None:
        status = _status_payload(smart_active_polling)
        announcement = status.get("announcement", "")
        if not announcement:
            announcement = status.get("sap_flash_markdown", "")
        poll_interval = status.get("poll_interval_seconds")
        if poll_interval is None:
            poll_interval = status.get("model_poll_interval_seconds")

        result.append(
            {
                "id": "smart_active_polling",
                "name": "Smart Active Polling",
                "status": status.get("status", "UNKNOWN"),
                "mode": status.get("mode", "UNKNOWN"),
                "hot_path": status.get("hot_path", "UNKNOWN"),
                "poll_interval_seconds": poll_interval,
                "capabilities": status.get("capabilities", {}),
                "announcement_version": status.get("announcement_version", 0),
                "providers": status.get("providers", []),
                "announcement": announcement,
            }
        )

    return result