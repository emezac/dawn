"""
Configuration module for MCP (Mission Control Protocol) integration.

This module provides classes and utilities for configuring MCP servers.
"""

import os
import yaml
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from pydantic import BaseModel, Field, validator


class MCPTransportType(str, Enum):
    """Supported MCP transport protocols."""
    STDIO = "stdio"
    TCP = "tcp"
    # Future support may include HTTP, WebSockets, etc.


class MCPStdioConfig(BaseModel):
    """Configuration for stdio-based MCP server."""
    command: str = Field(..., description="The command to execute the MCP server.")
    args: List[str] = Field(default_factory=list, description="Arguments for the command.")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables for the process.")
    cwd: Optional[str] = None

    @validator('command')
    def command_must_be_executable(cls, v):
        """Validate that the command exists and is executable."""
        # Simple check - could be enhanced to verify executable exists in PATH
        if not v or not isinstance(v, str):
            raise ValueError("Command must be a non-empty string")
        return v


class MCPTCPConfig(BaseModel):
    """Configuration for TCP transport."""
    host: str = "localhost"
    port: int
    use_ssl: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ca_cert_path: Optional[str] = None


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    alias: str = Field(..., description="Unique identifier for this MCP server.")
    type: MCPTransportType = Field(..., description="Transport protocol type.")
    enabled: bool = Field(default=True, description="Whether this server should be enabled.")
    
    # Transport-specific configuration
    stdio_config: Optional[MCPStdioConfig] = Field(
        None, description="Configuration for stdio transport (required if type is stdio)."
    )
    tcp_config: Optional[MCPTCPConfig] = None
    
    @validator('stdio_config')
    def stdio_config_required_for_stdio_type(cls, v, values):
        """Validate that stdio_config is provided when type is stdio."""
        if values.get('type') == MCPTransportType.STDIO and not v:
            raise ValueError("stdio_config is required when type is stdio")
        return v


class MCPConfiguration(BaseModel):
    """Global MCP configuration with all servers."""
    servers: Dict[str, MCPServerConfig] = Field(
        default_factory=dict, 
        description="Dictionary of MCP servers, keyed by alias."
    )
    auto_discover: bool = Field(
        default=True,
        description="Automatically discover and register tools on startup."
    )
    default_server: Optional[str] = None
    
    @validator('servers')
    def server_alias_must_match_key(cls, v):
        """Ensure each server's alias matches its key in the dictionary."""
        for key, server in v.items():
            if server.alias != key:
                raise ValueError(f"Server alias '{server.alias}' must match key '{key}'")
        return v

    def get_server_config(self, server_name: Optional[str] = None) -> MCPServerConfig:
        """
        Get configuration for a specific server or the default server.
        
        Args:
            server_name: Name of the server to get configuration for.
                If None, the default server will be used.
                
        Returns:
            The server configuration.
            
        Raises:
            ValueError: If the server name is invalid or no default is set.
        """
        if server_name is None:
            if self.default_server is None:
                raise ValueError("No default server configured")
            server_name = self.default_server
            
        if server_name not in self.servers:
            raise ValueError(f"Unknown server: {server_name}")
            
        return self.servers[server_name]


def load_mcp_config(config_path: Optional[Union[str, Path]] = None) -> MCPConfiguration:
    """
    Load MCP configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file.
                    If None, looks for 'mcp_config.yaml' in the current
                    directory or specified by MCP_CONFIG_PATH env variable.
    
    Returns:
        MCPConfiguration object with validated configuration.
    
    Raises:
        FileNotFoundError: If the config file doesn't exist.
        ValueError: If the config file has invalid format or content.
    """
    # Determine the configuration file path
    if config_path is None:
        config_path = os.environ.get("MCP_CONFIG_PATH", "mcp_config.yaml")
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"MCP configuration file not found: {config_path}")
    
    # Load and parse the YAML file
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Convert to our configuration model
    try:
        return MCPConfiguration.parse_obj(config_data)
    except Exception as e:
        raise ValueError(f"Invalid MCP configuration format: {e}") 