#!/usr/bin/env python3
"""
ASR Foundation - FreeCAD Knowledge MCP Plugin
Reference implementation following the MCP Plugin SDK specification.
"""

import json
import os
from dataclasses import dataclass
from typing import Callable, Dict, Any

# ==================== Plugin SDK Implementation ====================

@dataclass
class Capability:
    """Plugin capability definition"""
    name: str
    handler: Callable

class MCPPlugin:
    """MCP Plugin implementation for ASR Foundation"""
    
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self._caps = {}

    def register(self, capability: Capability):
        """Register a new capability"""
        self._caps[capability.name] = capability

    def execute(self, capability: str, request: dict) -> dict:
        """Execute a capability with the given request"""
        if capability not in self._caps:
            raise KeyError(f"Unknown capability: {capability}")
        return self._caps[capability].handler(request)

    def list_capabilities(self) -> list:
        """List all registered capabilities"""
        return sorted(self._caps.keys())

# ==================== FreeCAD Knowledge Data ====================

MATERIALS = {
    "6061": {"name": "6061-T6", "density": 2.70, "type": "aluminum"},
    "7075": {"name": "7075-T6", "density": 2.81, "type": "aluminum"},
    "3003": {"name": "3003-H14", "density": 2.74, "type": "aluminum"},
    "A36": {"name": "A36 Steel", "density": 7.85, "type": "steel"},
    "SS304": {"name": "Stainless Steel 304", "density": 7.93, "type": "steel"},
}

STANDARDS = {
    "ISO 9001": {"description": "Quality management systems"},
    "ASME": {"description": "American Society of Mechanical Engineers standards"},
    "ANSI": {"description": "American National Standards Institute"},
    "GB": {"description": "Chinese National Standards"},
    "JIS": {"description": "Japanese Industrial Standards"}
}

# ==================== Plugin Handlers ====================

def lookup_material(request: dict) -> dict:
    """Lookup material properties"""
    key = request.get("material", "6061")
    return MATERIALS.get(key, {"error": "not found", "material": key})

def lookup_standard(request: dict) -> dict:
    """Lookup standard information"""
    key = request.get("standard", "ISO 9001")
    return STANDARDS.get(key, {"error": "not found", "standard": key})

# ==================== Plugin Initialization ====================

# Create plugin instance
plugin = MCPPlugin("freecad-knowledge-mcp")

# Register capabilities
plugin.register(
    Capability(
        "freecad.material.lookup",
        lookup_material
    )
)

plugin.register(
    Capability(
        "freecad.standard.lookup",
        lookup_standard
    )
)

# ==================== Transport Selection ====================

class TransportSelector:
    """Selects transport method for MCP plugin"""
    
    PRIORITY = [
        "stdio",
        "streamable-http", 
        "sse"
    ]

    @classmethod
    def choose(cls, supported: list) -> str:
        """Choose best transport from supported options"""
        for transport in cls.PRIORITY:
            if transport in supported:
                return transport
        raise RuntimeError("No compatible transport")

# ==================== Plugin Discovery ====================

def discover_plugins(root: str) -> list:
    """Discover plugins in directory tree"""
    import json
    from pathlib import Path
    
    plugins = []
    manifest_path = Path(root) / "manifest.json"
    
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                plugins.append(json.load(f))
        except Exception as e:
            print(f"Error reading manifest: {e}")
    
    return plugins

# ==================== Plugin Manifest ====================

MANIFEST = {
    "id": "freecad-knowledge-mcp",
    "version": "1.0.0",
    "name": "FreeCAD Knowledge MCP", 
    "transports": ["stdio", "streamable-http", "sse"],
    "capabilities": [
        "freecad.material.lookup",
        "freecad.standard.lookup"
    ]
}

# ==================== Main Execution ====================

def main():
    """Demonstrate the FreeCAD Knowledge MCP plugin"""
    
    print("=== FreeCAD Knowledge MCP Plugin ===")
    print(f"Plugin ID: {plugin.plugin_id}")
    print(f"Version: {MANIFEST['version']}")
    print()
    
    print("Available capabilities:")
    for cap in plugin.list_capabilities():
        print(f"  - {cap}")
    print()
    
    # Test material lookup
    print("Testing material lookup:")
    test_request = {"material": "6061"}
    result = plugin.execute("freecad.material.lookup", test_request)
    print(f"  Request: {test_request}")
    print(f"  Result: {result}")
    print()
    
    # Test standard lookup  
    print("Testing standard lookup:")
    test_request = {"standard": "ASME"}
    result = plugin.execute("freecad.standard.lookup", test_request)
    print(f"  Request: {test_request}")
    print(f"  Result: {result}")
    print()
    
    # Show manifest
    print("Plugin Manifest:")
    print(json.dumps(MANIFEST, indent=2))
    
    print("\n=== Plugin Ready for ASR MCP Integration ===")

if __name__ == "__main__":
    main()