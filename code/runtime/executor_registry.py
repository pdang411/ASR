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