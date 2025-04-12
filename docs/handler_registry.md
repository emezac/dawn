# HandlerRegistry

## Overview

The `HandlerRegistry` is a core component of the Dawn framework that allows registering and managing handler functions that can be executed by `DirectHandlerTask` objects without requiring global tool registration. This provides a cleaner, more maintainable way to organize task handlers and enables separation of concerns between direct handler functions and global tools.

## Key Benefits

- **Decoupled Architecture**: Handlers can be registered independently of the global tool registry
- **Named References**: Tasks can reference handlers by name instead of requiring direct function references
- **Decorator Support**: Handlers can be registered using decorators for clean code organization
- **Validation**: Handler functions are validated at registration time for correct signature
- **Type Safety**: Strong typing ensures consistent input/output structures
- **Unit Testing**: Easier to test workflows by mocking or replacing handlers

## Usage

### Basic Handler Registration

There are three ways to register handlers:

#### 1. Using the Decorator Pattern

```python
from core.services import get_handler_registry

@get_handler_registry().register()
def process_data(input_data):
    # Process the data
    result = input_data.get("value", 0) * 2
    return {
        "success": True,
        "result": result
    }
```

#### 2. Using Named Decorator Registration

```python
@get_handler_registry().register(name="custom_processor")
def my_processor(input_data):
    # Process the data
    return {
        "success": True,
        "result": "Processed data"
    }
```

#### 3. Direct Registration Method

```python
def format_output(input_data):
    # Format the output
    return {
        "success": True,
        "result": f"Formatted: {input_data.get('text', '')}"
    }

# Register the handler with a specific name
get_handler_registry().register_handler("format_output", format_output)
```

### Using Handlers in DirectHandlerTask

Once handlers are registered, you can reference them by name in `DirectHandlerTask` instances:

```python
from core.task import DirectHandlerTask

task = DirectHandlerTask(
    task_id="process_task",
    name="Process Data Task",
    handler_name="process_data",  # Reference the registered handler by name
    input_data={"value": 42}
)
```

### Handler Function Requirements

Handler functions should:

1. Accept a single parameter (`input_data`) containing a dictionary of input parameters
2. Return a dictionary with at least a `"success"` key (boolean) and `"result"` or `"response"` key containing the output

Example of a properly structured handler:

```python
def handler_example(input_data):
    try:
        # Process input data
        value = input_data.get("value", 0)
        processed_value = value * 2
        
        # Return success response
        return {
            "success": True,
            "result": processed_value,
            # Additional fields as needed
            "metadata": {"operation": "multiply_by_2"}
        }
    except Exception as e:
        # Return error response
        return {
            "success": False,
            "error": f"Processing failed: {str(e)}",
            "error_type": type(e).__name__
        }
```

## HandlerRegistry API

### Core Methods

| Method | Description |
|--------|-------------|
| `register()` | Decorator function to register a handler using its name |
| `register_handler(name, handler)` | Register a handler under a specific name |
| `get_handler(name)` | Retrieve a handler by name |
| `execute_handler(name, input_data)` | Execute a handler with input data |
| `list_handlers()` | List all registered handler names |
| `clear()` | Clear all registered handlers |

### Using the HandlerRegistry in a Workflow Engine

The `HandlerRegistry` integrates with the workflow engine via the task execution strategy pattern:

```python
from core.services import get_services, get_handler_registry
from core.task import DirectHandlerTask
from core.workflow import Workflow

# Register handlers
@get_handler_registry().register()
def my_handler(input_data):
    return {"success": True, "result": "Success!"}

# Create a workflow
workflow = Workflow(workflow_id="example", name="Example Workflow")

# Add a task using the registered handler
task = DirectHandlerTask(
    task_id="my_task",
    name="My Task",
    handler_name="my_handler",
    input_data={"param": "value"}
)
workflow.add_task(task)

# Run the workflow
services = get_services()
engine = services.create_workflow_engine(workflow)
result = await engine.async_run()
```

## Advanced Usage

### Handler Name Conventions

It's recommended to use consistent naming conventions for handlers:

- Use snake_case for handler names (e.g., `process_user_data`)
- Group related handlers with prefixes (e.g., `user_create`, `user_update`, `user_delete`)
- Use verb_noun format to indicate action (e.g., `validate_input`, `transform_data`)

### Service Integration

The `HandlerRegistry` is integrated with the Dawn services container:

```python
from core.services import get_services

# Get handler registry from services
handler_registry = get_services().handler_registry

# Register a handler
handler_registry.register_handler("my_handler", my_handler_function)
```

### Testing with HandlerRegistry

For testing, you can create a mock handler registry:

```python
from core.tools.handler_registry import HandlerRegistry

def test_workflow_with_mock_handlers():
    # Create a mock handler registry
    mock_registry = HandlerRegistry()
    
    # Register mock handlers
    mock_registry.register_handler("test_handler", lambda data: {
        "success": True,
        "result": "Mock result"
    })
    
    # Create workflow and engine with mock registry
    workflow = create_test_workflow()
    engine = create_engine_with_registry(workflow, mock_registry)
    
    # Run the workflow and assert results
    result = await engine.async_run()
    assert result["status"] == "completed"
```

## Best Practices

1. **Register Early**: Register handlers at module import time to ensure they're available when needed
2. **Keep Handlers Pure**: Handler functions should be pure and not rely on global state
3. **Validate Inputs**: Add input validation at the start of your handler functions
4. **Use Decorators**: Prefer the decorator pattern for clean, readable code
5. **Consistent Returns**: Always return a dictionary with at least `"success"` and `"result"` keys
6. **Error Handling**: Include proper error handling in all handlers with meaningful error messages
7. **Documentation**: Add docstrings to handlers explaining their purpose and parameters
8. **Type Annotations**: Use type annotations for better code clarity and tooling support

## Example: Complete Workflow

Here's a complete example demonstrating a workflow with multiple handler functions:

```python
from core.services import get_handler_registry
from core.task import DirectHandlerTask
from core.workflow import Workflow

# Register handlers
@get_handler_registry().register()
def process_input(input_data):
    value = input_data.get("value", 0)
    processed = value * 2
    return {
        "success": True,
        "result": processed
    }

@get_handler_registry().register()
def validate_result(input_data):
    result = input_data.get("result", 0)
    is_valid = result > 10
    return {
        "success": True,
        "result": {
            "is_valid": is_valid,
            "value": result
        }
    }

@get_handler_registry().register()
def format_output(input_data):
    validation = input_data.get("validation", {})
    is_valid = validation.get("is_valid", False)
    value = validation.get("value", 0)
    
    if is_valid:
        message = f"Valid result: {value}"
    else:
        message = f"Invalid result: {value}"
        
    return {
        "success": True,
        "result": message
    }

# Create workflow
def create_workflow():
    workflow = Workflow(
        workflow_id="validation_workflow",
        name="Validation Workflow"
    )
    
    # Add tasks
    process_task = DirectHandlerTask(
        task_id="process",
        name="Process Input",
        handler_name="process_input",
        input_data={"value": 12}
    )
    workflow.add_task(process_task)
    
    validate_task = DirectHandlerTask(
        task_id="validate",
        name="Validate Result",
        handler_name="validate_result",
        input_data={"result": "${process.output_data.result}"}
    )
    workflow.add_task(validate_task)
    
    format_task = DirectHandlerTask(
        task_id="format",
        name="Format Output",
        handler_name="format_output",
        input_data={"validation": "${validate.output_data.result}"}
    )
    workflow.add_task(format_task)
    
    # Set transitions
    workflow.add_transition("process", "validate")
    workflow.add_transition("validate", "format")
    
    return workflow
```

## Integration with AsyncWorkflowEngine

The `HandlerRegistry` is fully integrated with the `AsyncWorkflowEngine`, allowing for efficient execution of workflows with direct handlers:

```python
from core.services import get_services
from core.async_workflow_engine import AsyncWorkflowEngine

# Create workflow
workflow = create_workflow()

# Get services
services = get_services()

# Create engine with handler registry
engine = AsyncWorkflowEngine(
    workflow=workflow,
    llm_interface=services.llm_interface,
    tool_registry=services.tool_registry,
    handler_registry=services.handler_registry
)

# Run workflow
result = await engine.async_run()
```

## Conclusion

The `HandlerRegistry` provides a flexible, maintainable way to organize and execute handler functions in Dawn workflows. By using named references instead of direct function references, it improves code organization, testability, and separation of concerns. Combined with `DirectHandlerTask`, it offers a powerful pattern for creating modular, reusable workflow components without the overhead of global tool registration. 