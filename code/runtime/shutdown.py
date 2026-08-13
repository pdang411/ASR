def shutdown(runtime):
    runtime.stop_accepting_requests()
    runtime.wait_for_active_tasks()
    if hasattr(runtime, "stop_sap"):
        runtime.stop_sap()
    runtime.stop_keepalive()
    runtime.flush_metrics()
    runtime.flush_database()
    runtime.close_provider_pool()