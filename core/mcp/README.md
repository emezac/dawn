# MCP Client

Este módulo proporciona un cliente para interactuar con servidores MCP (Model Control Protocol).

## Uso básico

```python
import asyncio
from core.mcp.client import MCPClient, load_config

async def main():
    # Cargar configuración desde un archivo
    config = await load_config("path/to/config.json")
    
    # Crear un cliente MCP
    client = MCPClient(
        server_url=config["servers"]["main"]["url"],
        api_key=config["servers"]["main"]["api_key"]
    )
    
    # Conectar al servidor
    await client.connect()
    
    # Listar herramientas disponibles
    tools = await client.list_tools()
    print(f"Herramientas disponibles: {tools}")
    
    # Llamar a una herramienta
    result = await client.call_tool(
        tool_name="example_tool",
        parameters={"param1": "value1"}
    )
    print(f"Resultado: {result}")
    
    # Desconectar
    await client.disconnect()

# Para usar el MCPService que maneja múltiples servidores
async def service_example():
    from core.mcp.client import MCPService
    
    config = await load_config("path/to/config.json")
    service = MCPService(config)
    
    # Conectar a todos los servidores configurados
    status = await service.connect_all()
    print(f"Estado de conexión: {status}")
    
    # Obtener un cliente para un servidor específico
    main_client = service.get_client("main")
    
    # Listar todas las herramientas en todos los servidores
    all_tools = await service.list_all_tools()
    print(f"Todas las herramientas: {all_tools}")
    
    # Desconectar de todos los servidores
    await service.disconnect_all()

if __name__ == "__main__":
    asyncio.run(main())
```

## Archivo de configuración

El archivo de configuración debe tener el siguiente formato:

```json
{
  "servers": {
    "main": {
      "url": "http://localhost:8080",
      "api_key": "your_api_key_here",
      "timeout": 30,
      "max_retries": 3,
      "retry_delay": 1.5
    },
    "development": {
      "url": "http://localhost:9000",
      "api_key": null,
      "timeout": 60,
      "max_retries": 5,
      "retry_delay": 2.0
    }
  },
  "default_server": "main",
  "log_level": "INFO",
  "max_connections": 5
}
```

Consulta `config_example.json` para un ejemplo completo.

## API

### MCPClient

- `__init__(server_url, api_key=None, timeout=30, max_retries=3, retry_delay=1.0, notification_handler=None)`: Inicializa el cliente.
- `connect()`: Establece conexión con el servidor.
- `disconnect()`: Cierra la conexión.
- `list_tools(force_refresh=False)`: Lista las herramientas disponibles.
- `call_tool(tool_name, parameters)`: Llama a una herramienta específica.

### MCPService

- `__init__(config)`: Inicializa el servicio con la configuración.
- `get_client(server_name)`: Obtiene un cliente para un servidor específico.
- `connect_all()`: Conecta a todos los servidores configurados.
- `disconnect_all()`: Desconecta de todos los servidores.
- `list_all_tools()`: Lista las herramientas disponibles en todos los servidores. 