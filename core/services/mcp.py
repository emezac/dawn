"""
Mission Control Protocol (MCP) service.

This module provides a service interface for working with MCP servers,
handling configuration management, client initialization, and tool calling.
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Awaitable

from core.mcp.client import MCPClient, MCPClientError, MCPToolError
from core.mcp.config import MCPConfiguration, MCPServerConfig
from core.mcp.schema import MCPTool, MCPNotification

logger = logging.getLogger(__name__)

T = TypeVar('T')


class MCPService:
    """
    Service for interacting with MCP servers.
    
    This class provides a high-level interface for working with MCP servers,
    including connection management and tool execution.
    """  # noqa: D202
    
    _instance: Optional['MCPService'] = None
    _config: Optional[MCPConfiguration] = None
    _clients: Dict[str, MCPClient] = {}
    
    @classmethod
    def initialize(cls, config_path: Optional[str] = None) -> 'MCPService':
        """
        Initialize the MCP service with configuration.
        
        Args:
            config_path: Optional path to configuration file.
            
        Returns:
            The service instance.
        """
        if cls._instance is None:
            cls._instance = MCPService()
            
        # Load configuration if needed
        if config_path or cls._config is None:
            cls._config = MCPConfiguration.load(config_path)
            # Clear existing clients since config changed
            cls._clients = {}
            
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'MCPService':
        """
        Get the singleton instance of the service.
        
        Returns:
            The service instance.
            
        Raises:
            RuntimeError: If the service has not been initialized.
        """
        if cls._instance is None:
            raise RuntimeError("MCPService has not been initialized. Call MCPService.initialize() first.")
        return cls._instance
    
    def get_client(self, server_name: Optional[str] = None) -> MCPClient:
        """
        Get or create an MCP client for the specified server.
        
        Args:
            server_name: Name of the server to connect to. If None, uses the default server.
            
        Returns:
            The MCP client.
            
        Raises:
            RuntimeError: If no configuration is loaded.
            ValueError: If the server name is not found in the configuration.
        """
        if self._config is None:
            raise RuntimeError("No MCP configuration loaded.")
            
        if server_name is None:
            server_name = self._config.default_server
            
        if server_name not in self._clients:
            # Create a new client
            self._clients[server_name] = MCPClient(server_name)
            
        return self._clients[server_name]
    
    async def connect_to_server(self, server_name: Optional[str] = None) -> MCPClient:
        """
        Connect to the specified MCP server.
        
        Args:
            server_name: Name of the server to connect to. If None, uses the default server.
            
        Returns:
            The connected MCP client.
            
        Raises:
            MCPClientError: If connection fails.
        """
        client = self.get_client(server_name)
        await client.connect()
        return client
    
    async def list_tools(self, server_name: Optional[str] = None) -> List[MCPTool]:
        """
        List the tools available on the specified server.
        
        Args:
            server_name: Name of the server to query. If None, uses the default server.
            
        Returns:
            List of available tools.
            
        Raises:
            MCPClientError: If the operation fails.
        """
        async with self.get_client(server_name).connection() as client:
            return await client.list_tools()
    
    async def call_tool(self, 
                        tool_name: str, 
                        parameters: Dict[str, Any], 
                        server_name: Optional[str] = None,
                        timeout: Optional[float] = None) -> Any:
        """
        Call a tool on the specified server.
        
        Args:
            tool_name: Name of the tool to call.
            parameters: Parameters to pass to the tool.
            server_name: Name of the server to use. If None, uses the default server.
            timeout: Optional timeout in seconds.
            
        Returns:
            The result of the tool call.
            
        Raises:
            MCPClientError: If the operation fails.
        """
        async with self.get_client(server_name).connection() as client:
            return await client.call_tool(tool_name, parameters, timeout)
    
    def register_notification_handler(self, 
                                     handler: Callable[[MCPNotification], Any],
                                     server_name: Optional[str] = None) -> None:
        """
        Register a handler for notification messages from the specified server.
        
        Args:
            handler: A callable that takes a notification message and processes it.
            server_name: Name of the server to handle notifications from. If None, uses the default server.
        """
        client = self.get_client(server_name)
        client.register_notification_handler(handler)
    
    def unregister_notification_handler(self, 
                                       handler: Callable[[MCPNotification], Any],
                                       server_name: Optional[str] = None) -> None:
        """
        Unregister a notification handler from the specified server.
        
        Args:
            handler: The handler to unregister.
            server_name: Name of the server to unregister from. If None, uses the default server.
        """
        client = self.get_client(server_name)
        client.unregister_notification_handler(handler)
    
    @staticmethod
    def handle_errors(default_value: Optional[T] = None) -> Callable:
        """
        Decorator to handle MCP errors gracefully.
        
        Args:
            default_value: Value to return if an error occurs.
            
        Returns:
            Decorated function.
        """
        def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[Union[T, None]]]:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Union[T, None]:
                try:
                    return await func(*args, **kwargs)
                except MCPToolError as e:
                    logger.error(f"MCP tool error: {str(e)}")
                    return default_value
                except MCPClientError as e:
                    logger.error(f"MCP client error: {str(e)}")
                    return default_value
                except Exception as e:
                    logger.error(f"Unexpected error in MCP operation: {str(e)}")
                    return default_value
            return wrapper
        return decorator


# Convenience access to the singleton instance
def get_mcp_service() -> MCPService:
    """
    Get the singleton MCP service instance.
    
    Returns:
        The MCP service instance.
    """
    return MCPService.get_instance() 