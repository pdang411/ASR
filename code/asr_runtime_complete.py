#!/usr/bin/env python3
"""
ASR Foundation - Complete MCP Runtime Implementation (Volume 3)
Contains reference implementations for the runtime components.
"""

import importlib.util
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

# ==================== Plugin Loader ====================

class PluginLoader:
    """Loads plugins from directory structure"""
    
    def __init__(self):
        self.loaded_plugins = {}
    
    def load(self, plugin_dir: str) -> object:
        """Load a plugin from directory"""
        module_path = Path(plugin_dir) / "server.py"
        
        if not module_path.exists():
            raise FileNotFoundError(f"Plugin server.py not found in {plugin_dir}")
            
        if plugin_dir in self.loaded_plugins:
            return self.loaded_plugins[plugin_dir]
            
        spec = importlib.util.spec_from_file_location("plugin", module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        self.loaded_plugins[plugin_dir] = mod
        return mod

# ==================== Capability Registry ====================

class CapabilityRegistry:
    """Registry for managing capability providers"""
    
    def __init__(self):
        self.providers: Dict[str, List[object]] = {}

    def register(self, plugin: object, capabilities: List[str]) -> None:
        """Register a plugin with its capabilities"""
        for cap in capabilities:
            if cap not in self.providers:
                self.providers[cap] = []
            self.providers[cap].append(plugin)

    def resolve(self, capability: str) -> Optional[object]:
        """Resolve which plugin provides a capability"""
        if capability not in self.providers:
            raise LookupError(f"Capability '{capability}' not found")
        return self.providers[capability][0]  # Return first provider

# ==================== Capability Router ====================

class CapabilityRouter:
    """Routes requests to appropriate plugin providers"""
    
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def dispatch(self, capability: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch request to appropriate plugin"""
        plugin = self.registry.resolve(capability)
        
        # Try to find handle_request method in plugin
        if hasattr(plugin, 'handle_request'):
            return plugin.handle_request(capability, request)  
        elif hasattr(plugin, 'execute'):
            return plugin.execute(capability, request)
        else:
            raise AttributeError(f"Plugin does not support capability {capability}")

# ==================== Transport Manager ====================

class TransportManager:
    """Manages transport protocol selection"""
    
    PRIORITY = ("stdio", "streamable-http", "sse")

    def select(self, supported: List[str]) -> str:
        """Select best transport from supported options"""
        for t in self.PRIORITY:
            if t in supported:
                return t
        raise RuntimeError("No supported transport found")

# ==================== Memory Cache ====================

class MemoryCache:
    """In-memory cache with TTL support"""
    
    def __init__(self):
        self.data = {}

    def put(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store item with expiration time"""
        self.data[key] = (value, time.time() + ttl)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve item if not expired"""
        item = self.data.get(key)
        if not item:
            return None
        value, exp = item
        if time.time() > exp:
            del self.data[key]
            return None
        return value

# ==================== Workflow Execution ====================

class Workflow:
    """Execute multi-step workflows"""
    
    def __init__(self, router: CapabilityRouter):
        self.router = router

    def execute(self, steps: List[tuple]) -> Dict[str, Any]:
        """Execute workflow steps sequentially"""
        result = None
        for capability, request in steps:
            print(f"Executing: {capability} with {request}")
            result = self.router.dispatch(capability, request)
            print(f"Result: {result}")
        return result

# ==================== Complete Runtime Example ====================

def main():
    """Demonstrate the complete runtime implementation"""
    
    print("=== ASR Foundation - Complete MCP Runtime ===")
    print()
    
    # Initialize components
    loader = PluginLoader() 
    registry = CapabilityRegistry()
    router = CapabilityRouter(registry)
    transport_mgr = TransportManager()
    cache = MemoryCache()
    
    print("1. Testing Plugin Loader:")
    try:
        # This would load actual plugins in real system
        print("   Plugin loader initialized")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Testing Capability Registry:")
    print("   Registry initialized with empty provider list")
    
    print("\n3. Testing Transport Manager:")
    transports = ["stdio", "streamable-http", "sse"]
    selected = transport_mgr.select(transports)
    print(f"   Selected transport: {selected}")
    
    print("\n4. Testing Memory Cache:")
    cache.put("test_key", {"data": "test_value"}, ttl=60)
    result = cache.get("test_key")
    print(f"   Cached data: {result}")
    
    print("\n5. Testing Workflow Execution:")
    # Create a dummy workflow - in practice this executes actual capabilities
    workflow_steps = [
        ("freecad.material.lookup", {"material": "6061"}),
        ("freecad.standard.lookup", {"standard": "ASME"})
    ]
    
    try:
        workflow = Workflow(router)
        print("   Workflow component created")
        print("   (In actual execution, this would dispatch to plugins)")
    except Exception as e:
        print(f"   Workflow error: {e}")
    
    print("\n=== Runtime Components Ready ===")

if __name__ == "__main__":
    main()