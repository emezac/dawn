#!/usr/bin/env python3
"""
Handler Registry for Dawn workflow system.

This module defines a registry for storing and retrieving handler functions
that can be executed directly by DirectHandlerTask objects.
"""  # noqa: D202

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

HandlerType = Callable[[Dict[str, Any]], Dict[str, Any]]


class HandlerRegistry:
    """Registry for storing and retrieving handler functions.

    The HandlerRegistry allows for registering Python functions that can be
    executed directly by DirectHandlerTask objects within a workflow.
    """  # noqa: D202

    def __init__(self):
        """Initialize a new HandlerRegistry."""
        self._handlers: Dict[str, HandlerType] = {}
        logger.debug("Initialized HandlerRegistry")

    def register(self, name: Optional[str] = None) -> Callable[[HandlerType], HandlerType]:
        """Register a handler function with the registry.

        This can be used as a decorator:
            @handler_registry.register()
            def my_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
                # handler implementation
                return {"result": "success"}

        Args:
            name: Optional name to register the handler under. If not provided,
                 the function's name will be used.

        Returns:
            A decorator function that registers the decorated function.
        """
        def decorator(handler: HandlerType) -> HandlerType:
            handler_name = name or handler.__name__
            self.register_handler(handler_name, handler)
            return handler
        return decorator

    def register_handler(self, name: str, handler: HandlerType) -> None:
        """Register a handler function with a specific name.

        Args:
            name: The name to register the handler under
            handler: The handler function to register
        """
        if name in self._handlers:
            logger.warning(f"Handler '{name}' already registered. Overwriting.")

        # Verify that the handler has the correct signature (task, input_data)
        sig = inspect.signature(handler)
        # Allow for 2 parameters (task, input_data) or potentially 1 (input_data only)
        if len(sig.parameters) not in [1, 2]:
            logger.warning(
                f"Handler '{name}' has {len(sig.parameters)} parameters, expected 1 (input_data) or 2 (task, input_data). "
                "This may cause issues during execution."
            )
        
        self._handlers[name] = handler
        logger.debug(f"Registered handler '{name}'")

    def get_handler(self, name: str) -> Optional[HandlerType]:
        """Get a handler function by name.

        Args:
            name: The name of the handler to retrieve

        Returns:
            The handler function if found, None otherwise
        """
        handler = self._handlers.get(name)
        if handler is None:
            logger.warning(f"Handler '{name}' not found in registry")
        return handler

    def handler_exists(self, name: str) -> bool:
        """Check if a handler with the given name exists in the registry.
        
        Args:
            name: The name of the handler to check
            
        Returns:
            True if the handler exists, False otherwise
        """
        return name in self._handlers

    def execute_handler(self, name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a handler function by name.

        Args:
            name: The name of the handler to execute
            input_data: The input data to pass to the handler

        Returns:
            The result of the handler execution

        Raises:
            ValueError: If the handler is not found in the registry
            Exception: Any exception raised by the handler function
        """
        handler = self.get_handler(name)
        if handler is None:
            raise ValueError(f"Handler '{name}' not found in registry")

        try:
            result = handler(input_data)
            if not isinstance(result, dict):
                logger.warning(
                    f"Handler '{name}' returned {type(result)} instead of Dict. "
                    "Converting to Dict."
                )
                result = {"result": result}
            return result
        except Exception as e:
            logger.error(f"Error executing handler '{name}': {str(e)}")
            raise

    def list_handlers(self) -> List[str]:
        """List all registered handler names.

        Returns:
            A list of all registered handler names
        """
        return list(self._handlers.keys())

    def clear(self) -> None:
        """Clear all registered handlers."""
        self._handlers.clear()
        logger.debug("Cleared all handlers from registry") 