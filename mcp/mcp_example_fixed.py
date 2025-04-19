#!/usr/bin/env python3
"""
Script de ejemplo para usar el cliente MCP.

Este ejemplo muestra cómo inicializar el cliente MCP, conectarse a servidores,
listar herramientas disponibles y llamar a herramientas.
"""  # noqa: D202

import argparse
import asyncio
import logging
import os
import sys
from typing import Dict, Any, Optional

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar directamente desde core.mcp
from core.mcp.client import MCPClient, load_config
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
    Run the MCP client example.
    
    Args:
        server_name: Name of the server to connect to
        tool_name: Optional name of a tool to call
        tool_params: Optional parameters for the tool call
        config_path: Path to MCP configuration file
    """
    if not config_path:
        logger.error("Configuration file path required")
        return
        
    try:
        # Cargar configuración
        config = await load_config(config_path)
        logger.info(f"Configuration loaded from {config_path}")
        
        # Si no se especificó un servidor, usar el default
        if server_name is None:
            server_name = config.get("default_server")
            if not server_name:
                logger.error("No server specified and no default server in config")
                return
                
        # Verificar que el servidor existe en la configuración
        server_configs = config.get("servers", {})
        if server_name not in server_configs:
            logger.error(f"Server '{server_name}' not found in configuration")
            return
            
        server_config = server_configs[server_name]
        
        # Crear cliente MCP
        client = MCPClient(
            server_url=server_config["url"],
            api_key=server_config.get("api_key"),
            timeout=server_config.get("timeout", 30),
            max_retries=server_config.get("max_retries", 3),
            retry_delay=server_config.get("retry_delay", 1.0)
        )
        
        logger.info(f"Connecting to MCP server: {server_name} ({server_config['url']})")
        
        # Conectar al servidor
        await client.connect()
        logger.info("Connected successfully")
        
        try:
            # Listar herramientas disponibles
            tools = await client.list_tools()
            logger.info(f"Available tools on {server_name}:")
            for tool in tools:
                logger.info(f"  - {tool.get('name')}: {tool.get('description', 'No description')}")
            
            # Llamar a una herramienta específica si se solicitó
            if tool_name:
                params = tool_params or {}
                logger.info(f"Calling tool '{tool_name}' with parameters: {params}")
                
                try:
                    result = await client.call_tool(tool_name, params)
                    logger.info(f"Tool result: {result}")
                except Exception as e:
                    logger.error(f"Tool call failed: {e}")
        finally:
            # Desconectar
            await client.disconnect()
            logger.info("Disconnected from server")
    
    except Exception as e:
        logger.error(f"Error during MCP operations: {e}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MCP Client Example")
    parser.add_argument("--server", help="Name of the MCP server to connect to")
    parser.add_argument("--config", required=True, help="Path to MCP configuration file")
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