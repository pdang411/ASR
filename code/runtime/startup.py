def startup(runtime):
    runtime.load_config()
    runtime.init_database()
    runtime.init_executor_registry()
    runtime.init_provider_pool()
    
    # Initialize SAP v2 components
    from runtime.smart_active_polling import SmartActivePolling
    from runtime.provider_manager import ProviderManager
    from runtime.reasoning_registry import ReasoningRegistry
    
    # Create and start Smart Active Polling
    provider_manager = ProviderManager(runtime.providers)
    registry = ReasoningRegistry()
    sap = SmartActivePolling(provider_manager, registry)
    
    # Start the polling in background
    import asyncio
    import threading
    
    def sap_runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(sap.start())
        finally:
            loop.close()
    
    sap_thread = threading.Thread(target=sap_runner, daemon=True)
    sap_thread.start()
    
    runtime.sap = sap
    runtime.sap_thread = sap_thread
    
    runtime.start_keepalive()
    runtime.start_metrics()