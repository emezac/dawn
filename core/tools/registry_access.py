"""
Standardized ToolRegistry access module.

This module provides a consistent way to access the ToolRegistry
throughout the application, implementing a singleton pattern to 
ensure only one registry instance is used.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Callable

from core.errors import ErrorCode
from core.tools.registry import ToolRegistry
from core.tools.response_format import create_error_response

# Configure logging
logger = logging.getLogger(__name__)

# Singleton instance of the ToolRegistry
_registry_instance = None

def get_registry() -> ToolRegistry:
    """
    Get the singleton instance of the ToolRegistry.
    
    Returns:
        ToolRegistry: The singleton registry instance
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ToolRegistry()
        logger.debug("Created new ToolRegistry singleton instance")
    return _registry_instance

def reset_registry() -> None:
    """
    Reset the singleton registry instance.
    This is primarily used for testing.
    """
    global _registry_instance
    _registry_instance = None
    logger.debug("Reset ToolRegistry singleton instance")

def register_tool(name: str, handler: Callable, replace: bool = False) -> bool:
    """
    Register a tool with the registry.
    
    Args:
        name: The name of the tool
        handler: The tool handler function
        replace: Whether to replace an existing tool with the same name
        
    Returns:
        bool: True if registration was successful
    """
    registry = get_registry()
    
    # Check if tool already exists
    if name in registry.tools and not replace:
        logger.warning(f"Tool '{name}' already registered and replace=False")
        return False
    
    try:
        # If replacing, we need to remove the existing tool first
        if name in registry.tools and replace:
            # ToolRegistry doesn't have a remove_tool method, so we directly modify the dict
            del registry.tools[name]
            logger.debug(f"Removed existing tool '{name}' for replacement")
            
        # Now register the tool
        registry.register_tool(name, handler)
        logger.debug(f"Successfully registered tool '{name}'")
        return True
    except Exception as e:
        logger.error(f"Failed to register tool '{name}': {e}")
        return False

def execute_tool(name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool by name with the provided data.
    
    Args:
        name: The name of the tool to execute
        data: The input data for the tool
        
    Returns:
        Dict: The result of the tool execution in standardized format
    """
    registry = get_registry()
    
    if name not in registry.tools:
        logger.warning(f"Tool '{name}' not found in registry")
        return create_error_response(
            message=f"Tool '{name}' not found in registry",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            details={"tool_name": name, "resource_type": "tool"}
        )
    
    try:
        result = registry.execute_tool(name, data)
        return result
    except Exception as e:
        logger.error(f"Error executing tool '{name}': {e}")
        return create_error_response(
            message=f"Error executing tool '{name}': {str(e)}",
            error_code=ErrorCode.EXECUTION_TOOL_FAILED,
            details={"tool_name": name, "error_type": type(e).__name__}
        )

def get_available_tools() -> List[Dict[str, Any]]:
    """
    Get metadata about all available tools.
    
    Returns:
        List of dictionaries containing tool metadata
    """
    registry = get_registry()
    return registry.get_available_tools()

def tool_exists(name: str) -> bool:
    """
    Check if a tool exists in the registry.
    
    Args:
        name: The name of the tool to check
        
    Returns:
        bool: True if the tool exists, False otherwise
    """
    registry = get_registry()
    return name in registry.tools

def load_plugins(reload: bool = False) -> None:
    """
    Load all plugins into the registry.
    
    Args:
        reload: Whether to reload already loaded plugins
    """
    registry = get_registry()
    registry.load_plugins(reload)
    logger.debug("Loaded plugins into registry")

def register_plugin_namespace(namespace: str) -> None:
    """
    Register a plugin namespace with the registry.
    
    Args:
        namespace: The namespace to register
    """
    registry = get_registry()
    registry.register_plugin_namespace(namespace)
    logger.debug(f"Registered plugin namespace: {namespace}") 