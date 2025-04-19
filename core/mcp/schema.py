#!/usr/bin/env python3
"""
Schema definitions for the Mission Control Protocol (MCP)

This module defines the data structures used by the MCP service for
communication with MCP servers, including tools, notifications, and responses.
"""  # noqa: D202

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Union


class NotificationType(Enum):
    """Types of notifications that can be received from an MCP server."""
    CONNECTED = auto()
    DISCONNECTED = auto()
    TOOL_CALLED = auto()
    TOOL_RESPONSE = auto()
    ERROR = auto()
    INFO = auto()
    CUSTOM = auto()


@dataclass
class MCPNotification:
    """Notification received from an MCP server."""
    type: NotificationType
    content: Dict[str, Any]
    server_name: Optional[str] = None
    timestamp: Optional[float] = None


@dataclass
class MCPToolParameter:
    """Definition of a parameter for an MCP tool."""
    name: str
    description: str
    type: str
    required: bool = False
    default: Any = None
    enum: Optional[List[Any]] = None


@dataclass
class MCPTool:
    """Definition of a tool available on an MCP server."""
    name: str
    description: str
    parameters: List[MCPToolParameter] = field(default_factory=list)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)


@dataclass
class MCPToolResponse:
    """Response from a tool call."""
    tool_name: str
    status: str  # 'success', 'error', etc.
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection."""
    url: str
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1


@dataclass
class MCPConfig:
    """Configuration for the MCP service."""
    servers: Dict[str, MCPServerConfig] = field(default_factory=dict)
    default_server: Optional[str] = None
    log_level: str = "INFO"
    max_connections: int = 5


class MCPError(Exception):
    """Base exception for MCP-related errors."""
    pass


class MCPConnectionError(MCPError):
    """Exception raised when there is an error connecting to an MCP server."""
    pass


class MCPToolError(MCPError):
    """Exception raised when there is an error calling a tool."""
    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.tool_name = tool_name
        self.details = details or {}
        super().__init__(f"Error calling tool '{tool_name}': {message}")


class MCPConfigError(MCPError):
    """Exception raised when there is an error with the MCP configuration."""
    pass 