# Dawn Framework Error Handling Guide

This guide explains the standardized approach to error handling within the Dawn framework.

## Table of Contents

1. [Overview](#overview)
2. [Error Response Format](#error-response-format)
3. [Success Response Format](#success-response-format)
4. [Error Classes](#error-classes)
5. [Error Codes](#error-codes)
6. [Utility Functions](#utility-functions)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Overview

The Dawn framework provides a comprehensive error handling system designed to:

- Standardize error reporting across the framework
- Provide meaningful error messages with appropriate context
- Categorize errors by type and severity
- Enable proper error handling at each level of the application
- Support debugging with optional stack traces
- Ensure consistent responses for both successes and errors

This system is implemented in the `core.errors` module, which provides error classes, utility functions, and standardized response formats.

## Error Response Format

All errors in the Dawn framework follow a consistent response format:

```json
{
  "error": {
    "code": 1000,
    "type": "INVALID_INPUT",
    "message": "Missing required field: username",
    "details": {
      "field": "username"
    },
    "trace": "..."  // Optional stack trace
  }
}
```

This format includes:

- **code**: A numeric error code from the `ErrorCode` enum
- **type**: The string name of the error code
- **message**: A human-readable error message
- **details**: (Optional) Additional context about the error
- **trace**: (Optional) Stack trace for debugging

## Success Response Format

For consistency, successful responses also follow a standardized format:

```json
{
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",  // Optional
  "metadata": {
    // Optional metadata
  }
}
```

This format includes:

- **data**: The main response data
- **message**: (Optional) A human-readable success message
- **metadata**: (Optional) Additional metadata about the response

## Error Classes

The framework provides a hierarchy of error classes for different types of errors:

```
DawnError (base class)
├── InputValidationError
├── ResourceError
├── ServiceError
├── ToolError
├── TaskError
└── WorkflowError
```

### DawnError

Base class for all errors in the Dawn framework.

```python
class DawnError(Exception):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.UNEXPECTED_ERROR
    ):
        # ...
    
    def to_response(self) -> Dict[str, Any]:
        # ...
```

### InputValidationError

Used for validation errors when input data doesn't meet requirements.

```python
class InputValidationError(DawnError):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.INVALID_INPUT
    ):
        # ...
```

### ResourceError

Used for errors related to resources like files, databases, etc.

```python
class ResourceError(DawnError):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND
    ):
        # ...
```

### ServiceError

Used for errors related to external services and APIs.

```python
class ServiceError(DawnError):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.SERVICE_ERROR
    ):
        # ...
```

### ToolError

Used for errors related to tool execution.

```python
class ToolError(DawnError):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.TOOL_EXECUTION_ERROR
    ):
        # ...
```

### TaskError

Used for errors related to task execution.

```python
class TaskError(DawnError):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.TASK_EXECUTION_ERROR
    ):
        # ...
```

### WorkflowError

Used for errors related to workflow execution.

```python
class WorkflowError(DawnError):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.WORKFLOW_EXECUTION_ERROR
    ):
        # ...
```

## Error Codes

Error codes are organized by category, with each category having a dedicated range:

- **1000-1999**: Input validation errors
- **2000-2999**: Resource errors
- **3000-3999**: Service errors
- **4000-4999**: Tool errors
- **5000-5999**: Task errors
- **6000-6999**: Workflow errors
- **9000-9999**: Generic errors

Example error codes:

```python
class ErrorCode(Enum):
    # Input validation errors (1000-1999)
    INVALID_INPUT = 1000
    MISSING_REQUIRED_FIELD = 1001
    INVALID_FORMAT = 1002
    
    # Resource errors (2000-2999)
    RESOURCE_NOT_FOUND = 2000
    RESOURCE_ALREADY_EXISTS = 2001
    RESOURCE_ACCESS_DENIED = 2002
    
    # Service errors (3000-3999)
    SERVICE_UNAVAILABLE = 3000
    SERVICE_TIMEOUT = 3001
    SERVICE_ERROR = 3002
    RATE_LIMIT_EXCEEDED = 3003
    
    # ...and more
```

## Utility Functions

The framework provides utility functions for creating and checking responses:

### create_error_response

Creates a standardized error response.

```python
def create_error_response(
    code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    trace: Optional[str] = None
) -> Dict[str, Any]:
    # ...
```

### create_success_response

Creates a standardized success response.

```python
def create_success_response(
    data: Any,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    # ...
```

### is_error_response

Checks if a response is an error response.

```python
def is_error_response(response: Dict[str, Any]) -> bool:
    # ...
```

### is_success_response

Checks if a response is a success response.

```python
def is_success_response(response: Dict[str, Any]) -> bool:
    # ...
```

### safe_execute

Executes a function and handles any exceptions, returning either the result or an error response.

```python
def safe_execute(func: Callable[..., T], *args, **kwargs) -> Union[T, Dict[str, Any]]:
    # ...
```

## Best Practices

### When to Raise vs When to Return Errors

1. **Raise exceptions** when:
   - The error should interrupt the normal flow of execution
   - The caller is expected to handle the exception
   - Working within a function where exceptions will be caught and handled by a higher level

2. **Return error responses** when:
   - The function is a service or API endpoint
   - The caller expects a response object (success or error)
   - The error doesn't need to interrupt execution flow

### Designing Error Messages

1. **Be specific**: Clearly describe what went wrong
2. **Be actionable**: Hint at what the user can do to fix the issue
3. **Provide context**: Include relevant details about the error state
4. **Avoid technical jargon** in user-facing messages
5. **Use consistent terminology** throughout error messages

### Adding Error Details

Use the `details` dictionary to provide additional context:

```python
raise InputValidationError(
    "Invalid email format",
    details={
        "field": "email",
        "value": input_email,
        "pattern": EMAIL_PATTERN
    }
)
```

### Error Handling in Components

#### In Tools

```python
def execute(self, data):
    # Validate input first
    validation_error = self.validate_input(data)
    if validation_error:
        return validation_error.to_response()
    
    try:
        # Process the request
        result = self.process(data)
        return create_success_response(result)
    except DawnError as e:
        return e.to_response()
    except Exception as e:
        return create_error_response(
            ErrorCode.UNEXPECTED_ERROR,
            str(e),
            {"exception_type": type(e).__name__}
        )
```

#### In Tasks

```python
def execute_task(self):
    try:
        # Execute the task
        result = self.do_work()
        return create_success_response(result)
    except DawnError as e:
        log_error(f"Task error: {e.message}")
        return e.to_response()
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}", exc_info=True)
        return create_error_response(
            ErrorCode.TASK_EXECUTION_ERROR,
            f"Task failed: {str(e)}",
            {"exception_type": type(e).__name__}
        )
```

#### In Workflows

Use aggregated error handling for multiple task results:

```python
results = []
error_count = 0

for task in tasks:
    result = task.execute()
    results.append(result)
    if is_error_response(result):
        error_count += 1

if error_count == len(tasks):
    return create_error_response(
        ErrorCode.WORKFLOW_EXECUTION_ERROR,
        "Workflow failed: all tasks failed",
        {"total_tasks": len(tasks), "failed_tasks": error_count}
    )
elif error_count > 0:
    return create_success_response(
        {"results": results},
        message="Workflow completed with some errors",
        metadata={"total_tasks": len(tasks), "failed_tasks": error_count}
    )
else:
    return create_success_response(
        {"results": results},
        message="Workflow completed successfully"
    )
```

## Examples

### Basic Error Handling

```python
from core.errors import InputValidationError, create_error_response, ErrorCode

def validate_user_data(user_data):
    if "username" not in user_data:
        return create_error_response(
            ErrorCode.MISSING_REQUIRED_FIELD,
            "Missing required field: username",
            {"field": "username"}
        )
    
    if len(user_data["username"]) < 3:
        return create_error_response(
            ErrorCode.INVALID_INPUT,
            "Username must be at least 3 characters long",
            {"field": "username", "min_length": 3, "actual_length": len(user_data["username"])}
        )
    
    return None  # No error
```

### Using Error Classes

```python
from core.errors import InputValidationError, ErrorCode

def validate_user_data(user_data):
    if "username" not in user_data:
        raise InputValidationError(
            "Missing required field: username",
            {"field": "username"},
            ErrorCode.MISSING_REQUIRED_FIELD
        )
    
    if len(user_data["username"]) < 3:
        raise InputValidationError(
            "Username must be at least 3 characters long",
            {"field": "username", "min_length": 3, "actual_length": len(user_data["username"])}
        )
```

### Handling Errors in API Endpoints

```python
from core.errors import DawnError, create_success_response, create_error_response, ErrorCode

def user_api_endpoint(request_data):
    try:
        # Validate the request
        validation_error = validate_user_data(request_data)
        if validation_error:
            return validation_error
        
        # Process the request
        user = create_user(request_data)
        return create_success_response(
            {"user_id": user.id, "username": user.username},
            message="User created successfully"
        )
    except DawnError as e:
        return e.to_response()
    except Exception as e:
        return create_error_response(
            ErrorCode.UNEXPECTED_ERROR,
            str(e),
            {"exception_type": type(e).__name__}
        )
```

### Using safe_execute

```python
from core.errors import safe_execute

def api_endpoint(request_data):
    result = safe_execute(process_request, request_data)
    return result  # Either the result or an error response
```

### Complete Tool Example

See the [complete example](../examples/error_handling_example.py) for a detailed implementation of error handling in a tool and task. 