#!/usr/bin/env python3
"""
Adaptador MCP para el Protocolo de Tiempo.

Este script implementa un adaptador que expone el Protocolo de Tiempo (RFC 868)
como una herramienta MCP.
"""  # noqa: D202

import argparse
import asyncio
import datetime
import json
import logging
import socket
import struct
import sys
import time
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_time_adapter")

# El protocolo de tiempo utiliza el 1 de enero de 1900 como base
TIME_1900_EPOCH = 2208988800  # segundos desde 1970-01-01 hasta 1900-01-01

# Ruta base del proyecto
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Intentar importar los módulos MCP
try:
    from core.mcp.service import MCPService, load_config, ToolRequest
except ImportError as e:
    logger.error(f"Error al importar módulos MCP: {e}")
    logger.error("Asegúrate de estar en el directorio correcto y que los módulos estén disponibles")
    sys.exit(1)

def get_time_from_server(host, port=37, timeout=5):
    """
    Obtiene la hora de un servidor de tiempo (RFC 868).
    
    Args:
        host: Nombre o dirección IP del servidor
        port: Puerto del servidor (por defecto 37)
        timeout: Tiempo de espera para la conexión en segundos
        
    Returns:
        Objeto datetime con la hora recibida del servidor
    """
    # Crear socket TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(timeout)
    
    try:
        # Conectar al servidor
        logger.debug(f"Conectando a {host}:{port}...")
        client_socket.connect((host, port))
        
        # Recibir 4 bytes (32 bits) con el tiempo
        data = client_socket.recv(4)
        if len(data) != 4:
            raise ValueError(f"Se esperaban 4 bytes de datos, pero se recibieron {len(data)}")
        
        # Convertir los bytes recibidos a un entero de 32 bits (big-endian)
        seconds_since_1900 = struct.unpack('!I', data)[0]
        
        # Convertir el tiempo recibido a tiempo UNIX (segundos desde 1970)
        seconds_since_1970 = seconds_since_1900 - TIME_1900_EPOCH
        
        # Convertir a un objeto datetime
        time_obj = datetime.datetime.fromtimestamp(seconds_since_1970)
        
        return time_obj
        
    finally:
        # Cerrar el socket
        client_socket.close()

async def get_time_handler(request):
    """
    Manejador MCP para obtener la hora de un servidor de tiempo.
    
    Args:
        request: Solicitud MCP
        
    Returns:
        Resultado con la hora obtenida
    """
    # Obtener parámetros
    parameters = request.parameters
    host = parameters.get("host", "localhost")
    port = int(parameters.get("port", 3737))
    timeout = int(parameters.get("timeout", 5))
    
    try:
        # Obtener la hora del servidor
        time_obj = get_time_from_server(host, port, timeout)
        
        # Formatear la respuesta
        result = {
            "status": "success",
            "time": time_obj.isoformat(),
            "timestamp": time_obj.timestamp(),
            "local_time": datetime.datetime.now().isoformat()
        }
        
        return result
    except Exception as e:
        logger.error(f"Error al obtener la hora: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

async def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Adaptador MCP para el Protocolo de Tiempo")
    parser.add_argument("--host", default="localhost", help="Host del servidor MCP")
    parser.add_argument("--port", type=int, default=8080, help="Puerto del servidor MCP")
    parser.add_argument("--time-host", default="localhost", help="Host del servidor de tiempo")
    parser.add_argument("--time-port", type=int, default=3737, help="Puerto del servidor de tiempo")
    parser.add_argument("--config", help="Ruta al archivo de configuración MCP")
    
    args = parser.parse_args()
    
    # Configuración para el servidor MCP
    config_data = {
        "host": args.host,
        "port": args.port,
        "api_key": "dawn-mcp-demo-key",
        "log_level": "INFO",
        "cors_origins": ["*"],
        "tools": [
            {
                "name": "get_time",
                "description": "Obtiene la hora actual del servidor de tiempo",
                "parameters": [
                    {
                        "name": "host",
                        "description": "Host del servidor de tiempo",
                        "type": "string",
                        "required": False,
                        "default": args.time_host
                    },
                    {
                        "name": "port",
                        "description": "Puerto del servidor de tiempo",
                        "type": "integer",
                        "required": False,
                        "default": args.time_port
                    },
                    {
                        "name": "timeout",
                        "description": "Tiempo de espera en segundos",
                        "type": "integer",
                        "required": False,
                        "default": 5
                    }
                ]
            }
        ]
    }
    
    # Cargar configuración desde archivo si se especificó
    if args.config:
        try:
            config_path = Path(args.config)
            if config_path.exists():
                logger.info(f"Cargando configuración desde {args.config}")
                config = await load_config(args.config)
            else:
                logger.warning(f"Archivo de configuración no encontrado: {args.config}")
                logger.info("Usando configuración por defecto")
                config = config_data
        except Exception as e:
            logger.error(f"Error al cargar configuración: {str(e)}")
            logger.info("Usando configuración por defecto")
            config = config_data
    else:
        config = config_data
    
    # Crear servicio MCP
    service = MCPService(config)
    
    # Registrar manejador para la herramienta get_time
    async def execute_get_time(request):
        return await get_time_handler(request)
    
    # Sobrescribir el método execute del servicio para manejar nuestra herramienta
    original_execute = service.app.post("/execute")
    
    @service.app.post("/execute")
    async def execute_tool(request: ToolRequest):
        if request.tool == "get_time":
            return await get_time_handler(request)
        return await original_execute(request)
    
    # Iniciar el servicio
    logger.info(f"Iniciando servicio MCP en {config['host']}:{config['port']}")
    logger.info(f"Configurado para usar servidor de tiempo en {args.time_host}:{args.time_port}")
    
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Servicio detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en el servicio: {str(e)}")
    finally:
        await service.stop()
        logger.info("Servicio detenido")

if __name__ == "__main__":
    asyncio.run(main()) 