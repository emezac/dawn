"""
Tool Registry for the AI Agent Framework.

This module provides a registry for tools that can be used by the agent
to perform specific tasks.
"""

from typing import Dict, Any, Callable, Optional


class ToolRegistry:
    """
    Registry for tools that can be used by the agent.
    
    Tools are functions that can be called by the agent to perform
    specific tasks.
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools = {}  # Map of tool_name to function
    
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
