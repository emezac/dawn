# Workflow Patterns

This document provides examples of common workflow patterns in the Dawn framework, including basic task sequences, parallel execution, conditional branching, and error handling strategies.

## Basic Sequential Workflow

The simplest workflow pattern is a sequence of tasks that execute one after another:

```python
workflow = Workflow("sequential", "Basic Sequential Workflow")

# Task 1
task1 = Task(
    task_id="task1",
    name="First Task",
    tool_name="some_tool",
    input_data={"param1": "value1"},
    next_task_id_on_success="task2"
)

# Task 2
task2 = Task(
    task_id="task2",
    name="Second Task", 
    tool_name="another_tool",
    input_data={"param2": "value2"},
    next_task_id_on_success="task3"
)

# Task 3
task3 = Task(
    task_id="task3",
    name="Final Task",
    tool_name="final_tool",
    input_data={"param3": "value3"}
)

# Add tasks to workflow
workflow.add_task(task1)
workflow.add_task(task2)
workflow.add_task(task3)
```

## Parallel Task Execution

Tasks can be executed in parallel by setting the `parallel` flag:

```python
workflow = Workflow("parallel", "Parallel Execution Workflow")

# Task 1 - Will execute in parallel with Task 2
task1 = Task(
    task_id="task1",
    name="Parallel Task 1",
    tool_name="some_tool",
    input_data={"param1": "value1"},
    next_task_id_on_success="task3",
    parallel=True  # Mark as parallel
)

# Task 2 - Will execute in parallel with Task 1
task2 = Task(
    task_id="task2",
    name="Parallel Task 2", 
    tool_name="another_tool",
    input_data={"param2": "value2"},
    next_task_id_on_success="task3",
    parallel=True  # Mark as parallel
)

# Task 3 - Will execute after both Task 1 and Task 2 complete
task3 = Task(
    task_id="task3",
    name="Final Task",
    tool_name="final_tool",
    input_data={
        "result1": "${task1.result}",
        "result2": "${task2.result}"
    }
)

# Add tasks to workflow
workflow.add_task(task1)
workflow.add_task(task2)
workflow.add_task(task3)
```

## Conditional Branching

Tasks can branch based on conditions:

```python
workflow = Workflow("conditional", "Conditional Workflow")

# Initial task
task1 = Task(
    task_id="task1",
    name="Initial Task",
    tool_name="check_condition",
    input_data={"check": "some_value"},
    condition="output_data.get('result', {}).get('condition_met', False)",
    next_task_id_on_success="task2_success",  # If condition is True
    next_task_id_on_failure="task2_failure"   # If condition is False
)

# Success path
task2_success = Task(
    task_id="task2_success",
    name="Success Path",
    tool_name="success_tool",
    input_data={"message": "Condition was met"}
)

# Failure path
task2_failure = Task(
    task_id="task2_failure",
    name="Failure Path",
    tool_name="failure_tool",
    input_data={"message": "Condition was not met"}
)

# Add tasks to workflow
workflow.add_task(task1)
workflow.add_task(task2_success)
workflow.add_task(task2_failure)
```

## Error Handling Patterns

### Basic Error Handling

This pattern implements a basic error handler for a task:

```python
workflow = Workflow("error_handling", "Basic Error Handling")

# Task that might fail
data_task = Task(
    task_id="process_data",
    name="Process Data",
    tool_name="data_processor",
    input_data={"data_source": "data.csv"},
    next_task_id_on_success="success_task",
    next_task_id_on_failure="error_handler"  # Path on failure
)

# Error handler task
error_handler = Task(
    task_id="error_handler",
    name="Error Handler",
    tool_name="handle_error",
    input_data={
        "error_message": "${error.process_data}",
        "error_code": "${error.process_data.error_code}"
    },
    next_task_id_on_success="recovery_task"
)

# Recovery task
recovery_task = Task(
    task_id="recovery_task",
    name="Recovery Task",
    tool_name="recover_data",
    input_data={"backup_source": "backup_data.csv"}
)

# Success task
success_task = Task(
    task_id="success_task",
    name="Success Task", 
    tool_name="process_success",
    input_data={"result": "${process_data.result}"}
)

# Add tasks to workflow
workflow.add_task(data_task)
workflow.add_task(error_handler)
workflow.add_task(recovery_task)
workflow.add_task(success_task)
```

### Retry Pattern

This pattern implements automatic retries for tasks that might experience transient failures:

```python
workflow = Workflow("retry_pattern", "Retry Pattern Workflow")

# Task with retry logic
api_task = Task(
    task_id="api_call",
    name="API Call",
    tool_name="external_api",
    input_data={"endpoint": "https://api.example.com/data"},
    max_retries=3  # Will retry up to 3 times
)

# Add task to workflow
workflow.add_task(api_task)
```

### Fallback Pattern

This pattern implements a fallback mechanism when a primary task fails:

```python
workflow = Workflow("fallback_pattern", "Fallback Pattern Workflow")

# Primary task
primary_task = Task(
    task_id="primary_service",
    name="Primary Service",
    tool_name="primary_api",
    input_data={"endpoint": "https://primary-api.example.com"},
    next_task_id_on_success="process_result",
    next_task_id_on_failure="fallback_service"
)

# Fallback task
fallback_task = Task(
    task_id="fallback_service",
    name="Fallback Service",
    tool_name="backup_api",
    input_data={
        "endpoint": "https://backup-api.example.com",
        "original_error": "${error.primary_service}"  # Pass along the original error
    },
    next_task_id_on_success="process_result"
)

# Process result
process_task = Task(
    task_id="process_result",
    name="Process Result",
    tool_name="result_processor",
    input_data={
        # This will use either the primary or fallback result
        "result": "${primary_service.result || fallback_service.result}"
    }
)

# Add tasks to workflow
workflow.add_task(primary_task)
workflow.add_task(fallback_task)
workflow.add_task(process_task)
```

### Validation and Error Recovery

This pattern implements validation checks with custom error recovery:

```python
workflow = Workflow("validation_recovery", "Validation and Recovery Workflow")

# Validation task
validation_task = Task(
    task_id="validate_data",
    name="Validate Data",
    tool_name="data_validator",
    input_data={"data": {"user_id": 123, "email": "user@example.com"}},
    next_task_id_on_success="process_data",
    next_task_id_on_failure="handle_validation_error"
)

# Error handler using DirectHandlerTask for custom logic
def validation_error_handler(input_data):
    """Custom handler for validation errors"""
    error = input_data.get("error_details", {})
    invalid_fields = error.get("invalid_fields", [])
    
    if "email" in invalid_fields:
        # Try to fix email format issues
        return {
            "success": True,
            "result": {
                "fixed_data": {"user_id": 123, "email": "corrected@example.com"},
                "fields_fixed": ["email"]
            }
        }
    else:
        # Can't fix other validation issues
        return {
            "success": False,
            "error": "Unable to fix validation errors",
            "error_details": {"unfixable_fields": invalid_fields}
        }

# Create handler task
error_handler_task = DirectHandlerTask(
    task_id="handle_validation_error",
    name="Handle Validation Error",
    handler=validation_error_handler,
    input_data={
        "error_details": "${error.validate_data.error_details}"
    },
    next_task_id_on_success="retry_with_fixed_data",
    next_task_id_on_failure="report_validation_failure"
)

# Retry with fixed data
retry_task = Task(
    task_id="retry_with_fixed_data",
    name="Retry With Fixed Data",
    tool_name="data_processor",
    input_data={"data": "${handle_validation_error.result.fixed_data}"}
)

# Report failure
report_task = Task(
    task_id="report_validation_failure",
    name="Report Validation Failure", 
    tool_name="failure_reporter",
    input_data={
        "error": "${error.handle_validation_error}",
        "unfixable_fields": "${error.handle_validation_error.error_details.unfixable_fields}"
    }
)

# Add tasks to workflow
workflow.add_task(validation_task)
workflow.add_task(error_handler_task)
workflow.add_task(retry_task)
workflow.add_task(report_task)
```

## Combining Patterns

These patterns can be combined to create complex workflows with robust error handling:

```python
workflow = Workflow("complex", "Complex Workflow with Error Handling")

# Initial tasks running in parallel
task1 = Task(
    task_id="fetch_user",
    name="Fetch User Data",
    tool_name="user_api",
    input_data={"user_id": 123},
    parallel=True,
    next_task_id_on_success="process_combined_data",
    next_task_id_on_failure="handle_user_error"
)

task2 = Task(
    task_id="fetch_product",
    name="Fetch Product Data",
    tool_name="product_api",
    input_data={"product_id": 456},
    parallel=True,
    next_task_id_on_success="process_combined_data",
    next_task_id_on_failure="handle_product_error"
)

# Error handlers
user_error_handler = Task(
    task_id="handle_user_error", 
    name="Handle User Error",
    tool_name="user_fallback",
    input_data={"error": "${error.fetch_user}"},
    next_task_id_on_success="process_combined_data"
)

product_error_handler = Task(
    task_id="handle_product_error",
    name="Handle Product Error",
    tool_name="product_fallback", 
    input_data={"error": "${error.fetch_product}"},
    next_task_id_on_success="process_combined_data"
)

# Processing task with conditional branch
process_task = Task(
    task_id="process_combined_data",
    name="Process Combined Data",
    tool_name="data_processor",
    input_data={
        "user_data": "${fetch_user.result || handle_user_error.result}",
        "product_data": "${fetch_product.result || handle_product_error.result}"
    },
    condition="output_data.get('result', {}).get('is_valid', False)",
    next_task_id_on_success="complete_order",
    next_task_id_on_failure="cancel_order"
)

# Final tasks
complete_task = Task(
    task_id="complete_order",
    name="Complete Order",
    tool_name="order_completion",
    input_data={"processed_data": "${process_combined_data.result}"}
)

cancel_task = Task(
    task_id="cancel_order",
    name="Cancel Order",
    tool_name="order_cancellation",
    input_data={"reason": "${process_combined_data.result.invalid_reason}"}
)

# Add all tasks to workflow
workflow.add_task(task1)
workflow.add_task(task2)
workflow.add_task(user_error_handler)
workflow.add_task(product_error_handler)
workflow.add_task(process_task)
workflow.add_task(complete_task)
workflow.add_task(cancel_task)
```

## Best Practices for Error Handling

1. **Always define failure paths for critical tasks** using `next_task_id_on_failure`
2. **Include context in error handlers** by passing relevant information from the original task
3. **Use specific error codes** to enable precise error handling logic
4. **Implement retry logic** for operations that might experience transient failures
5. **Provide fallback mechanisms** for critical functionality
6. **Use the error propagation system** to pass detailed error information between tasks
7. **Log errors comprehensively** for future debugging
8. **Design recovery strategies** based on specific error types and contexts
9. **Consider the entire workflow** when designing error handling, not just individual tasks
10. **Test failure scenarios** thoroughly to ensure proper error handling

## See Also

- [Error Propagation](error_propagation.md)
- [Error Codes Reference](error_codes_reference.md)
- [Example Workflows](../examples) 