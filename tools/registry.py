"""
Tool Registry for the AI Agent Framework.

This module provides a registry for tools that can be used by the agent
to perform specific tasks.
"""

from typing import Dict, Any, Callable, Optional
from tools.web_search_tool import WebSearchTool
from tools.file_read_tool import FileReadTool
from tools.file_upload_tool import FileUploadTool
from tools.vector_store_tool import VectorStoreTool
from tools.write_markdown_tool import WriteMarkdownTool

class ToolRegistry:
    """
    Registry for tools that can be used by the agent.
    
    Tools are functions that can be called by the agent to perform
    specific tasks.
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools = {}  # Map of tool_name to function
        # Register tools
        self.register_tool("web_search", self.web_search_tool_handler)
        self.register_tool("file_read", self.file_read_tool_handler)
        self.register_tool("file_upload", self.file_upload_tool_handler)
        self.register_tool("vector_store_create", self.vector_store_create_tool_handler)
        self.register_tool("write_markdown", self.write_markdown_tool_handler)
    
    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool function with the registry.
        
        Args:
            name: Name of the tool.
            func: Function to call when the tool is used.
        """
        if name in self.tools:
            raise ValueError(f"Tool with name '{name}' already registered")
        self.tools[name] = func
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Get a tool function by name.
        
        Args:
            name: Name of the tool to retrieve.
            
        Returns:
            The tool function, or None if not found.
        """
        return self.tools.get(name)
    
    def execute_tool(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given input data.
        
        Args:
            name: Name of the tool to execute.
            data: Input data for the tool.
            
        Returns:
            Dictionary containing the result of the tool execution.
        """
        tool_func = self.get_tool(name)
        if not tool_func:
            return {
                "success": False,
                "error": f"Tool '{name}' not found in registry"
            }
        try:
            # Unpack the dictionary as keyword arguments
            result = tool_func(**data)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def web_search_tool_handler(self, **data) -> str:
        """
        Handler function for the Web Search tool.
        
        Expects:
          query, context_size (optional), user_location (optional)
        """
        web_search_tool = WebSearchTool()
        query = data.get("query", "")
        context_size = data.get("context_size", "medium")
        user_location = data.get("user_location", None)
        return web_search_tool.perform_search(query, context_size, user_location)

    def file_read_tool_handler(self, **data) -> str:
        """
        Handler function for the File Read tool.
        
        Expects:
          vector_store_ids, query, max_num_results (optional), include_search_results (optional)
        """
        file_read_tool = FileReadTool()
        vector_store_ids = data.get("vector_store_ids", [])
        query = data.get("query", "")
        max_num_results = data.get("max_num_results", 5)
        include_search_results = data.get("include_search_results", False)
        return file_read_tool.perform_file_read(vector_store_ids, query, max_num_results, include_search_results)

    def file_upload_tool_handler(self, **data) -> str:
        """
        Handler function for the File Upload tool.
        
        Expects:
          file_path, purpose (optional)
        """
        file_upload_tool = FileUploadTool()
        file_path = data.get("file_path", "")
        purpose = data.get("purpose", "assistants")
        return file_upload_tool.upload_file(file_path, purpose)
    
    def vector_store_create_tool_handler(self, **data) -> str:
        """
        Handler function for the Vector Store Create tool.
        
        Expects:
          name, file_ids (list)
        """
        vector_store_tool = VectorStoreTool()
        name = data.get("name", "Default Vector Store")
        file_ids = data.get("file_ids", [])
        return vector_store_tool.create_vector_store(name, file_ids)
    
    def write_markdown_tool_handler(self, **data) -> str:
        """
        Handler function for the Write Markdown File tool.
        
        Expects:
          file_path, content
        """
        write_tool = WriteMarkdownTool()
        file_path = data.get("file_path", "")
        content = data.get("content", "")
        return write_tool.write_markdown_file(file_path, content)
