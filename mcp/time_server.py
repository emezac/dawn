#!/usr/bin/env python3
"""
Servidor simple para el Protocolo de Tiempo (RFC 868).

Este script implementa un servidor que responde al Protocolo de Tiempo
enviando la hora actual en formato de 32 bits.
"""  # noqa: D202

import socket
import struct
import time
import datetime
import argparse
import sys
import logging
import signal

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("time_server")

# El protocolo de tiempo utiliza el 1 de enero de 1900 como base
TIME_1900_EPOCH = 2208988800  # segundos desde 1970-01-01 hasta 1900-01-01

# Variable para controlar la ejecución del servidor
running = True

def signal_handler(sig, frame):
    """Manejador para señales de interrupción."""
    global running
    logger.info("Recibida señal de interrupción, deteniendo servidor...")
    running = False

def get_time_packet():
    """
    Crea un paquete de tiempo según el RFC 868.
    
    Returns:
        Bytes con el tiempo actual en formato de 32 bits
    """
    # Obtener segundos desde 1970
    current_time = int(time.time())
    
    # Convertir a segundos desde 1900
    seconds_since_1900 = current_time + TIME_1900_EPOCH
    
    # Empaquetar como entero de 32 bits (big-endian)
    return struct.pack('!I', seconds_since_1900)

def run_server(host='0.0.0.0', port=3737):
    """
    Ejecuta el servidor de tiempo.
    
    Args:
        host: Dirección en la que escuchar
        port: Puerto en el que escuchar
    """
    global running
    
    # Crear socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Permitir reutilizar la dirección/puerto
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Vincular a la dirección y puerto
        server_socket.bind((host, port))
        
        # Escuchar conexiones
        server_socket.listen(5)
        logger.info(f"Servidor de tiempo iniciado en {host}:{port}")
        
        # Establecer tiempo de espera para poder interrumpir con Ctrl+C
        server_socket.settimeout(1.0)
        
        while running:
            try:
                # Aceptar conexión
                client_socket, client_address = server_socket.accept()
                logger.info(f"Conexión aceptada desde {client_address[0]}:{client_address[1]}")
                
                try:
                    # Enviar paquete de tiempo
                    time_packet = get_time_packet()
                    client_socket.sendall(time_packet)
                    
                    # Mostrar información sobre el tiempo enviado
                    current_time = datetime.datetime.now()
                    logger.info(f"Tiempo enviado: {current_time}")
                    
                finally:
                    # Cerrar socket del cliente
                    client_socket.close()
                    
            except socket.timeout:
                # Timeout usado solo para verificar si debemos seguir ejecutando
                continue
                
    except Exception as e:
        logger.error(f"Error en el servidor: {str(e)}")
    finally:
        # Cerrar socket del servidor
        server_socket.close()
        logger.info("Servidor detenido")

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Servidor para el Protocolo de Tiempo (RFC 868)")
    parser.add_argument("--host", default="0.0.0.0", help="Dirección IP a la que vincular el servidor")
    parser.add_argument("--port", type=int, default=3737, help="Puerto en el que escuchar (por defecto: 3737)")
    
    args = parser.parse_args()
    
    # Registrar manejador de señales para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Ejecutar servidor
    run_server(args.host, args.port)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 