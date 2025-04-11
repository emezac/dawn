# Migrating Tool Functions to Standardized Format

This guide helps you migrate existing tool functions to use the Dawn framework's standardized error handling and response format.

## Response Format Changes

All tool functions should now return responses using the standardized format:

### Success Response

```json
{
  "success": true,
  "result": <result_data>,
  "status": "success"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CATEGORY_CODE",
  "status": "error"
}
```

## Migration Steps

### 1. Basic Tool Update

**Old format:**
```python
def my_tool(input_data):
    # Process data
    return {"result": "some result"}
```

**New format:**
```python
def my_tool(input_data):
    # Process data
    return {"success": True, "result": "some result"}
```

### 2. Using the Decorator Approach

The simplest way to update your tools is to use the `standardize_tool_response` decorator:

```python
from core.tools.response_format import standardize_tool_response

@standardize_tool_response
def my_tool(input_data):
    # Just return the result directly
    return "some result"  # Will be wrapped in {"success": true, "result": "some result"}
    
    # Or raise exceptions which will be properly formatted
    if something_wrong:
        raise ValidationError("Invalid input")
```

### 3. Add Input Validation

Use the `validate_tool_input` decorator to add standardized input validation:

```python
from core.tools.response_format import validate_tool_input

@validate_tool_input(
    schema={
        "query": {"type": str},
        "max_results": {"type": int}
    },
    required_fields=["query"]
)
@standardize_tool_response
def search_tool(input_data):
    # If we get here, validation passed
    query = input_data["query"]
    max_results = input_data.get("max_results", 10)
    # ... implementation ...
    return result
```

### 4. Tool Function Parameter Patterns

The Dawn framework supports three patterns for tool functions:

1. **No Parameters**: Functions with no parameters will be called without arguments
   ```python
   def status_tool():
       return {"success": True, "result": "System status OK"}
   ```

2. **Single Parameter**: Functions with a single parameter receive the entire input data dict
   ```python
   def process_tool(input_data):
       return {"success": True, "result": f"Processed {input_data.get('value')}"}
   ```

3. **Keyword Arguments**: Functions that unpack input as keyword arguments
   ```python
   def calculator(operation, a, b):
       # Called with calculator(operation="add", a=5, b=3)
       return {"success": True, "result": a + b}
   ```

4. **Variable Keyword Arguments**: Functions that take **kwargs
   ```python
   def flexible_tool(**kwargs):
       return {"success": True, "result": f"Got {len(kwargs)} parameters"}
   ```

### 5. Error Handling

Use the Dawn error classes for standardized error handling:

```python
from core.errors import ValidationError, ExecutionError, ErrorCode

def my_tool(input_data):
    try:
        # Validation
        if "required_field" not in input_data:
            raise ValidationError(
                message="Missing required field",
                error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                field_name="required_field"
            )
            
        # Processing
        result = process_data(input_data)
        
        # Return standardized success response
        return {"success": True, "result": result}
        
    except Exception as e:
        # Return standardized error response
        return {"success": False, "error": str(e), "error_code": ErrorCode.EXECUTION_TOOL_FAILED}
```

## Testing Your Migrated Tools

Test your migrated tools using the registry's execute_tool method:

```python
from core.tools.registry_access import get_registry, register_tool, execute_tool

# Register your tool
register_tool("my_tool", my_tool_function)

# Execute it
result = execute_tool("my_tool", {"param": "value"})

# Check the result
assert result["success"] == True
assert "result" in result
```

## Recommended Approach

For most tools, we recommend:

1. Use the `standardize_tool_response` decorator
2. Add the `validate_tool_input` decorator if input validation is needed
3. Raise appropriate exceptions rather than returning error responses directly
4. Make your function signature match how it will be called 