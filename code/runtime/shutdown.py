def shutdown(runtime):
    runtime.stop_accepting_requests()
    runtime.wait_for_active_tasks()
    runtime.stop_keepalive()
    
    # Shutdown SAP components
    if hasattr(runtime, 'sap'):
        import asyncio
        import threading
        
        def sap_stop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(runtime.sap.stop())
            finally:
                loop.close()
        
        runtime.sap.stop()
    
    runtime.flush_metrics()
    runtime.flush_database()
    runtime.close_provider_pool()