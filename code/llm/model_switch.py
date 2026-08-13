class ModelSwitcher:
    def switch(self, runtime, provider, model):
        runtime.stop_keepalive()
        runtime.drain_requests()

        session = runtime.session_pool.get(provider, model)
        if session is None:
            session = runtime.create_session(provider, model)
            runtime.session_pool.register(provider, model, session)
            session.connect()
            session.provider.keepalive()

        runtime.session_pool.activate(provider, model)
        runtime.start_keepalive()
        return session