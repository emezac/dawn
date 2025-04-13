# core/handlers/registry_access.py
"""
Standardized HandlerRegistry access module.

Provides a consistent way to access the HandlerRegistry, implementing
a singleton pattern (though typically managed via ServicesContainer).
"""  # noqa: D202

import logging
from typing import Any, Dict, List, Optional, Callable

# Assuming ErrorCode and create_error_response are generic enough
# If not, they might need adjustment or specific handler error codes.
from core.errors import ErrorCode
from core.tools.response_format import create_error_response # Re-using tool response format for now
from .registry import HandlerRegistry # Import from the same package

logger = logging.getLogger(__name__)

# Singleton instance (primarily for standalone use or fallback)
_handler_registry_instance: Optional[HandlerRegistry] = None

def get_handler_registry() -> HandlerRegistry:
    """
    Get the singleton instance of the HandlerRegistry.

    Note: In most cases, the registry should be accessed via ServicesContainer.
    This provides a fallback or direct access method.

    Returns:
        HandlerRegistry: The singleton registry instance
    """
    global _handler_registry_instance
    if _handler_registry_instance is None:
        # Check if it's available via services first
        try:
            from core.services import get_services
            services = get_services()
            if services.has_service(HandlerRegistry):
                 _handler_registry_instance = services.handler_registry
                 logger.debug("Retrieved HandlerRegistry singleton from ServicesContainer.")
                 return _handler_registry_instance
        except ImportError:
             logger.warning("Could not import get_services. Falling back to direct HandlerRegistry instantiation.")
        except Exception as e:
             logger.warning(f"Error checking services for HandlerRegistry: {e}. Falling back to direct instantiation.")

        # Fallback: Create a new instance if not found in services or services unavailable
        _handler_registry_instance = HandlerRegistry()
        logger.debug("Created new HandlerRegistry singleton instance (fallback).")
    return _handler_registry_instance

def reset_handler_registry() -> None:
    """
    Reset the singleton handler registry instance.
    Used for testing. Also consider resetting via ServicesContainer.reset().
    """
    global _handler_registry_instance
    _handler_registry_instance = None
    # Also reset within services if possible
    try:
        from core.services import get_services
        services = get_services()
        # Attempt to reset/remove from services container? Requires specific method.
        # For now, just reset the local singleton reference.
    except ImportError:
        pass # Services not available
    logger.debug("Reset HandlerRegistry singleton instance reference.")


def register_handler(name: str, handler: Callable, replace: bool = False) -> bool:
    """
    Register a handler with the registry.

    Args:
        name: The name of the handler
        handler: The handler function
        replace: Whether to replace an existing handler with the same name

    Returns:
        bool: True if registration was successful
    """
    registry = get_handler_registry()

    # Check if handler already exists
    if name in registry.list_handlers() and not replace:
        logger.warning(f"Handler '{name}' already registered and replace=False")
        return False

    try:
        if name in registry.list_handlers() and replace:
             # Assuming HandlerRegistry has a remove method, otherwise direct dict access
             if hasattr(registry, 'remove_handler'):
                 registry.remove_handler(name)
             else:
                 # Direct modification if necessary (less ideal)
                 if hasattr(registry, '_handlers'):
                     if name in registry._handlers: # Accessing protected member potentially
                         del registry._handlers[name]
             logger.debug(f"Removed existing handler '{name}' for replacement")

        registry.register_handler(name, handler)
        logger.debug(f"Successfully registered handler '{name}'")
        return True
    except Exception as e:
        logger.error(f"Failed to register handler '{name}': {e}")
        return False

# Note: Handler execution might not have a standardized 'execute_handler' function
# like execute_tool. Handlers are often retrieved and called directly.
# If needed, an execute_handler function could be added here.

def get_handler(name: str) -> Optional[Callable]:
    """
    Get a handler function by name.

    Args:
        name: The name of the handler to retrieve.

    Returns:
        Optional[Callable]: The handler function, or None if not found.
    """
    registry = get_handler_registry()
    try:
        return registry.get_handler(name)
    except KeyError:
        logger.warning(f"Handler '{name}' not found in registry.")
        return None

def list_handlers() -> List[str]:
    """
    Get a list of names of all registered handlers.

    Returns:
        List[str]: A list of handler names.
    """
    registry = get_handler_registry()
    return registry.list_handlers()

def handler_exists(name: str) -> bool:
    """
    Check if a handler exists in the registry.

    Args:
        name: The name of the handler to check

    Returns:
        bool: True if the handler exists, False otherwise
    """
    registry = get_handler_registry()
    # Use list_handlers() method rather than accessing protected member directly
    return name in registry.list_handlers() 