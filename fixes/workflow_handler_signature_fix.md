# Workflow Handler Signature Mismatch Fix

## Issue

The Dawn framework has a discrepancy in how handler functions are registered and called:

1. The `HandlerRegistry` class registers handlers that expect a single parameter (`input_data`) and calls them with just that parameter via its `execute_handler` method.

2. However, the `DirectHandlerTaskExecutionStrategy` expects handlers to accept two parameters (`task` and `input_data`), and when the task's handler is called directly (not via registry), it's called with both parameters.

This creates a conflict when implementing handlers that need to work with both mechanisms.

## Error Symptoms

The error manifests as:

```
ERROR: Engine error executing task 'get_user_criteria': get_user_input_handler() takes 1 positional argument but 2 were given
```

Or if you adapt your handlers to use two parameters:

```
ERROR: Engine error executing task 'get_user_criteria': handler_adapter.<locals>.wrapper() takes 1 positional argument but 2 were given
```

## Solution: Flexible Handler Adapter

The solution is to create an adapter that can handle both calling patterns:

```python
class DummyTask:
    """Dummy task for handler compatibility."""
    def __init__(self, task_id="dummy_task"):
        self.id = task_id
        self.name = "Dummy Task"
        self.status = "running"
        self.input_data = {}
        self.output_data = {}
        
    def set_status(self, status):
        self.status = status
        
    def set_output(self, output):
        self.output_data = output

def handler_adapter(handler_func):
    """Adapter to make 2-param handlers compatible with both 1-param and 2-param calls.
    
    Args:
        handler_func: The handler function that takes (task, input_data).
        
    Returns:
        A function that can handle both (input_data) and (task, input_data) calls.
    """
    def wrapper(*args):
        if len(args) == 1:
            # Called with just input_data (by registry)
            input_data = args[0]
            dummy_task = DummyTask()
            return handler_func(dummy_task, input_data)
        elif len(args) == 2:
            # Called with task, input_data (by engine directly)
            task, input_data = args
            return handler_func(task, input_data)
        else:
            raise ValueError(f"handler_adapter wrapper called with unexpected arguments: {args}")
    return wrapper
```

## Usage

1. Write your handlers using the 2-parameter pattern (`task, input_data`):

```python
def my_handler(task, input_data):
    # Process input_data
    result = do_something(input_data)
    return {"success": True, "result": result}
```

2. When registering handlers, wrap them with the adapter:

```python
# Register handler with adapter
register_handler("my_handler", handler_adapter(my_handler))
```

This enables your handlers to work correctly whether they're called directly with both parameters or via the registry with just one parameter.

## Long-term Solution

For a more permanent solution, the framework could be updated in one of these ways:

1. Update the HandlerRegistry to pass both task and input_data to the handlers
2. Update the DirectHandlerTaskExecutionStrategy to only pass input_data to handlers
3. Standardize on one consistent approach throughout the codebase

## References

- `HandlerRegistry.execute_handler` (in `core/handlers/registry.py`)
- `DirectHandlerTaskExecutionStrategy.execute` (in `core/task_execution_strategy.py`) 