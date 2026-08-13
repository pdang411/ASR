def startup(runtime):
    runtime.load_config()
    runtime.init_database()
    runtime.init_executor_registry()
    runtime.init_provider_pool()
    runtime.start_keepalive()
    if hasattr(runtime, "start_sap"):
        runtime.start_sap()
    runtime.start_metrics()