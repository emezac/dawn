"""
Tool Plugin Base Module for Dawn Framework.

This module defines the base class for all tool plugins in the Dawn framework.
Plugin implementation allows for modular and extensible tool management.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ToolPlugin(ABC):
    """Base class for all tool plugins in the Dawn framework."""  # noqa: D202

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """
        Get the unique name of the tool.
        
        Returns:
            str: The unique identifier for this tool
        """
        pass
    
    @property
    def tool_aliases(self) -> List[str]:
        """
        Get any aliases for this tool.
        
        Returns:
            List[str]: List of alternative names for the tool (empty by default)
        """
        return []
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Get a description of what the tool does.
        
        Returns:
            str: A human-readable description of the tool's functionality
        """
        pass
    
    @property
    def required_parameters(self) -> List[str]:
        """
        Get the list of required parameters for this tool.
        
        Returns:
            List[str]: List of parameter names that are required
        """
        return []
    
    @property
    def optional_parameters(self) -> Dict[str, Any]:
        """
        Get optional parameters and their default values.
        
        Returns:
            Dict[str, Any]: Dictionary mapping parameter names to default values
        """
        return {}
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool with the provided parameters.
        
        Args:
            **kwargs: Parameters for tool execution
            
        Returns:
            Any: The result of the tool execution
            
        Raises:
            ValueError: If required parameters are missing or invalid
            Exception: Any other exception that may occur during execution
        """
        pass
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate the parameters and set defaults for missing optional parameters.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Dict[str, Any]: Dictionary of validated parameters with defaults applied
            
        Raises:
            ValueError: If required parameters are missing or validation fails
        """
        # Validate required parameters
        for param in self.required_parameters:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: '{param}'")
        
        # Add default values for missing optional parameters
        result = {**self.optional_parameters, **kwargs}
        
        return result
    
    @property
    def version(self) -> str:
        """
        Get the version of this tool.
        
        Returns:
            str: Version string in semver format
        """
        return "1.0.0"
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing tool metadata
        """
        return {
            "name": self.tool_name,
            "aliases": self.tool_aliases,
            "description": self.description,
            "required_parameters": self.required_parameters,
            "optional_parameters": self.optional_parameters,
            "version": self.version
        } 