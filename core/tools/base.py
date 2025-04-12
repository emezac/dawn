"""
Base tool module for Dawn platform.

This module defines the BaseTool class, which serves as the foundation
for all tools in the Dawn platform.
"""

from typing import Dict, Any, Optional, List, Callable


class BaseTool:
    """
    Base class for all tools in the Dawn platform.
    
    A tool is a function that performs a specific operation and returns a result.
    Tools can interact with external APIs, process data, or perform other operations.
    """  # noqa: D202
    
    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameter_schema: Optional[Dict[str, Any]] = None,
        required_params: Optional[List[str]] = None
    ):
        """
        Initialize a new BaseTool.
        
        Args:
            name: Name of the tool
            description: Description of what the tool does
            handler: Function that implements the tool's behavior
            parameter_schema: Optional JSON schema describing the tool's parameters
            required_params: List of required parameter names
        """
        self.name = name
        self.description = description
        self.handler = handler
        self.parameter_schema = parameter_schema or {}
        self.required_params = required_params or []
        
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the provided parameters.
        
        Args:
            **kwargs: Parameters to pass to the tool handler
            
        Returns:
            Dictionary containing the tool execution result
        """
        # Validate required parameters
        for param in self.required_params:
            if param not in kwargs:
                return {
                    "success": False,
                    "error": f"Missing required parameter: {param}",
                    "error_type": "MissingParameter",
                    "status": "error"
                }
        
        try:
            # Execute the handler
            result = self.handler(**kwargs)
            
            # If the handler didn't return a dict, wrap it in a success response
            if not isinstance(result, dict):
                return {
                    "success": True,
                    "result": result,
                    "status": "success"
                }
            
            # If the handler returned a dict but it doesn't have the expected keys,
            # add them with default values
            if "success" not in result:
                result["success"] = True
            if "status" not in result:
                result["status"] = "success" if result["success"] else "error"
            
            return result
            
        except Exception as e:
            # Handle exceptions
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "status": "error"
            }
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool to a dictionary representation.
        
        Returns:
            Dictionary representing the tool
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameter_schema": self.parameter_schema,
            "required_params": self.required_params
        }
        
    def __str__(self) -> str:
        """Return a string representation of the tool."""
        return f"BaseTool({self.name})" 