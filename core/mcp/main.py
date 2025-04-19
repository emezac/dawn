#!/usr/bin/env python3
import os
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Optional

from .service import MCPService, load_config, MCPServiceConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("mcp.main")

async def run_service(config_path: Optional[str] = None) -> None:
    """
    Ejecuta el servicio MCP con la configuración proporcionada.
    
    Args:
        config_path: Ruta al archivo de configuración
    """
    try:
        # Cargar configuración
        if config_path:
            config = await load_config(config_path)
        else:
            # Configuración por defecto
            config = MCPServiceConfig()
        
        # Crear y ejecutar servicio
        service = MCPService(config)
        
        logger.info(f"Iniciando MCP Service en {config.host}:{config.port}")
        await service.start()
    except KeyboardInterrupt:
        logger.info("Servicio detenido por el usuario")
    except Exception as e:
        logger.error(f"Error al ejecutar el servicio: {str(e)}")
        raise

def main() -> None:
    """
    Punto de entrada principal para el servicio MCP.
    """
    parser = argparse.ArgumentParser(description="MCP Service")
    parser.add_argument(
        "--config", 
        "-c", 
        type=str, 
        help="Ruta al archivo de configuración JSON"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        help="Host para el servidor (sobreescribe la configuración)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        help="Puerto para el servidor (sobreescribe la configuración)"
    )
    parser.add_argument(
        "--api-key", 
        type=str, 
        help="Clave API para autenticación (sobreescribe la configuración)"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Nivel de log (sobreescribe la configuración)"
    )
    
    args = parser.parse_args()
    
    # Establecer nivel de log
    if args.log_level:
        logging.getLogger("mcp").setLevel(getattr(logging, args.log_level))
    
    # Buscar archivo de configuración
    config_path = args.config
    if not config_path:
        # Buscar en ubicaciones comunes
        possible_locations = [
            "./mcp_config.json",
            "./config/mcp_config.json",
            "~/.mcp/config.json",
            "/etc/mcp/config.json"
        ]
        
        for location in possible_locations:
            path = Path(os.path.expanduser(location))
            if path.exists():
                config_path = str(path)
                logger.info(f"Usando archivo de configuración encontrado: {config_path}")
                break
    
    try:
        # Ejecutar el servicio de forma asíncrona
        asyncio.run(run_service(config_path))
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 