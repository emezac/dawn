# Tool Registry Access Guide

This guide explains the standardized approach to accessing the Tool Registry throughout the Dawn framework.

## Background

Previously, registry access was inconsistent across the codebase:
- Some code directly instantiated new `ToolRegistry` instances
- Others relied on globals or instance variables
- Tool existence checks were inconsistent
- Error handling varied across implementations

The new registry_access module provides a standardized, singleton approach to registry access.

## Best Practices

### 1. Importing the Module

Always import the specific functions you need from the registry_access module:

```python
from core.tools.registry_access import (
    get_registry,  # Only if you need direct registry access
    register_tool, 
    execute_tool,
    tool_exists, 
    get_available_tools
)
```

### 2. Checking if a Tool Exists

**Old way:**
```python
registry = ToolRegistry()
if "tool_name" in registry.tools:
    # Tool exists
```

or 

```python
registry = ToolRegistry()
if "tool_name" in list(registry.tools.keys()):
    # Tool exists
```

**New way:**
```python
if tool_exists("tool_name"):
    # Tool exists
```

### 3. Registering Tools

**Old way:**
```python
registry = ToolRegistry()
try:
    registry.register_tool("tool_name", handler_func)
except ValueError:
    # Tool already exists
```

**New way:**
```python
# Simple version - returns boolean success indicator
success = register_tool("tool_name", handler_func)

# With replacement of existing tool if needed
success = register_tool("tool_name", handler_func, replace=True)
```

### 4. Executing Tools

**Old way:**
```python
registry = ToolRegistry()
result = registry.execute_tool("tool_name", input_data)
```

**New way:**
```python
result = execute_tool("tool_name", input_data)
```

### 5. Getting Available Tools

**Old way:**
```python
registry = ToolRegistry()
tools = list(registry.tools.keys())
```

**New way:**
```python
tools = get_available_tools()
```

### 6. Loading Plugins

**Old way:**
```python
registry = ToolRegistry()
registry.load_plugins(reload=True)
```

**New way:**
```python
load_plugins(reload=True)
```

## Benefits of the New Approach

1. **Consistency**: All code accesses the same registry instance
2. **Error Handling**: Standardized error handling across the codebase
3. **Simplified API**: Common operations available directly as functions
4. **Testing**: Easier to reset the registry for isolated tests
5. **Performance**: Avoids multiple registry instances
6. **Maintainability**: Central place to modify registry behavior

## Example: Workflow Integration

```python
from core.tools.registry_access import register_tool, execute_tool, tool_exists

# Register custom handlers if needed
if not tool_exists("custom_tool"):
    register_tool("custom_tool", custom_handler)

# Execute tool with proper error handling
result = execute_tool("custom_tool", input_data)
if result["success"]:
    # Handle success
    processed_data = result["result"]
else:
    # Handle error
    error_message = result.get("error", "Unknown error")
```

## Testing with Registry Access

When writing tests, you can use the `reset_registry()` function to ensure each test starts with a clean registry:

```python
from core.tools.registry_access import get_registry, reset_registry, register_tool

def setUp(self):
    # Reset registry before each test
    reset_registry()
    
    # Register mock tools for testing
    register_tool("mock_tool", lambda x: {"success": True, "result": "mocked"})
    
def test_something(self):
    # Test with a clean registry state
    registry = get_registry()
    self.assertIn("mock_tool", registry.tools)
```

## Migration Guide

1. Replace direct `ToolRegistry()` instantiations with appropriate registry_access functions
2. Replace manual tool existence checks with `tool_exists()`
3. Replace direct tool registration with `register_tool()`
4. Replace direct tool execution with `execute_tool()`
5. Replace manual tool listing with `get_available_tools()` 