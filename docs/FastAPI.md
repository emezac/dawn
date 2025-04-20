How to Use FastAPI MCP Server: A Comprehensive Guide

In today’s world of AI development, seamless integration between applications and AI models is crucial. The Model Context Protocol (MCP) bridges this gap by allowing AI models to access external tools and data sources. FastAPI MCP is a powerful tool that converts your existing FastAPI endpoints into MCP-compatible tools with minimal configuration. This article will guide you through setting up and using FastAPI MCP to enhance your AI applications.

Introduction to FastAPI MCP
FastAPI MCP is a zero-configuration tool that automatically exposes your FastAPI endpoints as Model Context Protocol (MCP) tools. The beauty of FastAPI MCP lies in its simplicity — it takes your existing API endpoints and makes them accessible to AI models without requiring you to rewrite your code or create separate implementations.

With FastAPI MCP, you can:

Automatically convert FastAPI endpoints to MCP tools
Preserve your API schemas and documentation
Deploy your MCP server alongside your API or as a separate service
Customize which endpoints are exposed as tools
Control how tool descriptions are generated
GitHub — tadata-org/fastapi_mcp: A zero-configuration tool for automatically exposing FastAPI…
A zero-configuration tool for automatically exposing FastAPI endpoints as Model Context Protocol (MCP) tools. …
github.com

Pro Tip: Boost your AI development workflow by integrating the Apidog MCP Server into your IDE. This gives your AI assistant real-time access to API specifications, enabling it to generate code, refine documentation, and streamline data model creation — all while ensuring alignment with your API design. 🚀

Apidog MCP Server: The Bridge Between Your API Specifications and AI Coding Assistants
Software development is undergoing a profound transformation as artificial intelligence becomes increasingly integrated…
sebastian-petrus.medium.com

apidog-mcp-server
The **Apidog MCP Server** allows you to use your API documentation from Apidog projects as a data source for AI-powered…
www.npmjs.com

Getting Started with FastAPI MCP
Installation
Before diving into usage, you’ll need to install the FastAPI MCP package. You have two options:

Using uv (recommended for faster installation):

uv add fastapi-mcp
Using pip:

pip install fastapi-mcp
Basic Implementation
The simplest way to implement FastAPI MCP is to mount it directly to your existing FastAPI application. Here’s a minimal example:

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
# Your existing FastAPI app
app = FastAPI()
# Define your API endpoints
@app.get("/users/{user_id}", operation_id="get_user_info")
async def read_user(user_id: int):
    return {"user_id": user_id}
# Add MCP server to your FastAPI app
mcp = FastApiMCP(
    app,
    name="My API MCP",
    description="MCP server for my API",
    base_url="<http://localhost:8000>"
)
# Mount the MCP server to your app
mcp.mount()
# Run your app as usual
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
With just these few lines of code, your FastAPI application is now equipped with an MCP server accessible at http://localhost:8000/mcp. AI models that support MCP, such as Claude, can now discover and interact with your API endpoints as tools.

Best Practices for Tool Naming
When AI models interact with your tools, clear naming is essential. FastAPI MCP uses the operation_id from your FastAPI routes as the MCP tool names. If you don't specify an operation_id, FastAPI generates one automatically, which might be cryptic and less user-friendly.

Consider these two endpoint definitions:

# Auto-generated operation_id (e.g., "read_user_users__user_id__get")
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}
# Explicit operation_id (tool will be named "get_user_info")
@app.get("/users/{user_id}", operation_id="get_user_info")
async def read_user(user_id: int):
    return {"user_id": user_id}
The second approach creates a more intuitive tool name that AI models will find easier to use correctly. Always provide explicit operation_id values for clearer tool names.

Advanced Configuration Options
Customizing Schema Description
FastAPI MCP offers options to control how your API schemas are described to AI models:

mcp = FastApiMCP(
    app,
    name="My API MCP",
    base_url="<http://localhost:8000>",
    describe_all_responses=True,  # Include all possible response schemas
    describe_full_response_schema=True  # Include full JSON schemas in descriptions
)
The describe_all_responses option includes all possible response schemas in the tool descriptions, while describe_full_response_schema includes the complete JSON schema rather than a simplified version.

Filtering Endpoints
You may not want all your API endpoints exposed as MCP tools. FastAPI MCP provides several ways to filter which endpoints become tools:

# Only include specific operations
mcp = FastApiMCP(
    app,
    include_operations=["get_user", "create_user"]
)
# Exclude specific operations
mcp = FastApiMCP(
    app,
    exclude_operations=["delete_user"]
)
# Only include operations with specific tags
mcp = FastApiMCP(
    app,
    include_tags=["users", "public"]
)
# Exclude operations with specific tags
mcp = FastApiMCP(
    app,
    exclude_tags=["admin", "internal"]
)
# Combine operation IDs and tags
mcp = FastApiMCP(
    app,
    include_operations=["user_login"],
    include_tags=["public"]
)
These filtering capabilities give you fine-grained control over which endpoints are exposed as tools, allowing you to maintain security while providing the necessary functionality to AI models.

Deployment Options
Separate Deployment
While mounting the MCP server to your existing FastAPI app is simple, you might want to deploy it separately for security or architectural reasons. Here’s how to set it up:

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
# Your API app
api_app = FastAPI()
# Define your API endpoints on api_app
@api_app.get("/users/{user_id}", operation_id="get_user_info")
async def read_user(user_id: int):
    return {"user_id": user_id}
# A separate app for the MCP server
mcp_app = FastAPI()
# Create MCP server from the API app
mcp = FastApiMCP(
    api_app,
    base_url="<http://api-host:8001>"  # The URL where the API app will be running
)
# Mount the MCP server to the separate app
mcp.mount(mcp_app)
# Now you can run both apps separately:
# uvicorn main:api_app --host api-host --port 8001
# uvicorn main:mcp_app --host mcp-host --port 8000
This approach allows you to run your API and MCP servers on different hosts or ports, providing flexibility in your architecture.

Updating Tools After Creation
If you add new endpoints to your FastAPI app after creating the MCP server, you’ll need to refresh the server to include them:

# Create MCP server
mcp = FastApiMCP(app)
mcp.mount()
# Add new endpoints after MCP server creation
@app.get("/new/endpoint/", operation_id="new_endpoint")
async def new_endpoint():
    return {"message": "Hello, world!"}
# Refresh the MCP server to include the new endpoint
mcp.setup_server()
# Add new endpoints after MCP server creation
@app.get("/new/endpoint/", operation_id="new_endpoint")
async def new_endpoint():
    return {"message": "Hello, world!"}
# Refresh the MCP server to include the new endpoint
mcp.setup_server()
The setup_server() method updates the MCP server with any new endpoints, ensuring your tools stay in sync with your API.

Connecting AI Models to Your MCP Server
Once your FastAPI app with MCP integration is running, you can connect AI models to it in various ways:

Using Server-Sent Events (SSE)
Many MCP clients, such as Cursor, support Server-Sent Events (SSE) for real-time communication:

Run your application with FastAPI MCP enabled
In Cursor, go to Settings > MCP
Use your MCP server’s endpoint (e.g., http://localhost:8000/mcp) as the SSE URL
Cursor will automatically discover all available tools and resources
Using MCP-Proxy for Other Clients
For clients that don’t support SSE directly, such as Claude Desktop, you can use mcp-proxy:

Install mcp-proxy: uv tool install mcp-proxy
Add the proxy configuration to Claude Desktop’s MCP config file
For Windows:

{
  "mcpServers": {
    "my-api-mcp-proxy": {
      "command": "mcp-proxy",
      "args": ["<http://127.0.0.1:8000/mcp>"]
    }
  }
}
For macOS:

{
  "mcpServers": {
    "my-api-mcp-proxy": {
      "command": "/Full/Path/To/Your/Executable/mcp-proxy",
      "args": ["<http://127.0.0.1:8000/mcp>"]
    }
  }
}
Real-World Applications and Benefits
FastAPI MCP opens up a world of possibilities for integrating your APIs with AI models:

