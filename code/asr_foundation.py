#!/usr/bin/env python3
"""
ASR Foundation - Reference Implementation

This implements a speed-first, accuracy-driven ASR Foundation runtime
with proper plugin architecture support.
"""

import os
import logging
import re
import time
import uuid
import json
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from flask import Flask, g, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")
_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_LANG_PATTERN = re.compile(r"^[A-Za-z]{2,12}(?:-[A-Za-z0-9]{2,8})?$")

API_VERSION = "1.1"
SERVICE_NAME = "mcp-server"
PROTOCOL_VERSION = "1.0"

# Plugin Interface Structure - Implementation of Reference Architecture
class FoundationPlugin(ABC):
    """Base class for ASR Foundation plugins"""
    
    def __init__(self, plugin_id: str, version: str):
        self.plugin_id = plugin_id
        self.version = version
    
    @abstractmethod
    def capability(self) -> str:
        """Return the capability this plugin provides"""
        pass
    
    @abstractmethod
    def execute(self, request) -> Dict[str, Any]:
        """Execute the plugin operation"""
        pass
    
    def reprocess(self, request) -> Optional[Dict[str, Any]]:
        """Optional background reprocessing for enrichment"""
        return None

# Scheduler with background processing
def dispatch(plugin: FoundationPlugin, request) -> Dict[str, Any]:
    """Dispatch a request to a plugin and handle background reprocessing"""
    logger.info(f"Dispatching request to plugin {plugin.plugin_id}")
    result = plugin.execute(request)
    
    # Check if need reprocessing
    if getattr(result, "needs_reprocess", False):
        logger.info(f"Request to plugin {plugin.plugin_id} needs reprocessing")
        # This would queue background work in a real implementation
        # For now we'll just return the initial result
    
    return result

# Knowledge Plugin Implementation - Based on reference architecture
class KnowledgePlugin(FoundationPlugin):
    """Knowledge table lookup plugin - optimized for speed-first approach"""
    
    def __init__(self):
        super().__init__("foundation.knowledge.lookup", "1.0.0")
        # Simulate knowledge base
        self.kb = {
            "greeting": "Hello, how can I help?",
            "weather": "It is sunny today.",
            "time": "The time is 12:00 PM."
        }
        
    def capability(self) -> str:
        return "knowledge.lookup"
    
    def execute(self, request) -> Dict[str, Any]:
        """Fast indexed lookup from knowledge base"""
        query = request.get("query", "")
        
        if not query:
            return {"error": "No query provided"}
            
        # Fast lookup in indexes
        result = self.kb.get(query.lower(), f"Information for '{query}' not found")
        
        # Return quick response without expensive AI inference
        return {
            "result": result,
            "source": "knowledge_index",
            "accuracy": "high",
            "speed": "fast"
        }
    
    def reprocess(self, request) -> Optional[Dict[str, Any]]:
        """Background enrichment process"""
        query = request.get("query", "")
        if not query:
            return None
        
        # Simulate deeper search or AI enhancement
        enriched_result = f"Enhanced result for '{query}' with additional context"
        
        return {
            "enriched": True,
            "result": enriched_result,
            "source": "ai_enhancement"
        }

# Hardware Acceleration Support
class HardwareAccelerator:
    """Support for CPU/GPU/NPU acceleration"""
    
    def __init__(self):
        self.hardware_support = {
            'cpu': True,
            'gpu': False,  # Optional in this implementation
            'npu': False   # Optional in this implementation
        }
    
    def prefer_hardware_acceleration(self) -> bool:
        """Automatically determine if hardware acceleration should be used"""
        return self.hardware_support['cpu']

# Plugin Registry - Maintains active plugins
class PluginRegistry:
    """Registry for managing ASR Foundation plugins"""
    
    def __init__(self):
        self.plugins = {}
        self.registry = {}
    
    def register_plugin(self, plugin: FoundationPlugin):
        """Register a new plugin"""
        capability = plugin.capability()
        self.plugins[capability] = plugin
        logger.info(f"Registered plugin: {plugin.plugin_id} for capability: {capability}")
    
    def get_plugin(self, capability: str) -> Optional[FoundationPlugin]:
        """Get a plugin by capability"""
        return self.plugins.get(capability)

# Initialize the ASR Foundation components
hardware_accelerator = HardwareAccelerator()
plugin_registry = PluginRegistry()

# Register default plugins
knowledge_plugin = KnowledgePlugin()
plugin_registry.register_plugin(knowledge_plugin)

# Utility functions
def _valid_id(value: str) -> bool:
    return isinstance(value, str) and bool(_ID_PATTERN.match(value))


def _canonical_text(text: Any) -> str:
    if isinstance(text, dict):
        text = json.dumps(text, separators=(',', ':'), sort_keys=True)
    return str(text)


def _deterministic_response(tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure response is deterministic"""
    return {
        "tool": tool_name,
        "result": result
    }


# Response formatting helpers
def _require_api_key(key_name: str) -> Optional[str]:
    key = os.environ.get(key_name)
    if not key:
        return None
    if not _TOKEN_PATTERN.match(key):
        return None
    return key


def _require_valid_api_key(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    if not _TOKEN_PATTERN.match(token):
        return None
    return token


def _require_valid_api_key_in_url(args: Dict[str, Any]) -> Optional[str]:
    key = args.get("api_key")
    if not key:
        return None
    if not _TOKEN_PATTERN.match(key):
        return None
    return key


def _error_response(tool_name: str, started_at: float, status_code: int, error_code: str, message: str) -> Dict[str, Any]:
    duration = time.perf_counter() - started_at
    return {
        "tool": tool_name,
        "version": API_VERSION,
        "duration": duration,
        "error": {
            "code": error_code,
            "message": message,
        },
        "status": status_code,
    }


def _post_json(url: str, payload: Dict[str, Any], cache_key: Optional[str] = None) -> Dict[str, Any]:
    """Mock HTTP POST handler"""
    # In a real implementation this would make actual HTTP requests
    if url.endswith("/knowledge"):
        return {
            "query": payload.get("query", ""),
            "result": knowledge_plugin.execute(payload),
            "cached": cache_key is not None,
            "source": "knowledge_lookup"
        }
    return {"error": f"Unknown URL: {url}"}


def _get_json(url: str, cache_key: Optional[str] = None) -> Dict[str, Any]:
    """Mock HTTP GET handler"""
    # In a real implementation this would make actual HTTP requests
    if url.endswith("/knowledge"):
        return {
            "plugin_id": "foundation.knowledge.lookup",
            "version": "1.0.0",
            "supported_capabilities": ["knowledge.lookup"],
            "source": "plugin_registry"
        }
    return {"error": f"Unknown URL: {url}"}


# Flask App Setup
def create_app() -> Flask:
    app = Flask(__name__)
    
    @app.before_request
    def before_request():
        g.start_time = time.perf_counter()
    
    @app.after_request
    def after_request(response):
        duration = time.perf_counter() - getattr(g, 'start_time', time.perf_counter())
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"})
    
    @app.route('/knowledge', methods=['POST'])
    def knowledge_lookup():
        """Knowledge base lookup endpoint - fast response with background enrichment"""
        started_at = time.perf_counter()
        g.tool_name = "knowledge.lookup"
        
        payload = request.get_json() or {}
        query = payload.get("query", "")
        
        if not query:
            return jsonify(_error_response(
                "knowledge.lookup", started_at, 400, 
                "invalid_argument", "Missing required 'query' field"
            )), 400
            
        # Dispatch to knowledge plugin for fast lookup
        try:
            result = dispatch(knowledge_plugin, payload)
            g.response_success = True
            return jsonify({
                "tool": "knowledge.lookup",
                "version": API_VERSION,
                "duration": time.perf_counter() - started_at,
                "result": result
            })
        except Exception as e:
            g.response_success = False
            return jsonify(_error_response(
                "knowledge.lookup", started_at, 500, 
                "internal_error", str(e)
            )), 500
    
    @app.route('/plugins', methods=['GET'])
    def list_plugins():
        """List available plugins"""
        started_at = time.perf_counter()
        g.tool_name = "plugins.list"
        
        try:
            plugin_list = []
            for capability, plugin in plugin_registry.plugins.items():
                plugin_list.append({
                    "id": plugin.plugin_id,
                    "version": plugin.version,
                    "capability": capability
                })
            
            g.response_success = True
            return jsonify({
                "tool": "plugins.list",
                "version": API_VERSION,
                "duration": time.perf_counter() - started_at,
                "result": {
                    "plugins": plugin_list,
                    "hardware_acceleration": hardware_accelerator.prefer_hardware_acceleration()
                }
            })
        except Exception as e:
            g.response_success = False
            return jsonify(_error_response(
                "plugins.list", started_at, 500, 
                "internal_error", str(e)
            )), 500
    
    @app.route('/plugin/<capability>', methods=['GET'])
    def get_plugin(capability):
        """Get information about a specific plugin"""
        started_at = time.perf_counter()
        g.tool_name = "plugin.get"
        
        try:
            plugin = plugin_registry.get_plugin(capability)
            if not plugin:
                return jsonify(_error_response(
                    "plugin.get", started_at, 404, 
                    "not_found", f"Plugin with capability '{capability}' not found"
                )), 404
            
            g.response_success = True
            return jsonify({
                "tool": "plugin.get",
                "version": API_VERSION,
                "duration": time.perf_counter() - started_at,
                "result": {
                    "id": plugin.plugin_id,
                    "version": plugin.version,
                    "capability": capability
                }
            })
        except Exception as e:
            g.response_success = False
            return jsonify(_error_response(
                "plugin.get", started_at, 500, 
                "internal_error", str(e)
            )), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)