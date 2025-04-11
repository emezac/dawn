#!/usr/bin/env python3
"""
Plugin System Example for Dawn Framework.

This example demonstrates how to use the plugin system for tool execution.
It shows how to:
1. Register plugin namespaces
2. Load plugins
3. Execute tools via plugins
4. Create custom plugins
"""  # noqa: D202

import os
import sys
import tempfile
import logging
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.tools.plugin import ToolPlugin
from core.tools.registry import ToolRegistry
from core.tools.registry_access import get_registry


# Define a simple custom plugin for the example
class GreetingPlugin(ToolPlugin):
    """A simple plugin that generates greeting messages."""  # noqa: D202
    
    @property
    def tool_name(self) -> str:
        return "greeting"
    
    @property
    def tool_aliases(self) -> list:
        return ["say_hello", "greet"]
    
    @property
    def description(self) -> str:
        return "Generates personalized greeting messages"
    
    @property
    def required_parameters(self) -> list:
        return ["name"]
    
    @property
    def optional_parameters(self) -> dict:
        return {
            "language": "english",
            "formal": False
        }
    
    def execute(self, **kwargs) -> str:
        """Generate a greeting based on the provided parameters."""
        # Get parameters with validation
        params = self.validate_parameters(**kwargs)
        name = params["name"]
        language = params["language"].lower()
        formal = params["formal"]
        
        # Generate greeting based on language
        if language == "english":
            if formal:
                greeting = f"Good day, {name}."
            else:
                greeting = f"Hello, {name}!"
        elif language == "spanish":
            if formal:
                greeting = f"Buenos días, {name}."
            else:
                greeting = f"¡Hola, {name}!"
        elif language == "french":
            if formal:
                greeting = f"Bonjour, {name}."
            else:
                greeting = f"Salut, {name}!"
        else:
            greeting = f"Hello, {name}!"
        
        return greeting


def main():
    """Run the plugin system example."""
    print("Dawn Framework Plugin System Example")
    print("===================================")
    
    # Get the singleton registry
    registry = get_registry()
    
    # Register the built-in plugin namespace
    registry.register_plugin_namespace("plugins.tools")
    print("✓ Registered 'plugins.tools' namespace")
    
    # Load all plugins from registered namespaces
    registry.load_plugins()
    print("✓ Loaded plugins from registered namespaces")
    
    # Manually register our custom plugin
    custom_plugin = GreetingPlugin()
    registry.plugin_manager.plugins[custom_plugin.tool_name] = custom_plugin
    for alias in custom_plugin.tool_aliases:
        registry.plugin_manager.plugins[alias] = custom_plugin
    
    # Update the registry with our custom plugin
    registry.load_plugins(reload=True)
    print("✓ Registered custom greeting plugin")
    
    # Display all available tools
    print("\nAvailable Tools:")
    for tool_metadata in registry.get_available_tools():
        name = tool_metadata["name"]
        version = tool_metadata.get("version", "unknown")
        description = tool_metadata.get("description", "No description")
        is_legacy = tool_metadata.get("is_legacy", False)
        
        tool_type = "Legacy" if is_legacy else "Plugin"
        print(f"- {name} (v{version}, {tool_type}): {description}")
    
    # Execute the markdown plugin
    print("\nExecuting 'write_markdown' plugin:")
    try:
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp:
            temp_path = temp.name
        
        md_content = "# Plugin System Example\n\nThis file was created by a plugin!"
        result = registry.execute_tool("write_markdown", {
            "file_path": temp_path,
            "content": md_content
        })
        
        if result["success"]:
            print(f"✓ Created markdown file at: {result['result']}")
            # Read and display the file content
            with open(result["result"], "r") as f:
                print("\nFile Content:")
                print("-------------")
                print(f.read())
                print("-------------")
        else:
            print(f"✗ Failed to create markdown file: {result['error']}")
    
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
    
    # Execute our custom greeting plugin
    print("\nExecuting 'greeting' plugin:")
    
    # Try different variations of the greeting
    examples = [
        {"name": "World"},
        {"name": "Dawn", "language": "spanish"},
        {"name": "Monsieur Smith", "language": "french", "formal": True},
        {"name": "Developer", "language": "invalid"}
    ]
    
    for params in examples:
        result = registry.execute_tool("greeting", params)
        if result["success"]:
            print(f"✓ {params}: {result['result']}")
        else:
            print(f"✗ {params}: {result['error']}")
    
    # Try using an alias
    result = registry.execute_tool("say_hello", {"name": "Plugin System"})
    if result["success"]:
        print(f"✓ Using alias 'say_hello': {result['result']}")
    
    print("\nExample complete!")


if __name__ == "__main__":
    main() 