# Error Propagation Implementation

## Problem

Previously, the Dawn framework lacked a robust mechanism for propagating error information between tasks in a workflow. When a task failed, the subsequent tasks could not access detailed information about the failure, making it difficult to implement error handling and recovery strategies.

## Solution

We implemented a comprehensive error propagation system with the following components:

### 1. `ErrorContext` Class

Created a centralized error tracking mechanism in `core/error_propagation.py` that:
- Records errors from tasks with their complete context
- Maintains a history of error propagation between tasks
- Provides utilities to extract and summarize error information

```python
class ErrorContext:
    """Container for tracking error information between tasks."""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.task_errors: Dict[str, Dict[str, Any]] = {}
        self.propagated_errors: List[Dict[str, Any]] = []
    
    def record_task_error(self, task_id: str, error_data: Dict[str, Any]) -> None:
        """Record an error that occurred during a task's execution."""
        # Implementation details...
    
    def get_task_error(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the error details for a specific task."""
        # Implementation details...
    
    def propagate_error(self, source_task_id: str, target_task_id: str, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Propagate an error from one task to another with additional context."""
        # Implementation details...
```

### 2. Template Variable Resolution for Errors

Enhanced the task input processing in the `WorkflowEngine` to support error references:

```python
def process_task_input(self, task: Task) -> Dict[str, Any]:
    """Process a task's input data, resolving references to outputs of previous tasks."""
    # Implementation details...
    
    # Look for references to task outputs or errors
    matches = re.findall(r"\${([^}]+)}", value)
    for match in matches:
        # Check if this is an error reference
        if match.startswith("error."):
            # Extract the task ID and error path
            parts = match.split(".", 2)
            if len(parts) >= 3:
                task_id = parts[1]
                error_path = parts[2] if len(parts) > 2 else None
                
                # Try to get the error from the error context
                error_data = self.error_context.get_task_error(task_id)
                if error_data:
                    # Get the error value using the provided path
                    error_value = get_error_value(error_data, error_path)
                    # Replace the reference with the error value
                    # ...
```

### 3. Enhanced Task and Workflow Error Handling

Updated the `Task` and `Workflow` classes to support error tracking:

```python
# In Task class
def set_output(self, data: Dict[str, Any]) -> None:
    """Set the output data for the task with standard format."""
    # Implementation details...
    
    # Handle error data
    if "error" in data:
        output_data["error"] = data["error"]
        self.error = data["error"]
        
        if "error_type" in data:
            output_data["error_type"] = data["error_type"]
            
        if "error_details" in data:
            output_data["error_details"] = data["error_details"]
            self.error_details = data["error_details"]
```

```python
# In Workflow class
def set_error(self, error_message: str, error_code: str = ErrorCode.FRAMEWORK_WORKFLOW_ERROR, details: Optional[Dict[str, Any]] = None) -> None:
    """Set error information for the workflow."""
    self.error = error_message
    self.error_code = error_code
    
    if details:
        self.error_details.update(details)
```

### 4. Improved Error Handling in `WorkflowEngine`

Enhanced the `handle_task_failure` method to record detailed error information:

```python
def handle_task_failure(self, task: Task, result: Dict[str, Any]) -> bool:
    """Handle a task failure by retrying if possible or recording the error."""
    # Record the error in our error context
    self.error_context.record_task_error(task.id, result)
    
    # Check if the task can be retried
    if task.can_retry():
        # Retry logic...
    else:
        # Task failed permanently
        task.set_status("failed")
        
        # Extract error details
        error_message = result.get("error", "Unknown error")
        error_code = result.get("error_code", ErrorCode.UNKNOWN_ERROR)
        error_details = result.get("error_details", {})
        
        # Set detailed error output on the task
        error_output = {
            "success": False,
            "error": error_message,
            "error_code": error_code,
            "error_details": error_details
        }
        
        # Include any additional fields from the result
        # ...
```

### 5. Workflow Error Summary

Added error summary information to workflow results:

```python
def run(self) -> Dict[str, Any]:
    """Run the workflow by executing all its tasks in order."""
    # Implementation details...
            
    # Include error summary in the result if there were errors
    error_summary = None
    if self.error_context.task_errors:
        error_summary = self.error_context.get_error_summary()
        
    return {
        "workflow_id": self.workflow.id,
        "workflow_name": self.workflow.name,
        "status": self.workflow.status,
        "tasks": {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()},
        "error_summary": error_summary
    }
```

## Example Usage

With these changes, tasks can now access error information from previous tasks:

```python
# Create a task that handles errors from previous tasks
error_handler_task = Task(
    task_id="error_handler",
    name="Error Handler",
    tool_name="error_recovery_tool",
    input_data={
        "error_message": "${error.previous_task}",  # Get the full error message
        "error_code": "${error.previous_task.error_code}",  # Get only the error code
        "error_reason": "${error.previous_task.error_details.reason}"  # Get a specific detail
    },
    next_task_id_on_success="recovery_path"
)
```

## Benefits

1. **Detailed Error Context**: Tasks now have access to complete error information from previous tasks
2. **Standardized Error Format**: All errors follow a consistent format with code, message, and details
3. **Error Propagation Chains**: The system tracks how errors propagate through tasks
4. **Better Recovery Strategies**: Tasks can implement sophisticated recovery based on error details
5. **Workflow-level Error Summary**: Comprehensive error reporting at the workflow level

## Additional Resources

- [Error Propagation Documentation](../error_propagation.md)
- [Error Codes Reference](../error_codes_reference.md)
- [Example Error Handling Workflow](../../examples/demo_error_propagation.py) 