#!/usr/bin/env python3
"""
Cliente simple para el Protocolo de Tiempo (RFC 868).

Este script se conecta a un servidor de tiempo en el puerto 37,
recibe el tiempo en formato de 32 bits y lo convierte a una fecha legible.
"""  # noqa: D202

import socket
import struct
import time
import datetime
import argparse
import sys

# El protocolo de tiempo utiliza el 1 de enero de 1900 como base
TIME_1900_EPOCH = 2208988800  # segundos desde 1970-01-01 hasta 1900-01-01

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
        print(f"Conectando a {host}:{port}...")
        client_socket.connect((host, port))
        
        # En TCP, el servidor envía los datos inmediatamente después de la conexión
        # No es necesario enviar ninguna solicitud
        
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

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Cliente para el Protocolo de Tiempo (RFC 868)")
    parser.add_argument("--host", default="localhost", help="Host del servidor de tiempo")
    parser.add_argument("--port", type=int, default=37, help="Puerto del servidor (por defecto: 37)")
    parser.add_argument("--timeout", type=int, default=5, help="Tiempo de espera en segundos")
    
    args = parser.parse_args()
    
    try:
        # Obtener la hora del servidor
        server_time = get_time_from_server(args.host, args.port, args.timeout)
        
        # Mostrar la hora recibida
        print(f"Hora recibida del servidor: {server_time}")
        print(f"Hora local del sistema:     {datetime.datetime.now()}")
        
    except ConnectionRefusedError:
        print(f"Error: Conexión rechazada. Asegúrate de que el servidor esté ejecutándose en {args.host}:{args.port}")
        return 1
    except socket.timeout:
        print(f"Error: Tiempo de espera agotado al conectar a {args.host}:{args.port}")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 