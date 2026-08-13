class ExecutorRegistry:
    # Provider mapping for capabilities
    _capability_providers = {
        "knowledge.search": ["deepagents", "runtime"],
        "code.generate": ["agent-mcp", "runtime"],
        "code.review": ["agent-mcp", "runtime"], 
        "cad.model": ["freecad", "runtime"],
        "workflow.plan": ["deepagents", "runtime"],
        "repository.search": ["github", "runtime"],
        "image.analyze": ["blender", "runtime"],
        "audio.transcribe": ["agent-mcp", "runtime"]
    }

    def __init__(self):
        self._adapters = []

    def resolve(self, capability: str):
        """Resolve a capability to its primary executor"""
        providers = self._providers_for(capability)
        return providers[0] if providers else "runtime"

    def _providers_for(self, capability):
        """Get all providers for a given capability"""
        return self._capability_providers.get(capability, ["runtime"])
    
    def get_all_providers(self, capability: str):
        """Get all providers for a given capability"""
        return self._providers_for(capability)
    
    def register_provider(self, capability: str, provider: str):
        """Register a new provider for a capability"""
        if capability not in self._capability_providers:
            self._capability_providers[capability] = []
        if provider not in self._capability_providers[capability]:
            self._capability_providers[capability].append(provider)

    def register(self, adapter):
        """Register an adapter implementing accepts(task) and dispatch(task)."""
        if adapter is not None:
            self._adapters.append(adapter)

    def dispatch(self, task):
        """Dispatch task to first matching adapter, else return runtime fallback."""
        for adapter in self._adapters:
            accepts = getattr(adapter, "accepts", None)
            if callable(accepts) and accepts(task):
                dispatch = getattr(adapter, "dispatch", None)
                if callable(dispatch):
                    return dispatch(task)

        return {
            "executor": "runtime",
            "reference": getattr(task, "input_ref", ""),
        }