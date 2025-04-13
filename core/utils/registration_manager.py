"""
Registration Manager for Dawn Framework.

This module provides centralized utility functions to register all tools and handlers
required by the workflow system. It ensures consistent availability of components
across different environments and applications.
"""

import logging
import importlib
import inspect
from typing import Dict, List, Optional, Any, Callable, Tuple

from core.services import get_services
from core.tools.registry_access import register_tool, tool_exists
from core.handlers.registry_access import register_handler, handler_exists, get_handler_registry

logger = logging.getLogger(__name__)

# Core tools that should always be registered
CORE_TOOLS = [
    # Framework tools
    "get_available_capabilities",
    # Add other core tools as needed
]

# Core handlers that should always be registered
CORE_HANDLERS = [
    # Chat planner handlers
    "plan_user_request_handler",
    "validate_plan_handler",
    "plan_to_tasks_handler", 
    "execute_dynamic_tasks_handler",
    "summarize_results_handler",
    "process_clarification_handler",
    # Add other core handlers as needed
]

def ensure_core_tools_registered() -> Dict[str, bool]:
    """
    Ensures all core tools are registered with the tool registry.
    
    This function attempts to import and register any core tools
    that aren't already registered.
    
    Returns:
        Dict[str, bool]: Mapping of tool names to registration status
    """
    results = {}
    
    # First check: get_available_capabilities (directly imported)
    try:
        from core.tools.framework_tools import get_available_capabilities
        if not tool_exists("get_available_capabilities"):
            success = register_tool("get_available_capabilities", get_available_capabilities)
            results["get_available_capabilities"] = success
            if success:
                logger.info("Registered 'get_available_capabilities' tool.")
            else:
                logger.warning("Failed to register 'get_available_capabilities' tool.")
        else:
            logger.debug("Tool 'get_available_capabilities' already registered.")
            results["get_available_capabilities"] = True
    except ImportError:
        logger.error("Could not import get_available_capabilities from framework_tools.")
        results["get_available_capabilities"] = False
    except Exception as e:
        logger.error(f"Error registering 'get_available_capabilities' tool: {e}")
        results["get_available_capabilities"] = False
        
    # Dynamically check for other tools in appropriate modules
    # This demonstrates how you might set up automatic discovery in the future
    
    return results

def ensure_chat_planner_handlers_registered() -> Dict[str, bool]:
    """
    Ensures all handlers required for the chat planner workflow are registered.
    
    Returns:
        Dict[str, bool]: Mapping of handler names to registration status
    """
    results = {}
    
    # Import chat planner handlers
    try:
        # Attempt to import from the examples module 
        from examples.chat_planner_workflow import (
            plan_user_request_handler,
            validate_plan_handler,
            plan_to_tasks_handler,
            execute_dynamic_tasks_handler, 
            summarize_results_handler,
            process_clarification_handler
        )
        
        # Dictionary mapping handler names to functions
        handlers = {
            "plan_user_request_handler": plan_user_request_handler,
            "validate_plan_handler": validate_plan_handler,
            "plan_to_tasks_handler": plan_to_tasks_handler,
            "execute_dynamic_tasks_handler": execute_dynamic_tasks_handler,
            "summarize_results_handler": summarize_results_handler,
            "process_clarification_handler": process_clarification_handler,
        }
        
        # Get the handler registry
        handler_registry = get_handler_registry()
        registered_handlers = handler_registry.list_handlers()
        
        # Register each handler if it doesn't already exist
        for name, handler_func in handlers.items():
            if name not in registered_handlers:
                success = register_handler(name, handler_func)
                results[name] = success
                if success:
                    logger.info(f"Registered '{name}' handler.")
                else:
                    logger.warning(f"Failed to register '{name}' handler.")
            else:
                logger.debug(f"Handler '{name}' already registered.")
                results[name] = True
                
    except ImportError as e:
        logger.error(f"Could not import chat planner handlers: {e}")
        # Mark all as failed if import fails
        for name in ["plan_user_request_handler", "validate_plan_handler", 
                    "plan_to_tasks_handler", "execute_dynamic_tasks_handler",
                    "summarize_results_handler", "process_clarification_handler"]:
            results[name] = False
    except Exception as e:
        logger.error(f"Error registering chat planner handlers: {e}")
        # Mark all as failed if general exception occurs
        for name in ["plan_user_request_handler", "validate_plan_handler", 
                    "plan_to_tasks_handler", "execute_dynamic_tasks_handler",
                    "summarize_results_handler", "process_clarification_handler"]:
            results[name] = False
            
    return results

def ensure_all_registrations() -> Dict[str, Dict[str, bool]]:
    """
    Ensures all necessary tools and handlers are registered.
    
    This function serves as the main entry point for application initialization
    to ensure all required components are properly registered.
    
    Returns:
        Dict with registration results for tools and handlers
    """
    results = {
        "tools": ensure_core_tools_registered(),
        "handlers": ensure_chat_planner_handlers_registered(),
    }
    
    # Log overall registration summary
    tools_registered = sum(1 for status in results["tools"].values() if status)
    tools_total = len(results["tools"])
    handlers_registered = sum(1 for status in results["handlers"].values() if status)
    handlers_total = len(results["handlers"])
    
    logger.info(f"Registration summary: {tools_registered}/{tools_total} tools and {handlers_registered}/{handlers_total} handlers successfully registered.")
    
    return results 