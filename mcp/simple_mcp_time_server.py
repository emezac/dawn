#!/usr/bin/env python3
"""
Servidor web simple que implementa la API MCP para el Protocolo de Tiempo.

Este servidor recibe solicitudes HTTP y devuelve la hora obtenida del
servidor de tiempo que implementa el Protocolo de Tiempo (RFC 868).
"""  # noqa: D202

import argparse
import datetime
import json
import logging
import socket
import struct
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_mcp_time_server")

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

class MCPRequestHandler(BaseHTTPRequestHandler):
    """Manejador de solicitudes HTTP para la API MCP."""  # noqa: D202
    
    def __init__(self, *args, time_host="localhost", time_port=3737, api_key=None, **kwargs):
        self.time_host = time_host
        self.time_port = time_port
        self.api_key = api_key
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Manejar solicitudes GET."""
        # Parsear la URL
        parsed_url = urlparse(self.path)
        
        # Verificar la ruta
        if parsed_url.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            response = {
                "status": "ok",
                "server": "MCP Time Server",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed_url.path == "/tools":
            # Verificar API key si está configurada
            if not self._verify_api_key():
                return
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # Definir herramientas disponibles
            tools = [
                {
                    "name": "get_time",
                    "description": "Obtiene la hora actual del servidor de tiempo",
                    "parameters": [
                        {
                            "name": "host",
                            "description": "Host del servidor de tiempo",
                            "type": "string",
                            "required": False,
                            "default": self.time_host
                        },
                        {
                            "name": "port",
                            "description": "Puerto del servidor de tiempo",
                            "type": "integer",
                            "required": False,
                            "default": self.time_port
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
            
            self.wfile.write(json.dumps(tools).encode())
            
        else:
            # Ruta no reconocida
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            response = {
                "status": "error",
                "error": "Ruta no encontrada"
            }
            
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Manejar solicitudes POST."""
        # Parsear la URL
        parsed_url = urlparse(self.path)
        
        # Verificar la ruta
        if parsed_url.path == "/execute":
            # Verificar API key si está configurada
            if not self._verify_api_key():
                return
            
            # Leer el cuerpo de la solicitud
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode()
            
            try:
                request_data = json.loads(post_data)
                tool_name = request_data.get("tool")
                parameters = request_data.get("parameters", {})
                
                # Verificar herramienta solicitada
                if tool_name == "get_time":
                    # Extraer parámetros
                    host = parameters.get("host", self.time_host)
                    port = int(parameters.get("port", self.time_port))
                    timeout = int(parameters.get("timeout", 5))
                    
                    try:
                        # Obtener la hora del servidor
                        time_obj = get_time_from_server(host, port, timeout)
                        
                        # Formatear la respuesta
                        result = {
                            "status": "success",
                            "result": {
                                "time": time_obj.isoformat(),
                                "timestamp": time_obj.timestamp(),
                                "local_time": datetime.datetime.now().isoformat()
                            }
                        }
                        
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
                        
                        logger.info(f"Tiempo enviado: {time_obj.isoformat()}")
                        
                    except Exception as e:
                        logger.error(f"Error al obtener la hora: {str(e)}")
                        
                        self.send_response(500)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        
                        error_response = {
                            "status": "error",
                            "error": str(e)
                        }
                        
                        self.wfile.write(json.dumps(error_response).encode())
                        
                else:
                    # Herramienta no reconocida
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    
                    response = {
                        "status": "error",
                        "error": f"Herramienta no encontrada: {tool_name}"
                    }
                    
                    self.wfile.write(json.dumps(response).encode())
                    
            except json.JSONDecodeError:
                # Error al decodificar JSON
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                response = {
                    "status": "error",
                    "error": "Invalid JSON in request body"
                }
                
                self.wfile.write(json.dumps(response).encode())
                
        else:
            # Ruta no reconocida
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            response = {
                "status": "error",
                "error": "Ruta no encontrada"
            }
            
            self.wfile.write(json.dumps(response).encode())
    
    def _verify_api_key(self):
        """
        Verifica la API key en el encabezado Authorization.
        
        Returns:
            True si la API key es válida o no se requiere, False en caso contrario
        """
        if not self.api_key:
            return True
            
        auth_header = self.headers.get("Authorization")
        
        if not auth_header:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.send_header("WWW-Authenticate", "Bearer")
            self.end_headers()
            
            response = {
                "status": "error",
                "error": "API key required"
            }
            
            self.wfile.write(json.dumps(response).encode())
            return False
            
        if not auth_header.startswith("Bearer "):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.send_header("WWW-Authenticate", "Bearer")
            self.end_headers()
            
            response = {
                "status": "error",
                "error": "Invalid authorization format. Use Bearer {api_key}"
            }
            
            self.wfile.write(json.dumps(response).encode())
            return False
            
        api_key = auth_header.replace("Bearer ", "")
        
        if api_key != self.api_key:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.send_header("WWW-Authenticate", "Bearer")
            self.end_headers()
            
            response = {
                "status": "error",
                "error": "Invalid API key"
            }
            
            self.wfile.write(json.dumps(response).encode())
            return False
            
        return True
        
def run_server(host="0.0.0.0", port=8080, time_host="localhost", time_port=3737, api_key=None):
    """
    Ejecuta el servidor HTTP.
    
    Args:
        host: Dirección IP del servidor HTTP
        port: Puerto del servidor HTTP
        time_host: Host del servidor de tiempo
        time_port: Puerto del servidor de tiempo
        api_key: Clave API para autenticación (opcional)
    """
    # Crear una clase de manejador con los parámetros configurados
    handler = lambda *args, **kwargs: MCPRequestHandler(*args, time_host=time_host, time_port=time_port, api_key=api_key, **kwargs)
    
    # Crear y configurar el servidor
    server = HTTPServer((host, port), handler)
    
    logger.info(f"Servidor MCP iniciado en {host}:{port}")
    logger.info(f"Configurado para usar servidor de tiempo en {time_host}:{time_port}")
    
    try:
        # Iniciar el servidor
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    finally:
        # Cerrar el servidor
        server.server_close()
        logger.info("Servidor detenido")

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Servidor MCP simple para el Protocolo de Tiempo")
    parser.add_argument("--host", default="0.0.0.0", help="Dirección IP del servidor HTTP")
    parser.add_argument("--port", type=int, default=8080, help="Puerto del servidor HTTP")
    parser.add_argument("--time-host", default="localhost", help="Host del servidor de tiempo")
    parser.add_argument("--time-port", type=int, default=3737, help="Puerto del servidor de tiempo")
    parser.add_argument("--api-key", default="dawn-mcp-demo-key", help="Clave API para autenticación")
    
    args = parser.parse_args()
    
    # Ejecutar el servidor
    run_server(args.host, args.port, args.time_host, args.time_port, args.api_key)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 