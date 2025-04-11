# Task Output and Variable Resolution Improvements

## Overview

This document describes the improvements made to task output handling and variable resolution in the Dawn workflow system. These improvements make the workflow more robust when dealing with complex data structures and variable interpolation across tasks.

## Key Improvements

### 1. DirectHandlerTask Implementation

The `DirectHandlerTask` class allows for custom processing functions to be directly executed in the workflow, bypassing the need for tool registry lookup:

```python
# Example of a DirectHandlerTask
task = DirectHandlerTask(
    task_id="parse_json_output",
    name="Parse JSON Analysis Output",
    handler=parse_llm_json_output,  # Direct function reference
    input_data={
        "llm_output": "${previous_task.output_data}"
    },
    next_task_id_on_success="next_step",
)
```

Benefits include:
- Direct access to execution context
- Custom error handling
- More predictable execution flow
- No need for tool registration

### 2. Enhanced Variable Resolution

Variable resolution has been improved to handle complex nested data structures:

```python
# New pattern for accessing nested properties
"${task_name.output_data.result.property}"  # Accesses the 'property' field inside the 'result' object
```

The system now properly resolves variables in these scenarios:
- JSON strings that need to be parsed
- Nested object properties
- Arrays/lists with indexed access
- Variables containing special characters

### 3. JSON Parsing and Extraction Utilities

New utility functions have been added to handle JSON parsing and data extraction:

```python
def extract_task_output(task_output, field_path=None):
    """
    Extract data from task output using a field path.
    
    Args:
        task_output: The task output data to extract from
        field_path: Optional dot-notation path to extract (e.g., "result.summary")
        
    Returns:
        The extracted data or the original output if no path is provided
    """
    # Implementation details for extracting data from complex structures
```

This utility helps access data from different output formats, automatically handling cases where:
- Output is a raw string
- Output is JSON that needs parsing
- Output is already a structured object

### 4. Standardized Task Output Format

Task outputs now follow a consistent format:

```python
{
    "success": True/False,     # Indicates if the task completed successfully
    "result": {},              # The actual output data in a structured format
    "error": None,             # Error message if any (null if successful)
    "error_type": None         # Type of error encountered (null if successful)
}
```

This consistent structure makes it easier to handle task outputs throughout the workflow.

### 5. Robust Error Handling

The system now handles errors more gracefully:

- Failed JSON parsing attempts additional recovery methods
- Provides detailed error information for debugging
- Allows workflows to continue executing when appropriate
- Falls back to safer default values when variables can't be resolved

### 6. Workflow Resilience

Workflows are now more resilient to missing or malformed data:

- Explicit parsing tasks between LLM and decision tasks
- Condition evaluations that handle missing values gracefully
- Multiple fallback paths for error conditions

## Usage Examples

### Handling LLM JSON Outputs

```python
# Task 1: Generate JSON with LLM
task1 = Task(
    task_id="generate_json_llm",
    name="Generate JSON Output",
    is_llm_task=True,
    input_data={"prompt": "Generate a JSON object with fields: name, age, city"}
)

# Task 2: Parse the JSON (using DirectHandlerTask)
task2 = DirectHandlerTask(
    task_id="parse_json",
    name="Parse JSON Output",
    handler=parse_llm_json_output,
    input_data={"llm_output": "${generate_json_llm.output_data}"}
)

# Task 3: Use the parsed JSON
task3 = Task(
    task_id="use_parsed_json",
    name="Use Parsed JSON",
    is_llm_task=True,
    input_data={
        "prompt": "The person's name is ${parse_json.output_data.result.name} and they live in ${parse_json.output_data.result.city}"
    }
)
```

### Conditional Logic Based on Task Output

```python
# Check a condition using a DirectHandlerTask
check_task = DirectHandlerTask(
    task_id="check_condition",
    name="Check Condition",
    handler=check_condition_handler,
    input_data={"data": "${previous_task.output_data.result}"}
)

# Conditional task execution
action_task = Task(
    task_id="conditional_action",
    name="Conditional Action",
    tool_name="some_tool",
    input_data={"param": "value"},
    condition="${check_condition.output_data.result.should_proceed}"  # Boolean value
)
```

## Implementation Details

The improvements have been applied to these workflows:
- Smart Compliance Workflow
- Context-Aware Legal Review Workflow
- Complex Parallel Workflow Example

Each workflow now uses the enhanced variable resolution and standardized task output formats, ensuring more reliable execution and easier debugging.

## Best Practices

1. Always use DirectHandlerTask for JSON parsing and data transformation
2. Structure output data consistently across all tasks
3. Use meaningful field names in task outputs
4. Include proper error handling and fallback paths
5. Test variable resolution with complex nested structures
6. Use condition evaluations that handle missing data gracefully

## Common Pitfalls

### DirectHandlerTask Limitations

The `DirectHandlerTask` class doesn't support all the parameters that the standard `Task` class does. Common issues include:

1. **Missing Dependencies Support**: The `dependencies` parameter is not supported in `DirectHandlerTask`. While you might set it as an attribute, the workflow engine won't use it for execution planning.

   ```python
   # This will cause an error:
   task = DirectHandlerTask(
       task_id="my_task",
       name="My Task",
       handler=my_handler,
       dependencies=["previous_task"],  # ERROR: Unsupported parameter
       input_data={"key": "value"}
   )
   ```

2. **Condition Format**: When using conditions with DirectHandlerTask, make sure to use the correct format:

   ```python
   # Correct condition format
   task = DirectHandlerTask(
       task_id="conditional_task",
       name="Conditional Task",
       handler=my_handler,
       condition="output_data.get('result', {}).get('needed', False)",
       input_data={"key": "value"}
   )
   ```

3. **Parameter Validation**: The constructor doesn't validate all parameters, so typos or wrong parameters might be silently ignored.

### Variable Resolution Errors

Common variable resolution issues include:

1. **Missing Square Brackets**: When accessing list items, ensure proper syntax:
   ```python
   # Correct: ${task_name.output_data.result.list[0]}
   # Incorrect: ${task_name.output_data.result.list.0}
   ```

2. **Raw References in Output**: If you see raw variable references in your output (like `${task.output_data}`), it means the resolution failed.

3. **Nested JSON String**: If a task returns JSON as a string, you might need an explicit parsing step before accessing nested properties. 