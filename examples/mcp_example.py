#!/usr/bin/env python3
"""
Example script for using the MCP service.

This example shows how to initialize the MCP service, connect to servers,
list available tools, and call tools.
"""  # noqa: D202

import argparse
import asyncio
import logging
import os
import sys
from typing import Dict, Any, Optional

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.services.mcp import MCPService, get_mcp_service
from core.mcp.schema import MCPNotification

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_example")


def notification_handler(notification: MCPNotification) -> None:
    """Handler for MCP notifications."""
    logger.info(f"Received notification: {notification.type}")
    logger.info(f"Notification content: {notification.content}")


async def run_example(server_name: Optional[str] = None, tool_name: Optional[str] = None, 
                     tool_params: Optional[Dict[str, Any]] = None, config_path: Optional[str] = None) -> None:
    """
    Run the MCP service example.
    
    Args:
        server_name: Name of the server to connect to
        tool_name: Optional name of a tool to call
        tool_params: Optional parameters for the tool call
        config_path: Optional path to MCP configuration file
    """
    # Initialize the MCP service
    try:
        service = MCPService.initialize(config_path)
        logger.info("MCP service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP service: {e}")
        return

    # Register notification handler
    service.register_notification_handler(notification_handler, server_name)
    
    try:
        # List available tools
        tools = await service.list_tools(server_name)
        logger.info(f"Available tools on server {server_name or 'default'}:")
        for tool in tools:
            logger.info(f"  - {tool.name}: {tool.description}")
        
        # Call a specific tool if requested
        if tool_name:
            params = tool_params or {}
            logger.info(f"Calling tool '{tool_name}' with parameters: {params}")
            
            try:
                result = await service.call_tool(tool_name, params, server_name)
                logger.info(f"Tool result: {result}")
            except Exception as e:
                logger.error(f"Tool call failed: {e}")
        
    except Exception as e:
        logger.error(f"Error during MCP operations: {e}")
    finally:
        # Clean up
        service.unregister_notification_handler(notification_handler, server_name)
        logger.info("Example completed")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MCP Service Example")
    parser.add_argument("--server", help="Name of the MCP server to connect to")
    parser.add_argument("--config", help="Path to MCP configuration file")
    parser.add_argument("--tool", help="Name of tool to call")
    parser.add_argument("--param", nargs=2, action="append", metavar=("KEY", "VALUE"),
                       help="Tool parameter in the format 'key value'. Can be specified multiple times.")
    
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Process tool parameters if provided
    tool_params = {}
    if args.param:
        for key, value in args.param:
            # Try to convert to appropriate types (int, float, bool)
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit() and value.count('.') < 2:
                value = float(value)
            elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            # Keep as string otherwise
            tool_params[key] = value
    
    # Run the async example
    asyncio.run(run_example(args.server, args.tool, tool_params, args.config))


if __name__ == "__main__":
    main() 