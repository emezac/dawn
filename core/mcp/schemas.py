"""
Pydantic schemas for MCP (Mission Control Protocol) messages and structures.

These schemas represent the data structures used in the MCP protocol
for communication between clients and servers.
"""

import json
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, root_validator


class InitializeRequest(BaseModel):
    """Request to initialize a session with an MCP server."""
    type: str = Field("initialize", const=True)
    message_id: str = Field(..., description="Unique identifier for this message.")
    content: Dict = Field(default_factory=dict, description="Additional initialization parameters.")


class InitializeResponse(BaseModel):
    """Response to an initialize request."""
    type: str = Field("initialize_response", const=True)
    message_id: str = Field(..., description="Unique identifier for this message.")
    request_id: str = Field(..., description="Message ID of the associated request.")
    success: bool = Field(..., description="Whether initialization was successful.")
    content: Optional[Dict] = Field(None, description="Additional information from initialization.")
    error: Optional[str] = Field(None, description="Error message if unsuccessful.")


class ListToolsRequest(BaseModel):
    """Request to list available tools from an MCP server."""
    type: str = Field("list_tools", const=True)
    message_id: str = Field(..., description="Unique identifier for this message.")


class MCPToolInfo(BaseModel):
    """Information about a tool provided by an MCP server."""
    name: str = Field(..., description="Unique name of the tool on the server.")
    description: str = Field("", description="Description of the tool's functionality.")
    input_schema: Dict = Field(..., description="JSON Schema for the tool's input.")


class ListToolsResponse(BaseModel):
    """Response to a list_tools request."""
    type: str = Field("list_tools_response", const=True)
    message_id: str = Field(..., description="Unique identifier for this message.")
    request_id: str = Field(..., description="Message ID of the associated request.")
    success: bool = Field(..., description="Whether the request was successful.")
    content: Optional[List[MCPToolInfo]] = Field(None, description="List of available tools.")
    error: Optional[str] = Field(None, description="Error message if unsuccessful.")


class CallToolRequest(BaseModel):
    """Request to call a tool on an MCP server."""
    type: str = Field("call_tool", const=True)
    message_id: str = Field(..., description="Unique identifier for this message.")
    content: Dict[str, Any] = Field(..., description="Content for the call_tool request.")
    
    @root_validator(pre=True)
    def validate_content(cls, values):
        """Ensure content has required fields."""
        content = values.get('content', {})
        if not isinstance(content, dict):
            raise ValueError("content must be a dictionary")
        
        if 'name' not in content:
            raise ValueError("content.name is required")
            
        if 'arguments' not in content:
            raise ValueError("content.arguments is required")
            
        return values


class CallToolResponse(BaseModel):
    """Response to a call_tool request."""
    type: str = Field("call_tool_response", const=True)
    message_id: str = Field(..., description="Unique identifier for this message.")
    request_id: str = Field(..., description="Message ID of the associated request.")
    success: bool = Field(..., description="Whether the tool call was successful.")
    content: Optional[Any] = Field(None, description="Result from the tool call.")
    error: Optional[str] = Field(None, description="Error message if unsuccessful.")


class MCPRequestMessage(BaseModel):
    """Generic MCP request message."""
    type: str = Field(..., description="The type of the message.")
    message_id: str = Field(..., description="Unique identifier for this message.")
    content: Optional[Dict[str, Any]] = Field(None, description="Message content.")


class MCPResponseMessage(BaseModel):
    """Generic MCP response message."""
    type: str = Field(..., description="The type of the message, ending with '_response'.")
    message_id: str = Field(..., description="Unique identifier for this message.")
    request_id: str = Field(..., description="Message ID of the associated request.")
    success: bool = Field(..., description="Whether the request was successful.")
    content: Optional[Any] = Field(None, description="Response content.")
    error: Optional[str] = Field(None, description="Error message if unsuccessful.")


# Mapping from request type to expected response type
REQUEST_TO_RESPONSE_TYPE = {
    "initialize": "initialize_response",
    "list_tools": "list_tools_response",
    "call_tool": "call_tool_response"
}


def parse_mcp_message(message_str: str) -> Union[MCPRequestMessage, MCPResponseMessage]:
    """
    Parse an MCP message from a string.
    
    Args:
        message_str: String representation of the MCP message.
        
    Returns:
        Parsed MCPRequestMessage or MCPResponseMessage.
        
    Raises:
        ValueError: If the message cannot be parsed or has an invalid format.
    """
    try:
        # Parse the JSON string
        data = json.loads(message_str)
        
        # Validate that it has a type
        if 'type' not in data:
            raise ValueError("MCP message must have a 'type' field")
            
        message_type = data['type']
        
        # Determine the specific message type and parse accordingly
        if message_type == "initialize":
            return InitializeRequest.parse_obj(data)
        elif message_type == "initialize_response":
            return InitializeResponse.parse_obj(data)
        elif message_type == "list_tools":
            return ListToolsRequest.parse_obj(data)
        elif message_type == "list_tools_response":
            return ListToolsResponse.parse_obj(data)
        elif message_type == "call_tool":
            return CallToolRequest.parse_obj(data)
        elif message_type == "call_tool_response":
            return CallToolResponse.parse_obj(data)
        else:
            # Generic parsing based on whether it's a request or response
            if message_type.endswith("_response"):
                return MCPResponseMessage.parse_obj(data)
            else:
                return MCPRequestMessage.parse_obj(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in MCP message: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing MCP message: {e}") 