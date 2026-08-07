def startup(runtime):
    runtime.load_config()
    runtime.init_database()
    runtime.init_executor_registry()
    runtime.init_provider_pool()
    runtime.start_keepalive()
    runtime.start_metrics()