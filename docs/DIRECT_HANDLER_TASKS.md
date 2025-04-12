# Direct Handler Tasks

## Overview

DirectHandlerTask is a specialized task type in the Dawn Framework that enables direct execution of Python functions without requiring registration in the global tool registry. This provides a more flexible, maintainable, and testable approach to defining custom task logic.

DirectHandlerTask supports two execution modes:
1. **Direct handler function**: Pass a Python function directly via the `handler` parameter
2. **Registry-based handler**: Pass a string name via `handler_name` parameter that will be looked up in the HandlerRegistry

## Key Benefits

- **Simplified Workflow Development**: Define task logic directly in your workflow code
- **Reduced Boilerplate**: No need to register tools for workflow-specific functions
- **Improved Testing**: Easier to mock and test with direct function references
- **Better Code Organization**: Keep workflow-specific logic with the workflow definition
- **Enhanced Modularity**: Separate concerns between global tools and workflow-specific handlers

## Usage Modes

### Mode 1: Direct Handler Function

Pass a Python function directly to the task:

```python
from core.task import DirectHandlerTask

def process_data(task, input_data):
    # Process the input data
    result = input_data.get("value", 0) * 2
    return {
        "success": True,
        "result": result
    }

task = DirectHandlerTask(
    task_id="double_value_task",
    name="Double Value Task",
    handler=process_data,
    input_data={"value": 21}
)

workflow.add_task(task)
```

### Mode 2: Registry-Based Handler

Reference a handler function by name that's registered in a HandlerRegistry:

```python
from core.task import DirectHandlerTask
from core.services import get_handler_registry

# Register the handler (typically done during application startup)
handler_registry = get_handler_registry()

@handler_registry.register()
def process_data(input_data):
    result = input_data.get("value", 0) * 2
    return {
        "success": True,
        "result": result
    }

# Create a task that references the handler by name
task = DirectHandlerTask(
    task_id="double_value_task",
    name="Double Value Task",
    handler_name="process_data",  # References the registered handler
    input_data={"value": 21}
)

workflow.add_task(task)
```

## Handler Function Requirements

Handler functions can follow either of two patterns:

1. **Two-parameter form (recommended)**:
   ```python
   def handler(task, input_data):
       # task: The DirectHandlerTask instance
       # input_data: Dictionary containing the processed input
       return {"success": True, "result": "Task completed"}
   ```

2. **Single-parameter form**:
   ```python
   def handler(input_data):
       # input_data: Dictionary containing the processed input
       return {"success": True, "result": "Task completed"}
   ```

The handler function should return a dictionary with at least:
- `success`: Boolean indicating success or failure
- `result`: The output data on success
- `error`: Error message on failure (optional)

## Integration with the WorkflowEngine

The Dawn Framework includes a `DirectHandlerTaskExecutionStrategy` class that automatically handles the execution of `DirectHandlerTask` instances. This strategy:

1. Checks if the task has a direct handler function
2. If not, looks up the handler by name in the `HandlerRegistry`
3. Executes the handler with appropriate parameters
4. Standardizes the result format

## Error Handling

DirectHandlerTask has robust error handling capabilities:

- **Non-Dictionary Results**: If a handler returns a non-dictionary value, it's treated as a failure with an error message
- **Exception Handling**: Exceptions raised by the handler are caught and returned as standardized error responses
- **Missing Handlers**: Errors when a handler can't be found by name are properly handled and reported

## When to Use DirectHandlerTask

- **Custom Logic**: For workflow-specific functions that don't need global availability
- **Rapid Development**: For quick prototyping without tool registry management
- **Testing**: For easier testing with mock handlers
- **Simple Transformations**: For lightweight data processing or formatting
- **Integration Points**: For connecting workflows to external systems or APIs

## DirectHandlerTask vs. Registry Tools

| Feature | DirectHandlerTask | Registry Tools |
|---------|-------------------|---------------|
| **Registration** | No global registry entry needed | Must be registered globally |
| **Scope** | Local to workflow | Global across application |
| **Testing** | Easy to mock and test | Requires registry mocking |
| **Reusability** | Limited to workflow | Reusable across workflows |
| **Overhead** | Minimal | Higher due to registry lookup |
| **Use Case** | Workflow-specific logic | Common reusable functionality |

## Best Practices

1. **Choose the Right Mode**:
   - Use direct handler functions for workflow-specific logic
   - Use registry-based handlers for reusable functions shared across workflows

2. **Follow Return Format Conventions**:
   - Always return dictionaries with the standard `success` key
   - Include `result` for successful operations
   - Include `error` for failures

3. **Keep Handlers Focused**:
   - Each handler should do one thing well
   - Complex logic should be broken down into multiple tasks

4. **Provide Clear Names**:
   - Use descriptive `task_id` and `name` values
   - Use meaningful function names for registry-based handlers

5. **Handle Errors Gracefully**:
   - Catch and handle exceptions within your handlers when appropriate
   - Format error messages to be user-friendly
   - Include enough context for debugging

## Example Workflow Using DirectHandlerTask

```python
from core.workflow import Workflow
from core.task import DirectHandlerTask, Task

def validate_input(task, input_data):
    user_id = input_data.get("user_id")
    if not user_id:
        return {
            "success": False,
            "error": "Missing user_id parameter"
        }
    return {
        "success": True,
        "result": {"valid": True, "user_id": user_id}
    }

def process_results(task, input_data):
    # Process the results from the previous task
    user_data = input_data.get("user_data", {})
    return {
        "success": True,
        "result": {
            "user_id": user_data.get("id"),
            "name": user_data.get("name"),
            "processed": True
        }
    }

# Create workflow
workflow = Workflow(workflow_id="user_processor", name="User Processor Workflow")

# Add validation task using direct handler
validation_task = DirectHandlerTask(
    task_id="validate_input",
    name="Validate Input Parameters",
    handler=validate_input,
    input_data={"user_id": "${user_id}"},
    next_task_id_on_success="fetch_user_data",
    next_task_id_on_failure=None  # End workflow on validation failure
)
workflow.add_task(validation_task)

# Add tool task to fetch user data
fetch_task = Task(
    task_id="fetch_user_data",
    name="Fetch User Data",
    tool_name="fetch_user",
    input_data={"user_id": "${validate_input.result.user_id}"},
    next_task_id_on_success="process_results"
)
workflow.add_task(fetch_task)

# Add processing task using direct handler
process_task = DirectHandlerTask(
    task_id="process_results",
    name="Process User Data",
    handler=process_results,
    input_data={"user_data": "${fetch_user_data.result}"}
)
workflow.add_task(process_task)
``` 