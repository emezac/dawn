"""
Markdown Plugin for Dawn Framework.

This plugin provides tools for working with markdown files.
"""

import os
from typing import Any, Dict, List

from core.tools.plugin import ToolPlugin


class WriteMarkdownPlugin(ToolPlugin):
    """Plugin for writing content to markdown files."""  # noqa: D202
    
    @property
    def tool_name(self) -> str:
        return "write_markdown"
    
    @property
    def tool_aliases(self) -> List[str]:
        return ["save_markdown", "create_markdown"]
    
    @property
    def description(self) -> str:
        return "Writes content to a markdown file at the specified path"
    
    @property
    def required_parameters(self) -> List[str]:
        return ["file_path"]
    
    @property
    def optional_parameters(self) -> Dict[str, Any]:
        return {"content": ""}
    
    def execute(self, **kwargs) -> str:
        """
        Execute the markdown file writing operation.
        
        Args:
            file_path: Path where the markdown file should be written
            content: The content to write to the file (default: empty string)
            
        Returns:
            The absolute path of the written file
        
        Raises:
            ValueError: If file_path is missing or invalid
            IOError: If there's an error writing to the file
        """
        # Extract parameters
        file_path = kwargs.get("file_path")
        content = kwargs.get("content", "")
        
        # Ensure file_path has .md extension
        if not file_path.lower().endswith('.md'):
            file_path += '.md'
        
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Write the content to the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Return the absolute path of the created file
            return os.path.abspath(file_path)
        
        except IOError as e:
            raise IOError(f"Error writing to markdown file {file_path}: {str(e)}")
    
    @property
    def version(self) -> str:
        return "1.0.0" 