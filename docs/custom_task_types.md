# Custom Task Types and Enhanced Condition Evaluation

This document explains two important features of the Dawn workflow system:

1. **Custom Task Types** - Creating your own specialized task types with dedicated execution strategies
2. **Enhanced Condition Evaluation** - Using improved variable scoping in task conditions

## Custom Task Types

The Dawn workflow system allows you to create custom task types by extending the base `CustomTask` class and providing a corresponding execution strategy.

### Creating a Custom Task Type

To create a custom task type:

1. **Define a Custom Task class** that extends `CustomTask`:

```python
from core.task import CustomTask

class MyCustomTask(CustomTask):
    """A custom task type with specialized behavior."""
    
    def __init__(
        self,
        task_id: str,
        name: str,
        special_param: str,  # Custom parameter specific to this task type
        input_data: Dict[str, Any] = None,
        **kwargs
    ):
        """Initialize the custom task."""
        super().__init__(
            task_id=task_id,
            name=name,
            task_type="my_custom_type",  # Unique type identifier
            input_data=input_data,
            is_llm_task=True,  # Set to True to bypass tool_name requirement
            **kwargs
        )
        # Store custom parameters as instance attributes
        self.special_param = special_param
```

> **Important:** Setting `is_llm_task=True` in your CustomTask makes it bypass the requirement for a tool name. This is useful for custom tasks that don't use the tool registry but have their own execution logic.

2. **Create an Execution Strategy** for your custom task type:

```python
from core.task_execution_strategy import TaskExecutionStrategy

class MyCustomStrategy(TaskExecutionStrategy):
    """Strategy for executing my custom task type."""
    
    async def execute(self, task: Task, **kwargs) -> Dict[str, Any]:
        """Execute the custom task.
        
        Args:
            task: The task to execute
            **kwargs: Additional arguments from the workflow engine
            
        Returns:
            Dict with execution results
        """
        # Get the processed input from the engine
        processed_input = kwargs.get("processed_input", {})
        
        # Access custom parameters on the task
        special_param = getattr(task, "special_param", None)
        
        # Execute custom logic
        try:
            # ... your custom execution logic ...
            result = "Custom result: " + special_param
            
            # Return success with the result
            return {"success": True, "result": result}
        except Exception as e:
            # Handle execution errors
            return {"success": False, "error": f"Execution error: {str(e)}"}
```

3. **Register your strategy** with the workflow engine:

```python
# Create your workflow
workflow = Workflow(workflow_id="my_workflow", name="My Workflow")

# Create the workflow engine
engine = WorkflowEngine(
    workflow=workflow,
    llm_interface=llm_interface,
    tool_registry=tool_registry
)

# Register your custom strategy
custom_strategy = MyCustomStrategy()
engine.strategy_factory.register_strategy("my_custom_type", custom_strategy)
```

4. **Use your custom task** in workflows:

```python
# Create a task of your custom type
custom_task = MyCustomTask(
    task_id="custom_task_1",
    name="My Custom Task",
    special_param="example_value",
    input_data={"key": "value"}
)
workflow.add_task(custom_task)

# Run the workflow
result = engine.run()
```

### How the Strategy Pattern Works

The workflow engine uses the Strategy Pattern to select the appropriate execution logic for each task:

1. When executing a task, the engine calls `strategy_factory.get_strategy(task)` to obtain the appropriate strategy
2. The factory checks the task's `task_type` attribute and returns the registered strategy for that type
3. The engine then delegates execution to the strategy's `execute()` method
4. The strategy has full access to the task's attributes and can implement specialized logic

## Enhanced Condition Evaluation

Tasks in the Dawn workflow system can include conditional logic that determines which task to execute next. This feature has been enhanced with improved variable scoping.

### Available Context in Conditions

When evaluating a task's condition, the following variables are available:

- `output_data`: The current task's output data
- `task`: The current task object (for advanced conditions)
- `workflow_id`: The current workflow's ID
- `workflow_name`: The current workflow's name
- `task_id`: The current task's ID
- `task_status`: The current task's status
- `task_outputs`: A dictionary mapping task IDs to their output data (only for completed tasks)
- `workflow_vars`: The workflow's variables dictionary

Additionally, any helper functions registered with the engine are also available.

### Example Conditions

Simple conditions using the current task's output:
```python
# Check if the result contains items
condition="len(output_data.get('result', [])) > 0"

# Check if a specific field meets a threshold
condition="output_data.get('result', {}).get('score', 0) > 75"
```

Advanced conditions using workflow variables and other tasks' outputs:
```python
# Compare with a workflow variable
condition="output_data.get('result', {}).get('count', 0) > workflow_vars.get('threshold', 0)"

# Check output from another task
condition="'error' not in task_outputs.get('previous_task_id', {})"
```

Using helper functions:
```python
# Using a custom helper function
condition="is_valid(output_data.get('result')) and meets_threshold(output_data.get('score'), workflow_vars.get('min_score'))"
```

### Registering Helper Functions

You can register helper functions for use in conditions:

```python
def is_valid(data):
    """Check if data meets validation criteria."""
    return isinstance(data, dict) and "id" in data
    
def meets_threshold(value, threshold):
    """Check if a value meets or exceeds a threshold."""
    return value >= threshold

# Register helpers with the engine
engine.register_condition_helper("is_valid", is_valid)
engine.register_condition_helper("meets_threshold", meets_threshold)
```

## Security Considerations

The condition evaluation system provides a restricted execution environment:

1. Only specific safe built-in functions are available (`abs`, `all`, `any`, etc.)
2. Access to the global namespace is restricted
3. Helper functions must be explicitly registered
4. The workflow engine validates that conditions evaluate to a boolean value

This ensures that conditions cannot introduce security vulnerabilities or unintended side effects.

## Complete Example

Here's a complete example demonstrating both custom task types and enhanced condition evaluation:

```python
import os
import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from core.task import CustomTask, Task
from core.task_execution_strategy import TaskExecutionStrategy
from core.workflow import Workflow
from core.engine import WorkflowEngine
from core.llm.interface import LLMInterface
from core.services import get_services

# Define a custom task type
class DataProcessingTask(CustomTask):
    """A custom task for data processing operations."""
    
    def __init__(
        self,
        task_id: str,
        name: str,
        operation: str,
        input_data: Dict[str, Any] = None,
        **kwargs
    ):
        super().__init__(
            task_id=task_id,
            name=name,
            task_type="data_processing",
            input_data=input_data,
            **kwargs
        )
        self.operation = operation

# Define an execution strategy
class DataProcessingStrategy(TaskExecutionStrategy):
    """Strategy for executing data processing tasks."""
    
    async def execute(self, task: Task, **kwargs) -> Dict[str, Any]:
        processed_input = kwargs.get("processed_input", {})
        operation = getattr(task, "operation", None)
        data = processed_input.get("data", [])
        
        if not data:
            return {"success": False, "error": "No data provided"}
            
        if not operation:
            return {"success": False, "error": "No operation specified"}
            
        try:
            if operation == "filter":
                result = [item for item in data if item.get("value", 0) > 50]
            elif operation == "transform":
                result = [{"id": item.get("id"), "value": item.get("value") * 2} for item in data]
            elif operation == "aggregate":
                total = sum(item.get("value", 0) for item in data)
                avg = total / len(data) if data else 0
                result = {"count": len(data), "total": total, "average": avg}
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"Operation error: {str(e)}"}

# Helper functions for conditions
def has_items(data):
    """Check if data has items."""
    return isinstance(data, list) and len(data) > 0

# Main function
def main():
    # Get services
    services = get_services()
    llm_interface = LLMInterface()
    tool_registry = services.tool_registry
    
    # Create a workflow
    workflow = Workflow(
        workflow_id="data_workflow",
        name="Data Processing Workflow"
    )
    
    # Set workflow variables
    workflow.variables = {
        "threshold": 50,
        "multiply_factor": 2
    }
    
    # Add tasks
    task1 = Task(
        task_id="provide_data",
        name="Provide Sample Data",
        is_llm_task=False,
        tool_name=None,
        input_data={
            "data": [
                {"id": 1, "value": 30},
                {"id": 2, "value": 60},
                {"id": 3, "value": 90}
            ]
        }
    )
    workflow.add_task(task1)
    
    task2 = DataProcessingTask(
        task_id="filter_data",
        name="Filter Data",
        operation="filter",
        input_data={"data": "${provide_data.output_data.result}"},
        condition="len(output_data.get('result', [])) > 0 and has_items(output_data.get('result'))"
    )
    workflow.add_task(task2)
    
    # Create the engine
    engine = WorkflowEngine(
        workflow=workflow,
        llm_interface=llm_interface,
        tool_registry=tool_registry
    )
    
    # Register the strategy
    engine.strategy_factory.register_strategy("data_processing", DataProcessingStrategy())
    
    # Register helper functions
    engine.register_condition_helper("has_items", has_items)
    
    # Run the workflow
    result = engine.run()
    
    return result

if __name__ == "__main__":
    main()
```

## Best Practices

When creating custom task types:

1. **Keep Task Classes Focused**: Each custom task type should represent a specific domain concept or operation
2. **Separate Data from Logic**: Store data parameters on the task, but keep the execution logic in the strategy
3. **Handle Errors Gracefully**: Always handle exceptions and return clear error messages
4. **Document Task Parameters**: Clearly document what parameters your task accepts and how they affect execution
5. **Use Type Hints**: Use Python type hints to make your code more maintainable

When using conditions:

1. **Keep Conditions Simple**: Complex conditions are harder to debug and maintain
2. **Use Helper Functions**: Extract complex logic into helper functions for readability
3. **Check for Missing Data**: Always use `.get()` with default values to handle missing data gracefully
4. **Test Edge Cases**: Test conditions with empty data, null values, and other edge cases
5. **Document Helper Functions**: Clearly document the purpose and input/output of helper functions 

## Troubleshooting

### Common Issues and Solutions

1. **Error: "Non-LLM tasks must specify a tool_name"**
   
   When creating a standard `Task` with `is_llm_task=False`, you must provide a valid `tool_name`. This is because non-LLM tasks in Dawn are expected to execute tools.
   
   Solutions:
   - If the task is meant to execute a tool, make sure to specify the correct `tool_name`
   - If the task doesn't require a tool, use `DirectHandlerTask` instead:
     ```python
     task = DirectHandlerTask(
         task_id="my_task",
         name="My Task",
         handler=my_handler_function,
         input_data={"key": "value"}
     )
     ```
   - If you want to create a task that just returns a fixed value, register a simple pass-through tool:
     ```python
     # Register a pass-through tool
     def pass_through_tool(input_data):
         return {"success": True, "result": input_data}
     
     tool_registry.register_tool("pass_through", pass_through_tool)
     
     # Use the pass-through tool
     task = Task(
         task_id="data_provider",
         name="Data Provider",
         is_llm_task=False,
         tool_name="pass_through",
         input_data={"data": {"key": "value"}}
     )
     ```

2. **Strategy Not Found for Custom Task Type**

   If you see an error about a strategy not being found for your custom task type, make sure:
   - You've registered your strategy with the exact same `task_type` as specified in your custom task
   - The strategy registration happens before running the workflow
   - You're registering the strategy with the same engine instance that's executing the workflow

3. **Function Not Found in Safe Builtins**

   When using complex expressions in conditions, you might encounter an error about a function not being found in safe builtins. This is because only a limited set of Python builtins are available in conditions.
   
   Solutions:
   - Register a helper function for any complex logic
   - Use only the supported built-ins: `abs`, `all`, `any`, `bool`, `dict`, `float`, `int`, `len`, `list`, `max`, `min`, `round`, `sorted`, `str`, `sum`, `tuple`, `type`

4. **Task Execution Failing with Event Loop Error**

   If you see an error related to the event loop or asyncio, ensure:
   - Your strategy's `execute()` method is properly declared as `async`
   - You're not trying to call another async function without awaiting it
   - You're returning a proper result dictionary with a `success` key

5. **Type Error in Strategy Execution**

   Type errors during strategy execution usually indicate problems with:
   - Incorrect handling of the `processed_input` parameter
   - Not checking for missing or null values before operations
   - Returning a malformed result (missing required keys)
   
   Always use defensive programming in your strategy implementations:
   ```python
   # Get with default value
   data = processed_input.get("data", {})
   
   # Type checking
   if not isinstance(data, dict):
       return {"success": False, "error": "Expected dict for data"}
       
   # Safe attribute access
   attr = getattr(task, "some_attr", None)
   if attr is None:
       return {"success": False, "error": "Required attribute missing"}
   ```

6. **Engine Not Found or AttributeError**

   If you encounter errors about the engine not being found or missing attributes:
   - Make sure you're creating the WorkflowEngine instance correctly
   - Ensure you're calling methods on the correct instance
   - When using the Agent class, remember that it creates its own engine internally, so you can't directly access or configure the engine before calling `agent.run()`
   
   If you need to customize the engine, create your own WorkflowEngine instance and use it directly:
   ```python
   engine = WorkflowEngine(
       workflow=workflow,
       llm_interface=llm_interface,
       tool_registry=tool_registry
   )
   # Customize engine here...
   result = engine.run()
   ``` 