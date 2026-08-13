from runtime.flash_store import FlashStore


class ASRRuntime:
    def __init__(
        self,
        provider_manager,
        reasoning_registry=None,
        capability_registry=None,
        runtime_state=None,
        announcement_resource=None,
        smart_active_polling=None,
        smart_preemption=None,
        flash_store=None,
    ):
        self.provider_manager = provider_manager
        self.reasoning_registry = reasoning_registry
        self.capability_registry = capability_registry
        self.runtime_state = runtime_state
        self.announcement_resource = announcement_resource
        self.smart_active_polling = smart_active_polling
        self.smart_preemption = smart_preemption
        self.flash = flash_store if flash_store is not None else FlashStore()

        if self.announcement_resource is None and self.runtime_state is not None:
            from .announcement_markdown import RuntimeAnnouncementMarkdown
            from .runtime_capability_resource import RuntimeCapabilityResource

            self.announcement_resource = RuntimeCapabilityResource(
                self.runtime_state,
                RuntimeAnnouncementMarkdown(self.runtime_state),
            )

    @property
    def status(self):
        runtime_state = self.runtime_state
        if runtime_state is None:
            return {}

        if hasattr(runtime_state, "state"):
            state = getattr(runtime_state, "state")
            if state is not None:
                if isinstance(state, dict):
                    return state
                snapshot = getattr(state, "snapshot", None)
                if callable(snapshot):
                    try:
                        payload = snapshot()
                        if isinstance(payload, dict):
                            return payload
                    except Exception:
                        pass

                runtime_status = getattr(state, "runtime_status", None)
                if runtime_status is not None:
                    return {"status": runtime_status}

        snapshot = getattr(runtime_state, "snapshot", None)
        if callable(snapshot):
            try:
                payload = snapshot()
                if isinstance(payload, dict):
                    return payload
            except Exception:
                pass

        runtime_status = getattr(runtime_state, "runtime_status", None)
        if runtime_status is not None:
            return {"status": runtime_status}

        return {}

    async def startup(self):
        if self.smart_preemption is not None and hasattr(self.smart_preemption, "initialize"):
            await self.smart_preemption.initialize()
            render = getattr(getattr(self.smart_preemption, "flash", None), "render", None)
            if callable(render) and hasattr(self.flash, "publish"):
                self.flash.publish("smart_preemption", render())

        if self.runtime_state is not None:
            self.runtime_state.set_runtime_state(
                runtime_status="STARTING",
                smart_preemption_status="READY",
                ai_kb_status="READY",
                executor_registry_status="READY",
            )

        await self.provider_manager.startup()

        if self.smart_active_polling is None:
            from .smart_active_polling import SmartActivePolling

            self.smart_active_polling = SmartActivePolling(
                self.provider_manager,
                self.reasoning_registry,
                interval_seconds=30,
                idle_keep_alive_seconds=60,
                on_provider_state=self._provider_state_changed,
            )

        if self.runtime_state is not None:
            self.runtime_state.set_runtime_state(
                runtime_status="RUNNING",
                sap_running=True,
            )

        if self.announcement_resource is not None:
            await self.announcement_resource.read()

        await self.smart_active_polling.start()
        render = getattr(getattr(self.smart_active_polling, "flash", None), "render", None)
        if callable(render) and hasattr(self.flash, "publish"):
            self.flash.publish("smart_active_polling", render())

    async def _provider_state_changed(self, provider_state):
        if self.runtime_state is not None and hasattr(self.runtime_state, "update_provider"):
            self.runtime_state.update_provider(provider_state)

        if self.reasoning_registry is not None:
            if hasattr(self.reasoning_registry, "update"):
                self.reasoning_registry.update(provider_state)
            elif hasattr(self.reasoning_registry, "update_provider"):
                class _Wrapper:
                    def __init__(self, state):
                        self.state = state

                self.reasoning_registry.update_provider(_Wrapper(provider_state))

    async def shutdown(self):
        if self.smart_active_polling:
            await self.smart_active_polling.stop()

        if self.smart_preemption is not None:
            state = getattr(self.smart_preemption, "preemption_state", None)
            if state is not None:
                state.status = "STOPPED"
                state.hot_path = "STOPPED"
                state.mark_changed()
            if hasattr(self.smart_preemption, "_refresh_flash"):
                self.smart_preemption._refresh_flash()

        if self.runtime_state is not None:
            self.runtime_state.set_runtime_state(
                runtime_status="STOPPED",
                sap_running=False,
            )