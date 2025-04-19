#!/usr/bin/env python3
"""
Mission Control Protocol (MCP) client implementation

This module provides the client implementation for interacting with MCP servers,
including connecting to servers, listing available tools, and calling tools.
"""  # noqa: D202

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
import os
from pathlib import Path

import aiohttp
from aiohttp import ClientSession, ClientError

from core.mcp.schema import (
    MCPTool, 
    MCPToolResponse, 
    MCPNotification, 
    NotificationType,
    MCPError, 
    MCPConnectionError, 
    MCPToolError,
    MCPServerConfig,
    MCPConfig
)


logger = logging.getLogger(__name__)


class MCPError(Exception):
    """Excepción base para errores del MCP"""
    pass

class ConnectionError(MCPError):
    """Error al conectar con el servidor MCP"""
    pass

class AuthenticationError(MCPError):
    """Error de autenticación con el servidor MCP"""
    pass

class ToolExecutionError(MCPError):
    """Error al ejecutar una herramienta"""
    pass


class MCPClient:
    """
    Client for interacting with MCP servers.
    """  # noqa: D202
    
    def __init__(
        self,
        server_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        notification_handler: Optional[Callable] = None,
    ):
        """
        Initialize an MCP client.
        
        Args:
            server_url: URL of the MCP server
            api_key: API key for authentication (optional)
            timeout: Maximum wait time for requests (seconds)
            max_retries: Maximum number of retries for failed requests
            retry_delay: Wait time between retries (seconds)
            notification_handler: Function for handling notifications from the server
        """
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.notification_handler = notification_handler
        
        self.session = None
        self.connected = False
        self._available_tools = None
    
    async def connect(self) -> bool:
        """
        Connect to the MCP server.
        
        Returns:
            True if connection was successful, False otherwise
        """
        if self.connected:
            return True
            
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=self._get_headers()
            )
            
            # Try a simple request to check connectivity
            async with self.session.get(f"{self.server_url}/health") as response:
                if response.status != 200:
                    await self.disconnect()
                    raise ConnectionError(f"Error al conectar con el servidor: {response.status}")
                
                self.connected = True
                logger.debug(f"Conectado exitosamente a {self.server_url}")
                return True
                
        except aiohttp.ClientError as e:
            await self.disconnect()
            raise ConnectionError(f"Error al conectar con el servidor: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close the connection to the MCP server."""
        if self.session:
            await self.session.close()
            self.session = None
        
        self.connected = False
        logger.debug("Desconectado del servidor MCP")
    
    async def list_tools(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        List available tools on the MCP server.
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            List of dictionaries with tool information
            
        Raises:
            ConnectionError: If not connected to the server
        """
        if not self.connected:
            raise ConnectionError("No hay conexión con el servidor")
            
        # Use cached tools if available and not expired
        if self._available_tools is not None and not force_refresh:
            return self._available_tools
        
        try:
            async with self.session.get(f"{self.server_url}/tools") as response:
                if response.status != 200:
                    if response.status == 401:
                        raise AuthenticationError("Credenciales inválidas")
                    else:
                        raise ConnectionError(f"Error al obtener herramientas: {response.status}")
                
                self._available_tools = await response.json()
                return self._available_tools
                
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Error al obtener herramientas: {str(e)}")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool
            
        Returns:
            Tool response with results
            
        Raises:
            ConnectionError: If not connected to the server
            ToolExecutionError: If the tool call fails
        """
        if not self.connected:
            raise ConnectionError("No hay conexión con el servidor")
            
        payload = {
            "tool": tool_name,
            "parameters": parameters
        }
        
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                async with self.session.post(
                    f"{self.server_url}/execute",
                    json=payload
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise AuthenticationError("Credenciales inválidas")
                    elif response.status == 404:
                        raise ToolExecutionError(f"Herramienta no encontrada: {tool_name}")
                    else:
                        error_text = await response.text()
                        logger.warning(f"Error al ejecutar herramienta (intento {retry_count+1}/{self.max_retries+1}): {response.status} - {error_text}")
                        
                        if retry_count >= self.max_retries:
                            raise ToolExecutionError(f"Error al ejecutar herramienta: {response.status} - {error_text}")
                        
                        retry_count += 1
                        await asyncio.sleep(self.retry_delay)
                        
            except aiohttp.ClientError as e:
                logger.warning(f"Error de conexión (intento {retry_count+1}/{self.max_retries+1}): {str(e)}")
                
                if retry_count >= self.max_retries:
                    raise ConnectionError(f"Error al ejecutar herramienta: {str(e)}")
                
                retry_count += 1
                await asyncio.sleep(self.retry_delay)
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Genera los encabezados HTTP para las peticiones.
        
        Returns:
            Diccionario con los encabezados
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers


class MCPService:
    """
    Service for managing multiple MCP server connections.
    """  # noqa: D202
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MCP service.
        
        Args:
            config: Service configuration
        """
        self.config = config
        self.clients: Dict[str, MCPClient] = {}
        self.default_server = config.get("default_server")
        
        # Configurar nivel de log
        log_level = config.get("log_level", "INFO")
        logging.getLogger("mcp").setLevel(getattr(logging, log_level))
        
        # Inicializar clientes
        for server_name, server_config in config.get("servers", {}).items():
            self.clients[server_name] = MCPClient(
                server_url=server_config["url"],
                api_key=server_config.get("api_key"),
                timeout=server_config.get("timeout", 30),
                max_retries=server_config.get("max_retries", 3),
                retry_delay=server_config.get("retry_delay", 1.0)
            )
    
    def get_client(self, server_name: Optional[str] = None) -> MCPClient:
        """
        Get or create an MCP client for the specified server.
        
        Args:
            server_name: Name of the server to connect to, or None for default
            
        Returns:
            MCP client instance
            
        Raises:
            ValueError: If the server does not exist
        """
        if server_name is None:
            if self.default_server is None:
                raise ValueError("No se ha especificado un servidor por defecto")
            server_name = self.default_server
            
        if server_name not in self.clients:
            raise ValueError(f"Servidor no encontrado: {server_name}")
            
        return self.clients[server_name]
    
    async def connect_all(self) -> Dict[str, bool]:
        """
        Connect to all configured servers.
        
        Returns:
            Dictionary mapping server names to connection status (True/False)
        """
        results = {}
        
        for server_name, client in self.clients.items():
            try:
                results[server_name] = await client.connect()
            except ConnectionError as e:
                logger.error(f"Error al conectar con {server_name}: {str(e)}")
                results[server_name] = False
        
        return results
    
    async def disconnect_all(self) -> None:
        """Disconnect from all servers."""
        for client in self.clients.values():
            await client.disconnect()
    
    async def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List tools available on all connected servers.
        
        Returns:
            Dictionary mapping server names to lists of available tools
        """
        results = {}
        
        for server_name, client in self.clients.items():
            if client.connected:
                try:
                    results[server_name] = await client.list_tools()
                except (ConnectionError, AuthenticationError) as e:
                    logger.error(f"Error al listar herramientas en {server_name}: {str(e)}")
                    results[server_name] = []
            else:
                results[server_name] = []
        
        return results


async def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load MCP configuration from a file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict with the configuration
    """
    if isinstance(config_path, str):
        config_path = Path(config_path)
        
    if not config_path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError:
        raise ValueError(f"El archivo {config_path} no contiene JSON válido") 