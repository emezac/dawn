# Direct Handler Tasks

## Overview

`DirectHandlerTask` is a core feature of the Dawn framework that allows you to create tasks that execute a function directly without requiring registration in the global tool registry. This provides a more flexible, maintainable, and testable approach to defining custom task logic.

## When to Use DirectHandlerTask

- **Custom Logic**: When you need to execute custom logic that doesn't warrant a global tool
- **Workflow-Specific Tasks**: For tasks that are specific to a particular workflow
- **Testing**: For easier testing of workflows with mock handlers
- **Rapid Development**: To quickly iterate on task implementations without registry management
- **Lightweight Tasks**: For simple transformations or processing that don't need tool infrastructure

## DirectHandlerTask vs. Registry Tools

| Feature | DirectHandlerTask | Registry Tools |
|---------|-------------------|---------------|
| **Registration** | No registry entry needed | Must be registered globally |
| **Scope** | Local to workflow | Global across application |
| **Testing** | Easy to mock and test | Requires registry mocking |
| **Reusability** | Limited to workflow | Reusable across workflows |
| **Overhead** | Minimal | Higher due to registry lookup |
| **Use Case** | Workflow-specific logic | Common reusable functionality |

## Creating a DirectHandlerTask

### Basic Example

```python
from core.task import DirectHandlerTask

# Define a handler function
def process_data(input_data):
    result = input_data.get("value", 0) * 2
    return {
        "success": True,
        "result": result
    }

# Create a DirectHandlerTask with the handler
task = DirectHandlerTask(
    task_id="double_value_task",
    name="Double Value Task",
    handler=process_data,
    input_data={"value": 21}
)

# Add to workflow
workflow.add_task(task)
```

### Handler Function Requirements

Your handler function should:

1. Accept a single dictionary parameter containing the task input data
2. Return a dictionary with at least:
   - `success`: Boolean indicating success or failure
   - `result`: The output data on success
   - `error`: Error message on failure (optional)

Example handler function:

```python
def sample_handler(data):
    try:
        # Process the input data
        result = perform_calculation(data)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Processing failed: {str(e)}"
        }
```

## Advanced Usage

### Conditional Tasks

```python
# Create a task with a condition
validation_task = DirectHandlerTask(
    task_id="validate_input",
    name="Validate Input Data",
    handler=validate_data,
    input_data={"data": user_input},
    condition="output_data.get('is_valid') == True",
    next_task_id_on_success="process_data",
    next_task_id_on_failure="handle_invalid_data"
)
```

### Using Dependencies in Handlers

```python
from services.data_service import DataService

# Handler that uses external service
def fetch_user_data(input_data):
    user_id = input_data.get("user_id")
    if not user_id:
        return {"success": False, "error": "Missing user_id"}
    
    data_service = DataService()
    try:
        user_data = data_service.get_user(user_id)
        return {
            "success": True,
            "result": user_data
        }
    except Exception as e:
        return {
            "success": False, 
            "error": f"Failed to fetch user data: {str(e)}"
        }

# Create the task
fetch_task = DirectHandlerTask(
    task_id="fetch_user",
    name="Fetch User Data",
    handler=fetch_user_data,
    input_data={"user_id": "12345"}
)
```

### Using Lambda Functions

For simple operations, you can use lambda functions:

```python
# Simple transformation using lambda
transform_task = DirectHandlerTask(
    task_id="format_name",
    name="Format User Name",
    handler=lambda data: {
        "success": True,
        "result": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
    },
    input_data={"first_name": "John", "last_name": "Doe"}
)
```

## Best Practices

1. **Keep Handlers Focused**: Each handler should do one thing well
2. **Handle Errors Gracefully**: Always return proper error responses
3. **Validate Inputs**: Check required fields at the start of your handler
4. **Use Descriptive Names**: Give handlers and tasks meaningful names
5. **Document Complex Logic**: Add docstrings to handler functions
6. **Consider Performance**: For computationally intensive tasks, consider async execution
7. **Test Thoroughly**: Write unit tests for handler functions and integration tests for workflows

## Converting Monkey-Patched Tasks

If you were previously using monkey-patched DirectHandlerTasks, here's how to convert them:

Before:
```python
# Monkey-patched DirectHandlerTask
class DirectHandlerTask(Task):
    def __init__(self, task_id, name, handler, input_data=None, condition=None, 
                next_task_id_on_success=None, next_task_id_on_failure=None, max_retries=0):
        super().__init__(
            task_id=task_id,
            name=name,
            tool_name="_direct_handler_",
            is_llm_task=False,
            input_data=input_data,
            condition=condition,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            max_retries=max_retries,
        )
        self.handler = handler
        self._is_direct_handler = True

    def execute(self, agent=None):
        result = self.handler(self.input_data)
        self.output_data = result
        return result.get("success", False)

# Monkey-patched WorkflowEngine
original_execute_task = WorkflowEngine.execute_task
def patched_execute_task(self, task):
    if isinstance(task, DirectHandlerTask):
        result = task.execute(agent=None)
        return result
    else:
        return original_execute_task(self, task)
WorkflowEngine.execute_task = patched_execute_task
```

After:
```python
from core.task import DirectHandlerTask

# Use the built-in DirectHandlerTask
task = DirectHandlerTask(
    task_id="my_task",
    name="My Task",
    handler=my_handler_function,
    input_data=input_data
)

# No need to monkey-patch the WorkflowEngine!
```

## Testing DirectHandlerTasks

### Unit Testing a Handler

```python
import unittest

class TestHandlers(unittest.TestCase):
    def test_data_processor(self):
        # Test the handler function directly
        result = process_data({"value": 10})
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], 20)
        
        # Test with invalid input
        result = process_data({"wrong_key": 10})
        self.assertTrue(result["success"])  # Should still succeed
        self.assertEqual(result["result"], 0)  # Default value * 2
```

### Integration Testing with Workflows

```python
from unittest.mock import MagicMock
from core.engine import WorkflowEngine
from core.task import DirectHandlerTask
from core.workflow import Workflow

class TestWorkflow(unittest.TestCase):
    def test_workflow_with_direct_handlers(self):
        # Create a workflow with a DirectHandlerTask
        workflow = Workflow(workflow_id="test_wf", name="Test Workflow")
        
        # Create a task with a mock handler
        mock_handler = MagicMock(return_value={"success": True, "result": "Processed"})
        task = DirectHandlerTask(
            task_id="mock_task",
            name="Mock Task",
            handler=mock_handler
        )
        workflow.add_task(task)
        
        # Run the workflow
        engine = WorkflowEngine(workflow=workflow, 
                              llm_interface=MagicMock(), 
                              tool_registry=MagicMock())
        result = engine.run()
        
        # Verify the handler was called
        mock_handler.assert_called_once()
        self.assertEqual(result["status"], "completed")
```

## Conclusion

`DirectHandlerTask` provides a powerful way to create custom task logic without the overhead of tool registration. By integrating your functions directly into the workflow, you can create more self-contained, testable, and maintainable workflows. 