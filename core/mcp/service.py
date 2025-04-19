import json
import logging
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Callable, Tuple
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .client import MCPError, ToolExecutionError

logger = logging.getLogger("mcp.service")

# Modelos de datos
class ToolParameter(BaseModel):
    name: str
    description: str = ""
    required: bool = False
    type: str = "string"
    default: Optional[Any] = None
    
class Tool(BaseModel):
    name: str
    description: str = ""
    parameters: List[ToolParameter] = []
    version: str = "1.0.0"
    tags: List[str] = []
    
class ToolRequest(BaseModel):
    tool: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
class ToolResponse(BaseModel):
    result: Any
    status: str = "success"
    message: Optional[str] = None
    
class ServerConfig(BaseModel):
    name: str
    url: str
    api_key: Optional[str] = None
    tools: List[Tool] = []
    
class MCPServiceConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    api_key: Optional[str] = None
    cors_origins: List[str] = ["*"]
    log_level: str = "INFO"
    tools: Dict[str, Tool] = Field(default_factory=dict)
    external_servers: Dict[str, ServerConfig] = Field(default_factory=dict)

class MCPService:
    """
    Servicio que expone herramientas MCP a través de una API HTTP.
    """  # noqa: D202
    
    def __init__(self, config: MCPServiceConfig):
        """
        Inicializa el servicio MCP.
        
        Args:
            config: Configuración del servicio
        """
        self.config = config
        self.app = FastAPI(title="MCP Service", description="Model Control Protocol Service")
        self.api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
        self.server_sessions: Dict[str, aiohttp.ClientSession] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Configurar nivel de log
        logging.getLogger("mcp").setLevel(getattr(logging, config.log_level))
        
        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Registrar rutas
        self._register_routes()
    
    def _register_routes(self) -> None:
        """
        Registra las rutas de la API.
        """
        @self.app.get("/health")
        async def health_check():
            """Verifica el estado del servicio."""
            return {"status": "ok"}
        
        @self.app.get("/tools")
        async def list_tools(api_key: str = Depends(self._verify_api_key)):
            """Lista todas las herramientas disponibles."""
            all_tools = []
            
            # Herramientas locales
            for tool in self.config.tools.values():
                all_tools.append(tool.dict())
            
            # Herramientas de servidores externos
            for server_name, server in self.config.external_servers.items():
                try:
                    tools = await self._get_server_tools(server_name)
                    for tool in tools:
                        # Agregamos el prefijo del servidor al nombre de la herramienta
                        tool["name"] = f"{server_name}:{tool['name']}"
                        all_tools.append(tool)
                except Exception as e:
                    logger.error(f"Error al obtener herramientas del servidor {server_name}: {str(e)}")
            
            return all_tools
        
        @self.app.post("/execute")
        async def execute_tool(
            request: ToolRequest, 
            background_tasks: BackgroundTasks,
            api_key: str = Depends(self._verify_api_key)
        ):
            """Ejecuta una herramienta."""
            tool_name = request.tool
            parameters = request.parameters
            
            # Verificar si es una herramienta de un servidor externo
            if ":" in tool_name:
                server_name, remote_tool_name = tool_name.split(":", 1)
                if server_name in self.config.external_servers:
                    return await self._execute_remote_tool(server_name, remote_tool_name, parameters)
            
            # Ejecutar herramienta local
            if tool_name in self.config.tools:
                try:
                    tool = self.config.tools[tool_name]
                    # Aquí implementarías la lógica para ejecutar la herramienta local
                    # En este ejemplo, simplemente devolvemos un mensaje
                    return {
                        "status": "success", 
                        "result": f"Herramienta {tool_name} ejecutada con parámetros: {parameters}"
                    }
                except Exception as e:
                    logger.error(f"Error al ejecutar herramienta {tool_name}: {str(e)}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Error al ejecutar herramienta: {str(e)}"
                    )
            
            raise HTTPException(status_code=404, detail=f"Herramienta no encontrada: {tool_name}")
        
        @self.app.post("/register/tool")
        async def register_tool(
            tool: Tool, 
            api_key: str = Depends(self._verify_api_key)
        ):
            """Registra una nueva herramienta local."""
            self.config.tools[tool.name] = tool
            return {"status": "success", "message": f"Herramienta {tool.name} registrada correctamente"}
        
        @self.app.delete("/tools/{tool_name}")
        async def unregister_tool(
            tool_name: str, 
            api_key: str = Depends(self._verify_api_key)
        ):
            """Elimina una herramienta local."""
            if tool_name in self.config.tools:
                del self.config.tools[tool_name]
                return {"status": "success", "message": f"Herramienta {tool_name} eliminada correctamente"}
            
            raise HTTPException(status_code=404, detail=f"Herramienta no encontrada: {tool_name}")
    
    async def _verify_api_key(self, authorization: Optional[str] = None) -> str:
        """
        Verifica la clave API.
        
        Args:
            authorization: Encabezado de autorización
            
        Returns:
            Clave API si es válida
            
        Raises:
            HTTPException: Si la clave API no es válida
        """
        if not self.config.api_key:
            return ""
            
        if not authorization:
            raise HTTPException(
                status_code=401, 
                detail="API key required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401, 
                detail="Invalid authorization format. Use Bearer {api_key}",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        api_key = authorization.replace("Bearer ", "")
        
        if api_key != self.config.api_key:
            raise HTTPException(
                status_code=401, 
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return api_key
    
    async def _get_server_session(self, server_name: str) -> aiohttp.ClientSession:
        """
        Obtiene o crea una sesión para un servidor externo.
        
        Args:
            server_name: Nombre del servidor
            
        Returns:
            Sesión HTTP para el servidor
            
        Raises:
            HTTPException: Si el servidor no existe
        """
        if server_name not in self.config.external_servers:
            raise HTTPException(status_code=404, detail=f"Servidor no encontrado: {server_name}")
            
        if server_name in self.server_sessions:
            return self.server_sessions[server_name]
            
        server = self.config.external_servers[server_name]
        headers = {}
        
        if server.api_key:
            headers["Authorization"] = f"Bearer {server.api_key}"
            
        session = aiohttp.ClientSession(headers=headers)
        self.server_sessions[server_name] = session
        
        return session
        
    async def _get_server_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Obtiene las herramientas disponibles en un servidor externo.
        
        Args:
            server_name: Nombre del servidor
            
        Returns:
            Lista de herramientas
            
        Raises:
            HTTPException: Si hay un error al obtener las herramientas
        """
        server = self.config.external_servers[server_name]
        session = await self._get_server_session(server_name)
        
        try:
            async with session.get(f"{server.url}/tools") as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Error al obtener herramientas: {error_text}"
                    )
                    
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión con el servidor {server_name}: {str(e)}"
            )
    
    async def _execute_remote_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta una herramienta en un servidor externo.
        
        Args:
            server_name: Nombre del servidor
            tool_name: Nombre de la herramienta
            parameters: Parámetros para la herramienta
            
        Returns:
            Resultado de la ejecución
            
        Raises:
            HTTPException: Si hay un error al ejecutar la herramienta
        """
        server = self.config.external_servers[server_name]
        session = await self._get_server_session(server_name)
        
        payload = {
            "tool": tool_name,
            "parameters": parameters
        }
        
        try:
            async with session.post(f"{server.url}/execute", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Error al ejecutar herramienta: {error_text}"
                    )
                    
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión con el servidor {server_name}: {str(e)}"
            )
    
    async def start(self) -> None:
        """
        Inicia el servicio MCP.
        """
        logger.info(f"Iniciando servicio MCP en {self.config.host}:{self.config.port}")
        import uvicorn
        
        config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level.lower()
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self) -> None:
        """
        Detiene el servicio MCP.
        """
        logger.info("Deteniendo servicio MCP")
        
        # Cerrar todas las sesiones de servidores externos
        for server_name, session in self.server_sessions.items():
            try:
                await session.close()
            except Exception as e:
                logger.error(f"Error al cerrar sesión del servidor {server_name}: {str(e)}")
        
        self.server_sessions.clear()
        
        # Cancelar todas las tareas en ejecución
        for task_id, task in self.running_tasks.items():
            if not task.done():
                try:
                    task.cancel()
                    await task
                except asyncio.CancelledError:
                    logger.debug(f"Tarea {task_id} cancelada")
                except Exception as e:
                    logger.error(f"Error al cancelar tarea {task_id}: {str(e)}")
        
        self.running_tasks.clear()


async def load_config(config_path: str) -> MCPServiceConfig:
    """
    Carga la configuración del servicio desde un archivo JSON.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Configuración del servicio
        
    Raises:
        ValueError: Si el archivo de configuración no es válido
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            
        # Convertir configuraciones de servidores externos
        external_servers = {}
        for name, server_data in config_data.get("external_servers", {}).items():
            if isinstance(server_data, dict):
                server_data["name"] = name
                external_servers[name] = ServerConfig(**server_data)
        
        config_data["external_servers"] = external_servers
        
        # Convertir herramientas locales
        tools = {}
        for tool_data in config_data.get("tools", []):
            if isinstance(tool_data, dict) and "name" in tool_data:
                tools[tool_data["name"]] = Tool(**tool_data)
        
        config_data["tools"] = tools
        
        return MCPServiceConfig(**config_data)
    
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Error al cargar configuración: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error al procesar configuración: {str(e)}") 