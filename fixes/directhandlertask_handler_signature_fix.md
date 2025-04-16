# DirectHandlerTask Handler Function Signature Fix

## Problem Description

The `economic_impact_researcher.py` script was failing with the following error:

```
Error in custom_plan_user_request_handler: 'DirectHandlerTask' object has no attribute 'get'
Traceback (most recent call last):
  File "/Users/admin/code/newstart/dawn/examples/economic_impact_researcher.py", line 275, in custom_plan_user_request_handler
    topic = task_input_data.get("topic", "")
AttributeError: 'DirectHandlerTask' object has no attribute 'get'
```

This error occurred when the handler function for the first task (`plan_research`) was executed. The handler function was defined with the wrong parameter signature.

## Root Cause

The handler function signatures in the Dawn framework have changed. Previously, handler functions were expecting `(task_input_data, task_context)` parameters, but now they should accept `(task, task_input_data)` where:

- `task` is the `DirectHandlerTask` instance itself
- `task_input_data` is the dictionary containing the inputs

The problem occurred because the `custom_plan_user_request_handler` function was expecting a dictionary as its first parameter and trying to call the `.get()` method on it, but it was actually receiving the `DirectHandlerTask` object.

## Solution

Updated the `custom_plan_user_request_handler` function signature to match the expected framework convention:

```python
# Old signature
def custom_plan_user_request_handler(task_input_data: dict, task_context: dict) -> dict:
    # Function that expects task_input_data to be a dictionary
    topic = task_input_data.get("topic", "")
    # ...

# New signature
def custom_plan_user_request_handler(task, task_input_data: dict) -> dict:
    # Function that expects task to be a DirectHandlerTask and task_input_data to be a dictionary
    topic = task_input_data.get("topic", "")
    # ...
```

Also modified the function body to properly access services and context:
- Removed references to `task_context` parameter
- Added `services = get_services()` to access services directly
- Used `services.get_service("llm")` to get the LLM interface

This change correctly handles the parameters passed by the workflow engine when executing the task.

## Verification

After making these changes, the handler function properly receives and processes the input data, allowing the workflow to proceed to the next tasks.

## Additional Notes

This change is part of the framework's evolution toward a more consistent interface for handler functions. When the framework changes how it calls handler functions, all custom handlers need to be updated to match the new parameter patterns.

It's important to note that handler functions in the Dawn framework can now receive the task object directly, allowing them to access task properties and service context without needing an additional context parameter.

# DirectHandlerTask Signature Fix

## Issue

The `DirectHandlerTask` constructor was updated to require both `task_id` and `name` parameters, but existing code was still using the older signature with just `id`. This caused TypeError exceptions when trying to create task objects.

Additionally, handler functions needed to be updated to use a consistent signature pattern that properly accesses services and logging from the task object.

## Symptoms

- `TypeError: __init__() missing 2 required positional arguments: 'task_id' and 'name'` when creating a `DirectHandlerTask`
- `'DirectHandlerTask' object has no attribute 'services'` when executing handler functions
- Handler functions incorrectly accessing services using global registry rather than from the task object

## Solution

### 1. Update DirectHandlerTask Constructor Calls

Replace all `DirectHandlerTask` constructor calls to use `task_id` instead of `id`, and add a required `name` parameter:

```python
# Old version
task = DirectHandlerTask(
    id="my_task",
    handler=my_handler_function,
    input_data={...}
)

# New version
task = DirectHandlerTask(
    task_id="my_task",
    name="My Task",
    handler=my_handler_function,
    input_data={...}
)
```

### 2. Use a Consistent Handler Signature Pattern

All handler functions should follow this pattern:

```python
def custom_handler(task, input_data: dict) -> dict:
    """Handler function description.
    
    Args:
        task: The DirectHandlerTask object
        input_data: Dictionary containing input data
        
    Returns:
        Dictionary with result data
    """
    # Get logger from task object's workflow context
    logger = task.logger if hasattr(task, 'logger') else logging.getLogger(__name__)
    
    logger.info("Starting task execution")
    
    try:
        # Access input data
        some_input = input_data.get("input_key")
        
        # Access services through the task object
        llm = task.services.get_llm_interface() if hasattr(task, 'services') else None
        
        # Process data and return result
        return {
            "status": "success",
            "result": "Processed result"
        }
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": f"Error: {str(e)}"
        }
```

### 3. Handle JSON Serialization for TaskOutput Objects

When saving results to JSON, convert TaskOutput objects to dictionaries:

```python
# Convert TaskOutput objects to dictionaries for JSON serialization
serializable_results = {}
for task_id, output in results.items():
    if hasattr(output, 'to_dict'):
        serializable_results[task_id] = output.to_dict()
    else:
        serializable_results[task_id] = output

with open("results.json", "w") as f:
    json.dump(serializable_results, f, indent=2)
```

## Notes

- Always check if attributes exist on task objects before accessing them to prevent errors
- Use `task.logger` if available, otherwise fall back to creating a logger
- Similarly, use `task.services` if available for accessing framework services
- Handle exceptions in handler functions and return structured error responses
- Always convert TaskOutput objects to dictionaries before JSON serialization 