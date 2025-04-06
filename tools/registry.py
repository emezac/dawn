"""
Tool Registry for the AI Agent Framework.

This module provides a registry for tools that can be used by the agent
to perform specific tasks.
"""

from typing import Dict, Any, Callable, Optional
from tools.web_search_tool import WebSearchTool


class ToolRegistry:
    """
    Registry for tools that can be used by the agent.
    
    Tools are functions that can be called by the agent to perform
    specific tasks.
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools = {}  # Map of tool_name to function
        # Register the Web Search tool
        self.register_tool("web_search", self.web_search_tool_handler)
    
    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool function with the registry.
        
        Args:
            name: Name of the tool
            func: Function to call when the tool is used
        """
        if name in self.tools:
            raise ValueError(f"Tool with name '{name}' already registered")
        
        self.tools[name] = func
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Get a tool function by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            The tool function, or None if not found
        """
        return self.tools.get(name)
    
    def execute_tool(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given input data.
        
        Args:
            name: Name of the tool to execute
            data: Input data for the tool
            
        Returns:
            Dictionary containing the result of the tool execution
            
        Raises:
            ValueError: If the tool is not found
            Exception: If the tool execution fails
        """
        tool_func = self.get_tool(name)
        if not tool_func:
            return {
                "success": False,
                "error": f"Tool '{name}' not found in registry"
            }
        
        try:
            result = tool_func(data)
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

    def web_search_tool_handler(self, data: Dict[str, Any]) -> str:
        """
        Handler function for the Web Search tool.
        
        Args:
            data: Input data for the tool, should include 'query' and optional 'context_size' and 'user_location'
        
        Returns:
            The result of the web search
        """
        web_search_tool = WebSearchTool()
        query = data.get("query", "")
        context_size = data.get("context_size", "medium")
        user_location = data.get("user_location", None)
        return web_search_tool.perform_search(query, context_size, user_location)
