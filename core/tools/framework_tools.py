# core/tools/framework_tools.py
import logging
from typing import Dict, Optional, List, Any

# Assuming access to registries via services
from core.services import get_services
# Assuming registry access functions are available if needed directly
from core.tools.registry_access import get_available_tools, get_registry, register_tool, tool_exists
# Corrected import for handler registry access
from core.handlers.registry_access import get_handler_registry
from core.tools.registry import ToolRegistry # Keep for type hinting
from core.handlers.registry import HandlerRegistry # Keep for type hinting

logger = logging.getLogger(__name__)

def get_available_capabilities(input_data: dict = None) -> dict:
    """
    Retrieves lists and descriptions of available tools and handlers
    by accessing the registries registered in the central ServicesContainer.

    Returns:
        dict: A dictionary containing:
            - success (bool): True if retrieval was successful, False otherwise.
            - result (dict): Contains:
                - tools_context (str): Formatted string listing available tools.
                - handlers_context (str): Formatted string listing available handlers.
                - tool_details (list): List of dicts, each with 'name' and 'description'.
                - handler_details (list): List of dicts, each with 'name' and 'description'.
            - error (str): Error message if success is False.
    """
    logger.info("Executing get_available_capabilities tool.")
    tool_details = []
    handler_details = []
    tools_context_lines = ["Available Tools:"]
    handlers_context_lines = ["Available Handlers:"]
    tool_names = set()
    handler_names = set()

    try:
        # Get registries via the Services Container
        services = get_services()
        tool_registry = services.tool_registry # Access via service property
        handler_registry = services.handler_registry # Access via service property

        # Get Tool Registry details
        if tool_registry:
            available_tools = tool_registry.tools # Access the .tools dictionary directly
            if available_tools:
                # Assuming .tools is {name: handler_func}
                for name, handler_func in available_tools.items():
                    # Attempt to get description from docstring
                    description = "No description provided."
                    if handler_func and handler_func.__doc__:
                        description = handler_func.__doc__.strip().split('\n')[0]
                    detail = {"name": name, "description": description}
                    tool_details.append(detail)
                    tools_context_lines.append(f"- {name}: {detail['description']}")
                    tool_names.add(name)
            if not tool_details:
                tools_context_lines.append("- No tools available.")
        else:
            logger.warning("ToolRegistry not found in ServicesContainer.")
            tools_context_lines.append("- Tool registry unavailable via services.")

        # Get Handler Registry details
        if handler_registry:
            available_handlers = handler_registry.list_handlers() # list_handlers returns names
            if available_handlers:
                for name in available_handlers:
                     description = "No description provided."
                     handler_func = handler_registry.get_handler(name)
                     if handler_func and handler_func.__doc__:
                          description = handler_func.__doc__.strip().split('\n')[0]

                     detail = {"name": name, "description": description}
                     handler_details.append(detail)
                     handlers_context_lines.append(f"- {name}: {detail['description']}")
                     handler_names.add(name)

            if not handler_details:
                handlers_context_lines.append("- No handlers available.")
        else:
            logger.warning("HandlerRegistry not found in ServicesContainer.")
            handlers_context_lines.append("- Handler registry unavailable via services.")

        logger.info(f"Found {len(tool_details)} tools and {len(handler_details)} handlers via services.")

        return {
            "success": True,
            "result": {
                "tools_context": "\n".join(tools_context_lines),
                "handlers_context": "\n".join(handlers_context_lines),
                "tool_details": tool_details,
                "handler_details": handler_details
            }
        }

    except Exception as e:
        logger.exception("Error retrieving available capabilities via services.")
        return {
            "success": False,
            "error": f"Failed to retrieve capabilities: {str(e)}"
        }

# --- Ensure Tool is Registered ---
# This registration happens when the module is imported
try:
    # Check if tool already exists before registering
    if not tool_exists("get_available_capabilities"):
        register_tool("get_available_capabilities", get_available_capabilities)
        logger.info("Registered 'get_available_capabilities' tool.")
    else:
        logger.debug("Tool 'get_available_capabilities' already registered.")
except ImportError:
     logger.error("Could not import registry functions for tool registration.")
except Exception as e:
     logger.error(f"Error registering 'get_available_capabilities' tool: {e}")
# 