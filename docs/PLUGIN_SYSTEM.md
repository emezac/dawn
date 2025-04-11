# Plugin System for Tool Execution

The Dawn framework includes a plugin system for extending its functionality with new tools. This document explains how to use and develop plugins for the Dawn framework.

## Table of Contents

- [Overview](#overview)
- [Using Plugins](#using-plugins)
- [Creating Plugins](#creating-plugins)
- [Plugin Manager](#plugin-manager)
- [Tool Registry Integration](#tool-registry-integration)
- [Best Practices](#best-practices)

## Overview

The plugin system allows for a modular and extensible approach to adding new tools to the Dawn framework. The system consists of:

1. **Base Plugin Class**: A base class that all plugins must inherit from
2. **Plugin Manager**: Responsible for discovering, loading, and managing plugins
3. **Tool Registry Integration**: Integration with the existing tool registry

Key features of the plugin system:

- Automatic discovery and loading of plugins from registered namespaces
- Declarative parameter validation
- Tool aliasing
- Metadata for tools
- Backward compatibility with existing tools

## Using Plugins

### Registering Plugin Namespaces

To use plugins, first register the namespaces where your plugins are located:

```python
from core.tools.registry import ToolRegistry

registry = ToolRegistry()
registry.register_plugin_namespace("plugins.tools")  # Built-in plugins
registry.register_plugin_namespace("my_plugins")     # Your custom plugins
```

### Loading Plugins

After registering namespaces, load all the plugins:

```python
registry.load_plugins()
```

To reload plugins (useful during development):

```python
registry.load_plugins(reload=True)
```

### Executing Plugin Tools

Plugins are automatically registered as tools in the registry, so you can execute them like any other tool:

```python
result = registry.execute_tool("plugin_tool_name", {
    "param1": "value1",
    "param2": "value2"
})

if result["success"]:
    print(f"Result: {result['result']}")
else:
    print(f"Error: {result['error']}")
```

### Listing Available Tools

You can get metadata about all available tools, including plugins:

```python
tools = registry.get_available_tools()
for tool in tools:
    print(f"{tool['name']} (v{tool['version']}): {tool['description']}")
```

## Creating Plugins

### Basic Plugin Structure

To create a plugin, create a new Python module and define a class that inherits from `ToolPlugin`:

```python
from core.tools.plugin import ToolPlugin

class MyPlugin(ToolPlugin):
    @property
    def tool_name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "Description of what my tool does"
    
    @property
    def required_parameters(self) -> list:
        return ["required_param"]
    
    @property
    def optional_parameters(self) -> dict:
        return {"optional_param": "default_value"}
    
    def execute(self, **kwargs) -> any:
        # Validate parameters
        params = self.validate_parameters(**kwargs)
        
        # Use parameters
        required_param = params["required_param"]
        optional_param = params["optional_param"]
        
        # Do some work...
        result = f"Processed {required_param} with {optional_param}"
        
        return result
```

### Required Methods and Properties

Every plugin must implement:

- `tool_name`: The unique name of the tool
- `description`: A human-readable description
- `execute(**kwargs)`: The main execution method

Optional properties to implement:

- `tool_aliases`: List of alternative names for the tool
- `required_parameters`: List of parameter names that are required
- `optional_parameters`: Dictionary of parameter names and default values
- `version`: Version string in semver format

### Parameter Validation

The base class provides a `validate_parameters` method that checks for required parameters and applies defaults for optional parameters. Use it in your `execute` method:

```python
def execute(self, **kwargs) -> any:
    params = self.validate_parameters(**kwargs)
    # Now use params safely...
```

## Plugin Manager

The `PluginManager` class handles:

1. Discovering plugins in Python packages
2. Loading plugin instances
3. Managing plugin lifecycle

The `PluginManager` is already integrated with the `ToolRegistry`, so you typically won't need to use it directly.

## Tool Registry Integration

Plugins are automatically registered as tools in the `ToolRegistry`. This means:

1. Plugin tools can be executed just like traditional tools
2. Tools from plugins and traditional tools can coexist
3. Plugins are executed with the same error handling as traditional tools

## Best Practices

### Organization

- Group related plugins in their own modules
- Use meaningful names for your plugin classes
- Follow the established naming convention for tools

### Documentation

- Provide detailed docstrings for your plugin and its methods
- Document each parameter, including type and usage
- Include examples in your documentation

### Error Handling

- Validate parameters thoroughly
- Raise specific exceptions with clear error messages
- Handle exceptions gracefully and provide helpful error information

### Testing

- Write unit tests for your plugins
- Test with various parameter combinations
- Test error cases and edge cases

### Versioning

- Use semantic versioning for your plugins
- Update the version when you make changes
- Document breaking changes

## Example

See `examples/plugin_system_example.py` for a complete working example of using and creating plugins. 