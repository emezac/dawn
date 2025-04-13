"""
Provides a central container for accessing framework-wide singleton services.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar, Generic, Union, cast

from .tools.registry import ToolRegistry
from .tools.registry_access import get_registry as get_tool_registry_singleton
from .tools.registry_access import reset_registry as reset_tool_registry_singleton
from .llm.interface import LLMInterface
from .handlers.registry import HandlerRegistry

logger = logging.getLogger(__name__)

# Type variable for service classes
T = TypeVar('T')

class ServiceEntry(Generic[T]):
    """
    Container for a service instance with metadata.
    """
    def __init__(self, instance: T, service_type: Type[T], name: str):
        self.instance = instance
        self.service_type = service_type
        self.name = name


class ServicesContainer:
    """
    Manages singleton instances of core framework services.
    
    This container provides centralized access to shared services like
    ToolRegistry, LLMInterface, etc. It ensures that only one instance
    of each service exists throughout the application.
    """
    def __init__(self):
        self._services: Dict[str, ServiceEntry[Any]] = {}
        self._initialized = False
        self._tool_registry = None
        self._handler_registry = None
        self._llm_interfaces = {}
        logger.debug("ServicesContainer initialized.")
        
    def initialize(self) -> None:
        """
        Initialize built-in services if not already done.
        """
        if self._initialized:
            return
            
        # Register the ToolRegistry singleton
        self.register_service(
            get_tool_registry_singleton(), 
            ToolRegistry,
            "tool_registry"
        )
        
        # Initialize the handler registry if not already initialized
        if self._handler_registry is None:
            self._handler_registry = HandlerRegistry()
            self.register_service(
                self._handler_registry,
                HandlerRegistry,
                "handler_registry"
            )
        
        self._initialized = True
        logger.debug("ServicesContainer initialized with default services.")

    @property
    def tool_registry(self) -> ToolRegistry:
        """
        Provides access to the singleton ToolRegistry instance.
        Initializes it on first access.
        """
        self.initialize()
        if self._tool_registry is None:
            self._tool_registry = ToolRegistry()
        return self._tool_registry

    @property
    def handler_registry(self) -> HandlerRegistry:
        """Get the global handler registry.
        
        Creates a new handler registry if one doesn't exist.
        
        Returns:
            HandlerRegistry: The global handler registry
        """
        self.initialize()
        if self._handler_registry is None:
            self._handler_registry = HandlerRegistry()
            self.register_service(
                self._handler_registry,
                HandlerRegistry,
                "handler_registry"
            )
        return self._handler_registry

    def register_service(self, instance: T, service_type: Type[T], name: Optional[str] = None) -> None:
        """
        Register a service instance with the container.
        
        Args:
            instance: The service instance to register
            service_type: The type of the service (used for type-based lookups)
            name: Optional name for the service (defaults to the class name)
        """
        service_name = name or service_type.__name__
        entry = ServiceEntry(instance, service_type, service_name)
        
        # Check if service already exists
        if service_name in self._services:
            logger.warning(f"Service '{service_name}' already registered. Overwriting.")
            
        self._services[service_name] = entry
        logger.debug(f"Registered service: {service_name}")

    def get_service(self, service_type_or_name: Union[Type[T], str]) -> Any:
        """
        Get a service by its type or name.
        
        Args:
            service_type_or_name: Either a type (class) or a string name
            
        Returns:
            The service instance
            
        Raises:
            KeyError: If the service is not found
        """
        self.initialize()
        
        # Handle lookup by type
        if isinstance(service_type_or_name, type):
            service_type = service_type_or_name
            # Find the first service that matches this type
            for entry in self._services.values():
                if entry.service_type is service_type or issubclass(entry.service_type, service_type):
                    return entry.instance
            raise KeyError(f"No service registered for type {service_type.__name__}")
        
        # Handle lookup by name
        service_name = service_type_or_name
        if service_name not in self._services:
            raise KeyError(f"No service registered with name '{service_name}'")
            
        return self._services[service_name].instance
        
    def get_service_typed(self, service_type: Type[T], name: Optional[str] = None) -> T:
        """
        Get a service with proper type casting.
        
        Args:
            service_type: The type (class) of the service
            name: Optional name to disambiguate services of the same type
            
        Returns:
            The service instance with the correct type
        """
        if name:
            return cast(service_type, self.get_service(name))
        return cast(service_type, self.get_service(service_type))
        
    def has_service(self, service_type_or_name: Union[Type, str]) -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_type_or_name: Either a type (class) or a string name
            
        Returns:
            True if the service is registered, False otherwise
        """
        self.initialize()
        
        # Handle lookup by type
        if isinstance(service_type_or_name, type):
            service_type = service_type_or_name
            # Find the first service that matches this type
            for entry in self._services.values():
                if entry.service_type is service_type or issubclass(entry.service_type, service_type):
                    return True
            return False
        
        # Handle lookup by name
        return service_type_or_name in self._services

    def register_llm_interface(self, llm_interface: LLMInterface, name: str = "default_llm") -> None:
        """
        Register an LLMInterface instance.
        
        Args:
            llm_interface: The LLMInterface instance
            name: Optional name for the LLM interface
        """
        self.register_service(llm_interface, LLMInterface, name)

    def get_llm_interface(self, name: str = "default_llm") -> LLMInterface:
        """
        Get the LLMInterface instance.
        
        Args:
            name: The name of the LLM interface to get
            
        Returns:
            The LLMInterface instance
            
        Raises:
            KeyError: If no LLM interface is registered with the given name
        """
        try:
            return self.get_service_typed(LLMInterface, name)
        except KeyError:
            # If no LLM interface is registered, create a mock interface
            from .llm.mock_interface import MockLLMInterface
            llm_interface = MockLLMInterface()
            self.register_llm_interface(llm_interface, name)
            logger.warning(f"Created mock LLM interface with name '{name}'")
            return llm_interface
    
    def reset(self) -> None:
        """
        Reset the container, clearing all services.
        Primarily used for testing.
        """
        self._services.clear()
        self._tool_registry = None
        self._handler_registry = None
        self._llm_interfaces = {}
        self._initialized = False
        
        # Reset the global tool registry singleton
        reset_tool_registry_singleton()
        
        logger.debug("ServicesContainer reset.")
    
    def register_tool_registry(self, registry: ToolRegistry) -> None:
        """
        Register a custom tool registry.
        
        Args:
            registry: The tool registry to register
        """
        self._tool_registry = registry
        self.register_service(registry, ToolRegistry, "tool_registry")
        logger.debug("Custom ToolRegistry registered.")
        
    def register_handler_registry(self, registry: HandlerRegistry) -> None:
        """
        Register a custom handler registry.
        
        Args:
            registry: The handler registry to register
        """
        self._handler_registry = registry
        self.register_service(registry, HandlerRegistry, "handler_registry")
        logger.debug("Custom HandlerRegistry registered.")
        
    def create_workflow_engine(self, workflow):
        """
        Create a workflow engine with all necessary dependencies.
        
        Args:
            workflow: The workflow to execute
            
        Returns:
            A WorkflowEngine instance with all dependencies injected
        """
        from .workflow_engine import WorkflowEngine
        return WorkflowEngine(
            workflow=workflow,
            llm_interface=self.get_llm_interface(),
            tool_registry=self.tool_registry,
            handler_registry=self.handler_registry
        )


# Global singleton instance
_services_instance = None

def get_services() -> ServicesContainer:
    """
    Get the global services container instance.
    
    Returns:
        The global ServicesContainer instance
    """
    global _services_instance
    if _services_instance is None:
        _services_instance = ServicesContainer()
    return _services_instance

def reset_services() -> None:
    """
    Reset the global services container.
    Primarily used for testing.
    """
    global _services_instance
    if _services_instance is not None:
        _services_instance.reset()
    _services_instance = None
    logger.debug("Global ServicesContainer reset.")
    
def get_handler_registry() -> HandlerRegistry:
    """
    Get the global handler registry instance.
    
    Returns:
        The global HandlerRegistry instance
    """
    return get_services().handler_registry 