async def poll_cycle(runtime):
    sap = getattr(runtime, "smart_active_polling", None)
    if sap is None:
        raise RuntimeError("smart_active_polling is not available")

    providers = []
    discover = getattr(sap, "discover_providers", None)
    if callable(discover):
        providers = await discover()

    discover_models = getattr(sap, "discover_models", None)
    models = []
    if callable(discover_models):
        models = await discover_models(providers)

    check_health = getattr(sap, "check_health", None)
    if callable(check_health):
        await check_health(providers)

    update_registry = getattr(sap, "update_registry", None)
    if callable(update_registry):
        await update_registry(providers, models)

    should_keep_alive = getattr(sap, "should_keep_alive", None)
    keep_alive = getattr(sap, "keep_alive_idle_services", None)
    if callable(should_keep_alive) and callable(keep_alive) and should_keep_alive():
        await keep_alive()

    flash = getattr(runtime, "flash", None)
    render = getattr(getattr(sap, "flash", None), "render", None)
    if flash is not None and callable(getattr(flash, "publish", None)) and callable(render):
        flash.publish("smart_active_polling", render())

    return {
        "poll_cycle": getattr(getattr(sap, "state", None), "cycle_count", 0),
        "providers": providers,
        "models": models,
        "announcement_version": getattr(flash, "version", lambda *_: 0)("smart_active_polling") if flash is not None else 0,
    }