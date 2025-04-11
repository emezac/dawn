# Error Propagation Between Tasks

This document describes how errors are propagated between tasks in the Dawn framework, allowing for robust error handling and recovery in workflows.

## Overview

Error propagation is a mechanism that allows errors that occur in one task to be passed to subsequent tasks in a workflow. This enables tasks to react to errors in upstream tasks, implement recovery strategies, and make decisions based on error information.

The Dawn framework provides a comprehensive error propagation system with the following features:

1. **Standardized Error Formats**: All errors follow a consistent format with error codes, messages, and detailed context
2. **Error Context Tracking**: Errors are tracked in a centralized `ErrorContext` object throughout workflow execution
3. **Error References in Templates**: Tasks can reference error information from previous tasks using template variables
4. **Error Chaining**: When errors propagate through multiple tasks, a chain of error origins is maintained
5. **Workflow-level Error Summaries**: Workflows include summaries of all errors that occurred during execution

## Using Error Propagation

### Accessing Errors from Previous Tasks

You can access error information from previous tasks using template variables in your task input:

```json
{
  "input_data": {
    "error_message": "${error.task1}",
    "error_code": "${error.task1.error_code}",
    "specific_detail": "${error.task1.error_details.field_name}"
  }
}
```

This template syntax allows you to extract specific error information:

- `${error.task_id}` - Returns the full error message from the specified task
- `${error.task_id.error_code}` - Returns just the error code
- `${error.task_id.error_details.field_name}` - Returns a specific field from the error details

### Implementing Error Handling Tasks

A common pattern is to create dedicated error handler tasks that are executed when upstream tasks fail:

```python
# Task that may fail
task1 = Task(
    task_id="task1",
    name="Task That May Fail",
    tool_name="some_tool",
    next_task_id_on_success="normal_path_task",
    next_task_id_on_failure="error_handler_task"  # Go to error handler on failure
)

# Error handler task
error_handler_task = Task(
    task_id="error_handler_task",
    name="Error Handler",
    tool_name="error_recovery_tool",
    input_data={
        "error_message": "${error.task1}",
        "error_code": "${error.task1.error_code}",
        "retry_allowed": "${error.task1.error_details.is_retryable}"
    },
    next_task_id_on_success="recovery_path_task",
    next_task_id_on_failure="terminal_error_task"
)
```

### Creating Custom Error Handler Functions

You can also implement custom error handling logic using `DirectHandlerTask`:

```python
def my_error_handler(input_data):
    # Extract error information
    error_message = input_data.get("error_message")
    error_code = input_data.get("error_code")
    
    # Implement recovery logic based on error
    if "timeout" in error_message.lower():
        return {"success": True, "result": {"action": "retry", "delay": 5}}
    elif "not found" in error_message.lower():
        return {"success": True, "result": {"action": "create_resource"}}
    else:
        return {"success": False, "error": f"Unrecoverable error: {error_message}"}

# Create the error handler task
error_handler = DirectHandlerTask(
    task_id="error_handler",
    name="Custom Error Handler",
    handler=my_error_handler,
    input_data={
        "error_message": "${error.previous_task}",
        "error_code": "${error.previous_task.error_code}"
    }
)
```

## Error Context Object

The `ErrorContext` object is responsible for tracking and managing errors throughout workflow execution. It provides several methods for working with errors:

- `record_task_error(task_id, error_data)`: Records an error that occurred in a task
- `get_task_error(task_id)`: Retrieves error information for a specific task
- `propagate_error(source_task_id, target_task_id, additional_context)`: Creates a new error that propagates from one task to another
- `get_latest_error()`: Returns the most recent error that occurred
- `get_error_summary()`: Generates a summary of all errors in the workflow

## Error Structure

Standardized error responses include the following fields:

```json
{
  "success": false,
  "status": "error",
  "error": "Human-readable error message",
  "error_code": "ERROR_CATEGORY_DESCRIPTION_NUMBER",
  "error_details": {
    "field_name": "specific_field",
    "reason": "Detailed explanation",
    "additional_context": "Any relevant information"
  },
  "timestamp": "2023-05-15T12:34:56.789Z",
  "propagation_chain": [
    {"task_id": "original_task", "timestamp": "2023-05-15T12:34:55.123Z"},
    {"task_id": "intermediate_task", "timestamp": "2023-05-15T12:34:56.456Z"} 
  ]
}
```

## Workflow Error Summary

When a workflow completes execution, it includes an error summary in its result if any errors occurred:

```json
{
  "workflow_id": "my_workflow",
  "workflow_name": "My Workflow",
  "status": "completed",
  "tasks": { /* task details */ },
  "error_summary": {
    "workflow_id": "my_workflow",
    "error_count": 2,
    "has_errors": true,
    "tasks_with_errors": ["task2", "task5"],
    "propagation_count": 1,
    "latest_error": { /* details of most recent error */ }
  }
}
```

This summary provides a high-level overview of errors that occurred during workflow execution, which is useful for monitoring and debugging.

## Best Practices

1. **Use Specific Error Codes**: Always use specific error codes rather than generic ones to make error handling more precise
2. **Include Actionable Details**: Add details to errors that help with recovery (e.g., is_retryable, retry_after)
3. **Design for Failure**: Create workflows with error handling paths for all critical tasks
4. **Use Conditional Logic**: Implement conditions that check error properties to determine the next step
5. **Log Error Chains**: Use the propagation_chain to trace error origins for complex workflows
6. **Create Recovery Tasks**: Design dedicated tasks for handling specific types of errors
7. **Validate Inputs After Errors**: Tasks that execute after an error should validate their inputs carefully

## Example: Error Recovery Workflow

Here's a complete example of a workflow that handles errors and implements recovery:

```python
# Create a workflow with error propagation
workflow = Workflow("data_processing", "Data Processing with Error Handling")

# Task 1: Data validation
validation_task = Task(
    task_id="validate_data",
    name="Validate Input Data",
    tool_name="data_validator",
    input_data={"data_source": "customer_records.csv"},
    next_task_id_on_success="process_data",
    next_task_id_on_failure="handle_validation_error"
)

# Task 2: Error handler for validation errors
validation_error_handler = DirectHandlerTask(
    task_id="handle_validation_error",
    name="Handle Validation Error",
    handler=validate_error_handler_func,
    input_data={
        "error_message": "${error.validate_data}",
        "error_details": "${error.validate_data.error_details}",
        "data_source": "customer_records.csv"
    },
    next_task_id_on_success="process_data",  # Continue to processing if recovery succeeds
    next_task_id_on_failure="report_failure"  # Report failure if recovery fails
)

# Add tasks to workflow
workflow.add_task(validation_task)
workflow.add_task(validation_error_handler)
# ... add more tasks

# Create and run the workflow
engine = WorkflowEngine(workflow, llm_interface, tool_registry)
result = engine.run()
```

This example demonstrates how to create a workflow that can recover from validation errors by implementing a custom error handler task.

## See Also

- [Error Codes Reference](error_codes_reference.md)
- [Standardized Error Handling](error_handling.md)
- [Workflow Design Patterns](workflow_patterns.md) 