# Dawn Framework Error Handling and Response Format

This document describes the standardized error handling and response format used throughout the Dawn framework.

## Response Format Standards

All tools and operations in the Dawn framework use a standardized response format to ensure consistency and make error handling predictable.

### Success Response Format

```json
{
  "success": true,
  "status": "success",
  "result": <result_data>,
  "response": <result_data>,  // Both fields included for backward compatibility
  "timestamp": "2023-04-28T12:34:56.789Z",
  "message": "Optional success message",  // Optional
  "metadata": {  // Optional
    "additional_info": "any value"
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "status": "error",
  "error": "Human-readable error message",
  "error_code": "ERROR_CATEGORY_CODE",
  "timestamp": "2023-04-28T12:34:56.789Z",
  "error_details": {  // Optional
    "field_name": "The field that caused the error",
    "expected_type": "Expected data type",
    "received_value": "Value that was received"
  }
}
```

### Warning Response Format

```json
{
  "success": true,
  "status": "warning",
  "result": <result_data>,
  "response": <result_data>,  // Both fields included for backward compatibility
  "warning": "Human-readable warning message",
  "timestamp": "2023-04-28T12:34:56.789Z",
  "warning_code": "WARNING_CODE",  // Optional
  "warning_details": {  // Optional
    "additional_info": "any value"
  }
}
```

## Implementation Details

### 1. Core Error Classes

The [`core/errors.py`](../core/errors.py) module defines:

- `DawnError` - Base exception class for all Dawn framework errors
- Specialized error classes (`ValidationError`, `ExecutionError`, etc.)
- Standard error codes organized by category
- Utility functions for creating standardized responses

### 2. Response Format Utilities

The [`core/tools/response_format.py`](../core/tools/response_format.py) module provides:

- `format_tool_response()` - Formats any tool result into the standard format
- `standardize_tool_response` decorator - Wraps tool functions to ensure standard responses
- `validate_tool_input` decorator - Validates tool inputs against a schema

### 3. ToolRegistry with Standardized Responses

The [`core/tools/registry.py`](../core/tools/registry.py) uses:

- Consistent error handling for all tool executions
- Support for various function signatures (no args, single arg, kwargs, etc.)
- Auto-conversion of tool results to standardized format

### 4. Backward Compatibility

To ensure backward compatibility, we've implemented these features:

- Both `result` and `response` fields are included in all success responses
- Tools can return either field, and both will be available to consumers
- Legacy error handling formats are automatically upgraded to the new format

## How to Use

### For Tool Developers

When creating new tools, you can:

1. Return the raw result and let the framework wrap it:
   ```python
   def my_tool(data):
       return "Hello, world!"  # Will be wrapped as {"success": true, "result": "Hello, world!", ...}
   ```

2. Return a partial response and let the framework complete it:
   ```python
   def my_tool(data):
       return {"result": "Hello, world!"}  # Will be enhanced with success, timestamp, etc.
   ```

3. Return a complete standardized response:
   ```python
   def my_tool(data):
       return {
           "success": True,
           "result": "Hello, world!",
           "response": "Hello, world!",
           "status": "success",
           "timestamp": datetime.now().isoformat()
       }
   ```

4. Use the decorators for automatic formatting:
   ```python
   @standardize_tool_response
   def my_tool(data):
       return "Hello, world!"
   ```

### For Tool Consumers

When using tools, you can expect:

1. Consistent response format across all tools
2. Both `result` and `response` fields available for backward compatibility
3. Standard error handling with error codes and detailed information

See the [Migrating Tools](migrating_tools.md) guide for more information on updating existing tools to use the new format.

## Error Codes

Error codes in the Dawn framework follow a standardized format:

```
<CATEGORY>_<DESCRIPTION>_<NUMBER>
```

For example: `VALIDATION_MISSING_FIELD_101`

### Error Categories

- **VALIDATION** (100-199): Input/output validation errors
- **EXECUTION** (200-299): Errors during task/tool execution
- **AUTH** (300-399): Authentication/authorization errors
- **CONNECTION** (400-499): Network/connection errors
- **RESOURCE** (500-599): Resource-related errors (not found, access denied)
- **FRAMEWORK** (600-699): Framework internal errors
- **PLUGIN** (700-799): Errors in plugin system
- **UNKNOWN** (900-999): Uncategorized errors

## Exception Classes

The framework provides specialized exception classes for different error types:

- `DawnError`: Base exception class for all framework errors
- `ValidationError`: For input validation errors
- `ExecutionError`: For errors during task/tool execution
- `ConnectionError`: For network-related errors
- `ResourceError`: For resource access errors

## Using the Error Handling System

### Creating Standard Responses

```python
from core.errors import create_error_response, create_success_response, create_warning_response, ErrorCode

# Create a success response
response = create_success_response(
    result={"key": "value"},
    message="Operation completed successfully",
    metadata={"operation_id": "123"}
)

# Create an error response
response = create_error_response(
    message="Required field 'username' is missing",
    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
    details={"field_name": "username"}
)

# Create a warning response
response = create_warning_response(
    result={"partial_data": "value"},
    warning="Some records could not be processed",
    warning_code="PARTIAL_PROCESSING",
    details={"processed": 8, "failed": 2}
)
```

### Making Tool Handlers Comply with Standard Format

Tool handlers can be decorated with the `standardize_tool_response` decorator to ensure they return responses in the standard format:

```python
from core.tools.response_format import standardize_tool_response

@standardize_tool_response
def my_tool_handler(input_data):
    # Your tool implementation
    return result
```

Or you can manually ensure compliance by using the formatting utilities:

```python
from core.tools.response_format import format_tool_response

def my_tool_handler(input_data):
    try:
        # Your tool implementation
        result = do_something()
        return format_tool_response(result)
    except Exception as e:
        return create_error_response(
            message=f"Tool execution failed: {str(e)}",
            error_code=ErrorCode.EXECUTION_TOOL_FAILED,
            details={"error_type": type(e).__name__}
        )
```

### Input Validation

For tools that require input validation, you can use the `validate_tool_input` decorator:

```python
from core.tools.response_format import validate_tool_input

@validate_tool_input(
    schema={
        "query": {"type": str},
        "max_results": {"type": int}
    },
    required_fields=["query"]
)
def search_tool_handler(input_data):
    # If we get here, validation passed
    query = input_data["query"]
    max_results = input_data.get("max_results", 10)
    # ... implementation ...
    return result
```

## Exit Code Handling

For applications or scripts using Dawn, standard exit codes are provided:

- `0`: Success
- `1`: General Error
- `2-4`: Configuration Errors
- `5-7`: Resource Errors
- `10-11`: Workflow Errors
- `20-22`: Connection Errors
- `30-32`: User Input Errors
- `40-41`: Internal Errors

The `main_wrapper` decorator can be used to handle exceptions and return appropriate exit codes:

```python
from core.errors import main_wrapper

@main_wrapper
def main():
    # Your main function
    # Any exceptions will be caught and translated to appropriate exit codes
    pass

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
```

## Adding New Error Codes

When adding new error codes to the framework, follow these guidelines:

1. Add the error code to the appropriate category in `core.errors.ErrorCode`
2. Use the standard naming format: `CATEGORY_DESCRIPTION_NUMBER`
3. Use the next available number in the category's range
4. Document the error code and its meaning 