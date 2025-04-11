# Improved Task Output and Variable Resolution

## Overview

This document describes the improvements made to task output handling and variable resolution in the Dawn framework. These improvements enhance the flexibility and reliability of workflows by providing better support for complex data structures and more intuitive variable syntax.

## Key Improvements

### 1. DirectHandlerTask Support

The `DirectHandlerTask` class provides a way to execute handler functions directly without requiring registration in the global tool registry:

```python
from core.task import DirectHandlerTask

def my_handler(input_data):
    # Process input data
    result = process_data(input_data)
    return {
        "success": True,
        "result": result
    }

task = DirectHandlerTask(
    task_id="my_task",
    name="My Task",
    handler=my_handler,
    input_data={"key": "value"}
)
```

Benefits:
- Simplifies workflow creation by eliminating the need for tool registry registration
- Improves testability of workflows
- Allows for workflow-specific handlers without polluting the global registry
- Supports more flexible error handling and return types

### 2. Enhanced Variable Resolution

The variable resolution system now supports access to deeply nested data structures using a more intuitive dot notation:

```python
# Old syntax (basic support only)
"${task_name}.output_data.result"

# New syntax (supports nested objects and arrays)
"${task_name.output_data.result.nested.field}"
"${task_name.output_data.result.array[0].field}"
```

Features:
- Access to any level of nested objects
- Support for array indexing
- Improved error handling with detailed messages
- Graceful fallback when referenced tasks have not completed

### 3. Standardized Task Output

All tasks now return a standardized output format:

```python
{
    "success": True,          # Boolean indicating success/failure
    "result": {...},          # The actual result data
    "error": "Error message", # Present only on failure
    "error_type": "ErrorType" # Type of error (optional)
}
```

Benefits:
- Consistent access to task results
- Clearer error information
- Better support for conditional branching based on task status

### 4. Workflow Engine Integration

Both the synchronous `WorkflowEngine` and asynchronous `AsyncWorkflowEngine` now fully support `DirectHandlerTask` execution:

```python
# Both engines now use the same approach
if hasattr(task, "is_direct_handler") and task.is_direct_handler:
    # Execute DirectHandlerTask directly
    result = task.execute(processed_input)
else:
    # Handle regular task types
    ...
```

This ensures consistent behavior across different execution models.

## Usage Examples

### Basic Variable Resolution

```python
# Task 1 produces output with a nested structure
task1.output_data = {
    "result": {
        "user": {
            "name": "Alice",
            "settings": {
                "theme": "dark"
            }
        },
        "items": [
            {"id": 1, "value": "first"},
            {"id": 2, "value": "second"}
        ]
    }
}

# Task 2 can access these values with the new syntax
task2 = Task(
    task_id="task2",
    name="Task 2",
    tool_name="some_tool",
    input_data={
        "userName": "${task1.output_data.result.user.name}",           # Resolves to "Alice"
        "theme": "${task1.output_data.result.user.settings.theme}",    # Resolves to "dark"
        "firstItem": "${task1.output_data.result.items[0].value}"      # Resolves to "first"
    }
)
```

### DirectHandlerTask with Variable Resolution

```python
def first_handler(input_data):
    return {
        "success": True,
        "result": {
            "data": "Hello, World!",
            "count": 42
        }
    }

def second_handler(input_data):
    message = input_data.get("message")
    count = input_data.get("count")
    return {
        "success": True,
        "result": f"Message: {message}, Count: {count}"
    }

# Task 1: Generate initial data
task1 = DirectHandlerTask(
    task_id="task1",
    name="First Task",
    handler=first_handler,
    input_data={}
)

# Task 2: Process data from Task 1
task2 = DirectHandlerTask(
    task_id="task2",
    name="Second Task",
    handler=second_handler,
    input_data={
        "message": "${task1.output_data.result.data}",    # Resolves to "Hello, World!"
        "count": "${task1.output_data.result.count}"       # Resolves to 42
    }
)
```

### Error Handling

Error handling is now more consistent and provides better diagnostics:

```python
def error_handler(input_data):
    if "required_field" not in input_data:
        return {
            "success": False,
            "error": "Missing required field",
            "error_type": "ValidationError"
        }
    
    try:
        # Process data
        return {
            "success": True,
            "result": "Processed data"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Processing error: {str(e)}",
            "error_type": type(e).__name__
        }
```

## Implementation Details

### DirectHandlerTask Class

The `DirectHandlerTask` class inherits from `Task` and adds:

1. A `handler` property to store the function
2. An `is_direct_handler` flag for identification
3. An `execute()` method that directly calls the handler

```python
class DirectHandlerTask(Task):
    def __init__(self, task_id, name, handler, input_data=None, ...):
        super().__init__(
            task_id=task_id,
            name=name,
            tool_name="__direct_handler__",  # Special placeholder
            is_llm_task=False,
            input_data=input_data,
            ...
        )
        self.handler = handler
        self.is_direct_handler = True
        
    def execute(self, processed_input=None):
        # Use provided input or fall back to task's input_data
        input_to_use = processed_input if processed_input is not None else self.input_data
        
        try:
            return self.handler(input_to_use)
        except Exception as e:
            return {
                "success": False,
                "error": f"Handler execution failed: {str(e)}",
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
```

### Variable Resolution

The variable resolution mechanism uses a robust parser to:

1. Identify variable placeholders with regex matching
2. Parse nested paths from dot notation
3. Handle array indices when specified
4. Resolve values by traversing the data structure
5. Provide helpful error messages when resolution fails

## Best Practices

1. **Use DirectHandlerTask for workflow-specific logic**
   - Use `DirectHandlerTask` for custom logic that doesn't need to be globally available
   - Use the tool registry for common functionality shared across workflows

2. **Structure your data consciously**
   - Use consistent field names for easier variable resolution
   - Keep nested structures reasonably flat to maintain readability

3. **Handle errors gracefully**
   - Always include `success`, `result`, and `error` fields in handler returns
   - Provide specific error types for better debugging

4. **Test variable resolution paths**
   - Verify that all variables resolve correctly before deploying workflows
   - Add validation in handler functions for required fields

## Conclusion

These improvements enable more sophisticated workflows with cleaner code, better error handling, and more flexible data passing between tasks. The ability to use direct handler functions and access complex nested data structures makes the Dawn framework more powerful and easier to use. 