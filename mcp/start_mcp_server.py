#!/usr/bin/env python3
"""
Script para iniciar el servidor MCP-timeserver.

Este script ejecuta el comando uvx para iniciar el servidor MCP-timeserver
y maneja su ciclo de vida.
"""  # noqa: D202

import subprocess
import signal
import sys
import time
import logging
import argparse
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_server_starter")

# Variable para almacenar el proceso del servidor
server_process = None

def signal_handler(sig, frame):
    """Manejador para señales de interrupción."""
    logger.info("Recibida señal de interrupción, deteniendo servidor...")
    stop_server()
    sys.exit(0)

def start_server(server_name="MCP-timeserver", debug=False):
    """
    Inicia el servidor MCP.
    
    Args:
        server_name: Nombre del servidor a iniciar
        debug: Si se debe mostrar salida detallada
    """
    global server_process
    
    logger.info(f"Iniciando servidor MCP: {server_name}")
    
    command = ["uvx", server_name]
    
    if debug:
        stdout = None  # Mostrar en la consola
        stderr = None
    else:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    
    try:
        server_process = subprocess.Popen(
            command,
            stdout=stdout,
            stderr=stderr,
            text=True
        )
        
        # Esperar un momento para que el servidor se inicie
        time.sleep(2)
        
        if server_process.poll() is not None:
            # El proceso ya terminó
            if not debug:
                stdout, stderr = server_process.communicate()
                logger.error(f"Error al iniciar el servidor. Código: {server_process.returncode}")
                logger.error(f"Salida: {stdout}")
                logger.error(f"Error: {stderr}")
            return False
            
        logger.info(f"Servidor {server_name} iniciado con PID: {server_process.pid}")
        return True
        
    except FileNotFoundError:
        logger.error(f"Comando 'uvx' no encontrado. Asegúrate de que esté instalado y en el PATH.")
        return False
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {str(e)}")
        return False

def stop_server():
    """Detiene el servidor MCP si está en ejecución."""
    global server_process
    
    if server_process is not None:
        logger.info(f"Deteniendo servidor con PID: {server_process.pid}")
        
        try:
            # Intentar primero terminar suavemente
            server_process.terminate()
            
            # Esperar hasta 5 segundos para finalización limpia
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("El servidor no se detuvo en el tiempo asignado, forzando terminación...")
                server_process.kill()
            
            logger.info("Servidor detenido correctamente")
        except Exception as e:
            logger.error(f"Error al detener el servidor: {str(e)}")
        
        server_process = None

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Iniciador de servidor MCP")
    parser.add_argument("--server", default="MCP-timeserver", help="Nombre del servidor a iniciar")
    parser.add_argument("--debug", action="store_true", help="Mostrar salida detallada")
    args = parser.parse_args()
    
    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar servidor
    if start_server(args.server, args.debug):
        logger.info(f"Servidor {args.server} iniciado correctamente")
        logger.info("Presiona Ctrl+C para detener el servidor")
        
        try:
            # Mantener el script en ejecución hasta que sea interrumpido
            while True:
                # Verificar si el servidor sigue en ejecución
                if server_process.poll() is not None:
                    logger.error(f"El servidor se detuvo inesperadamente con código: {server_process.returncode}")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupción recibida, deteniendo servidor...")
        finally:
            stop_server()
    else:
        logger.error("No se pudo iniciar el servidor")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 