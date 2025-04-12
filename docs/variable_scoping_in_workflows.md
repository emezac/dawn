# Enhanced Variable Scoping in Workflow Conditions

## Introduction

The Dawn framework's workflow system allows tasks to have conditions that determine which task to execute next. This document explains the enhanced variable scoping system that provides more context and safer evaluation for these conditions.

## Key Improvements

1. **Rich Evaluation Context**: Conditions now have access to more variables and context
2. **Safe Execution Environment**: Only approved built-in functions are available
3. **Helper Function Support**: Custom functions can be registered for use in conditions
4. **Access to Workflow Variables**: Conditions can access global workflow variables
5. **Cross-Task Data Access**: Access to all completed tasks' outputs

## Available Variables in Conditions

When evaluating a task's condition, the following variables are available:

| Variable | Type | Description |
|----------|------|-------------|
| `output_data` | `Dict` | The current task's output data |
| `task` | `Task` | The current task object for accessing attributes |
| `task_id` | `str` | The current task's ID (convenience) |
| `task_status` | `str` | The current task's status (convenience) |
| `workflow_id` | `str` | The current workflow's ID |
| `workflow_name` | `str` | The current workflow's name |
| `task_outputs` | `Dict[str, Dict]` | Dictionary of all completed tasks' outputs, keyed by task ID |
| `workflow_vars` | `Dict` | The workflow's variables dictionary |
| *custom helper functions* | `Callable` | Any registered helper functions |

## Example Condition Expressions

### Basic Output Checking

```python
# Check if the task's "result" contains a certain key
condition="'data' in output_data.get('result', {})"

# Check if the "score" field exceeds a threshold
condition="output_data.get('result', {}).get('score', 0) > 75"
```

### Using Task Outputs

```python
# Check if a previous task found any matching items
condition="len(task_outputs.get('search_task', {}).get('result', [])) > 0"

# Check if an error was detected in another task
condition="'error' not in task_outputs.get('validation_task', {})"
```

### Using Workflow Variables

```python
# Compare with a workflow-level threshold
condition="output_data.get('result', {}).get('count', 0) > workflow_vars.get('min_items', 0)"

# Use workflow environment setting
condition="workflow_vars.get('environment') == 'production'"
```

### Combining Multiple Conditions

```python
# Check multiple conditions
condition="output_data.get('result', {}).get('has_data', False) and len(task_outputs.get('search_task', {}).get('result', [])) > 0"

# Use complex logic with parentheses
condition="(output_data.get('result', {}).get('score', 0) > 75 or output_data.get('result', {}).get('priority', '') == 'high') and workflow_vars.get('environment') == 'production'"
```

### Using Helper Functions

```python
# Using a custom validation function
condition="is_valid_data(output_data.get('result')) and meets_threshold(output_data.get('result', {}).get('score', 0), workflow_vars.get('min_score', 0))"
```

## Registering Helper Functions

Helper functions allow for more complex logic in conditions. Register them with the workflow engine:

```python
def is_valid_data(data):
    """Check if data is valid (e.g., has required fields)."""
    if not isinstance(data, dict):
        return False
    return all(key in data for key in ['id', 'name', 'value'])
    
def meets_threshold(value, threshold):
    """Check if a value meets or exceeds a threshold."""
    try:
        return float(value) >= float(threshold)
    except (ValueError, TypeError):
        return False

# Register helpers with the engine
engine = WorkflowEngine(workflow=workflow, ...)
engine.register_condition_helper("is_valid_data", is_valid_data)
engine.register_condition_helper("meets_threshold", meets_threshold)
```

## Safe Execution Environment

To ensure security, conditions are evaluated in a restricted environment with only these built-in functions:

```python
safe_builtins = {
    "True": True, "False": False, "None": None,
    "abs": abs, "all": all, "any": any, "bool": bool, 
    "dict": dict, "float": float, "int": int, "len": len,
    "list": list, "max": max, "min": min, "round": round,
    "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
    "type": type
}
```

Functions not in this list (like `exec`, `eval`, `__import__`, etc.) are not available.

## Implementation Details

The enhanced variable scoping is implemented in the workflow engine:

1. The `_build_condition_context()` method builds a dictionary containing all the available variables
2. The `get_next_task_by_condition()` method uses this context to evaluate conditions
3. The conditions are evaluated using Python's `eval()` function with the restricted builtins dict
4. Helper functions are stored in `self._condition_helper_funcs` and added to the context

## Best Practices

1. **Use Defensive Coding**: Always use `.get()` with default values to handle missing data
2. **Keep Conditions Simple**: Complex conditions are harder to debug and maintain
3. **Avoid Side Effects**: Helper functions should not have side effects
4. **Document Helper Functions**: Clearly document the purpose and expected inputs/outputs
5. **Test Edge Cases**: Test conditions with empty data, null values, etc.
6. **Validate Inputs**: Check types and null values in helper functions

## Examples

### Workflow with Enhanced Conditions

```python
# Create a workflow with variables
workflow = Workflow(
    workflow_id="data_workflow",
    name="Data Processing Workflow"
)

# Set workflow variables
workflow.variables = {
    "threshold": 50,
    "environment": "production",
    "retry_count": 3
}

# Add tasks with conditions
task1 = Task(
    task_id="search_data",
    name="Search Data",
    is_llm_task=True,
    input_data={"prompt": "Search for relevant data"}
)
workflow.add_task(task1)

task2 = Task(
    task_id="process_data",
    name="Process Data",
    is_llm_task=True,
    input_data={"prompt": "Process the found data: ${search_data.output_data.response}"},
    condition="len(output_data.get('response', '')) > 0 and is_valid_json(output_data.get('response'))"
)
workflow.add_task(task2)

# Create the workflow engine
engine = WorkflowEngine(
    workflow=workflow,
    llm_interface=llm_interface,
    tool_registry=tool_registry
)

# Register helpers
def is_valid_json(text):
    if not isinstance(text, str):
        return False
    try:
        import json
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False

engine.register_condition_helper("is_valid_json", is_valid_json)

# Run the workflow
result = engine.run()
```

## Error Handling

Common errors with conditions include:

1. **NameError**: An undefined variable or function was referenced
   - Check that you're using available variables and registered helpers
   - Verify that helper functions are registered before workflow execution

2. **TypeError**: An operation was performed on the wrong type
   - Use defensive coding with `.get()` and type checking
   - Verify that variables are initialized before use

3. **SyntaxError**: The condition contains Python syntax errors
   - Check for missing parentheses, quotes, or other syntax issues
   - Ensure that string literals are properly quoted

4. **AttributeError**: Trying to access attributes on None
   - Use `getattr(obj, 'attr', default_value)` for safe attribute access
   - Check for None before attribute access 