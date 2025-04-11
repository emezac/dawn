# Vector Store ID Validation

This document provides guidelines and best practices for validating OpenAI Vector Store IDs in the Dawn project.

## Vector Store ID Format

Vector Store IDs returned by the OpenAI API follow a specific format:

- They always start with the prefix `vs_`.
- They are followed by a string of alphanumeric characters (a-z, A-Z, 0-9).
- The total length of the ID (including the prefix) is typically fixed at 27 characters.
- The structure follows the pattern: `vs_` + 24 alphanumeric characters.

Example of a valid Vector Store ID: `vs_abc123def456ghi789jkl012`

## Validation Levels

The project provides two levels of validation for Vector Store IDs:

1. **Basic Validation**:
   - Checks that the ID is not null/None
   - Verifies it's a string type
   - Ensures it's not empty
   - Confirms it starts with the `vs_` prefix

2. **Strict Validation**:
   - Performs all the basic validation checks
   - Additionally validates against the exact pattern: `vs_[a-zA-Z0-9]{24}`
   - Ensures the format matches what is expected from the OpenAI API

## Validation Utilities

The `tools.openai_vs.utils.vs_id_validator` module provides several functions for validating vector store IDs:

### Boolean Validation Functions

```python
# Basic validation
is_valid = is_valid_vector_store_id(vector_store_id)

# Strict validation
is_strict_valid = is_strict_valid_vector_store_id(vector_store_id)
```

### Detailed Validation Functions

```python
# Get validation status and error message
is_valid, error_message = validate_vector_store_id(vector_store_id, strict=False)

# Assert valid ID (raises ValueError if invalid)
assert_valid_vector_store_id(vector_store_id, strict=False)
```

## Integration with Tools

### Current Implementation

All vector store tools currently perform basic validation:

```python
if not vector_store_id or not isinstance(vector_store_id, str):
    raise ValueError("Vector Store ID must be a non-empty string")
```

The registry also verifies that newly created vector store IDs start with "vs_":

```python
if not result or not isinstance(result, str) or not result.startswith("vs_"):
    raise ToolExecutionError(f"Invalid vector store ID format received: {result}")
```

### Enhanced Implementation

For enhanced validation, tools can use the validation utilities:

```python
from tools.openai_vs.utils.vs_id_validator import assert_valid_vector_store_id

def some_function(vector_store_id):
    # Basic validation
    assert_valid_vector_store_id(vector_store_id)
    
    # Or with strict validation for critical operations
    assert_valid_vector_store_id(vector_store_id, strict=True)
    
    # Continue with operation
    ...
```

## Testing Vector Store IDs

The project includes comprehensive tests for vector store ID validation:

1. `tests/test_vector_store_id_validation.py`: Tests the validation of vector store IDs across the codebase
2. `tests/openai_vs/test_vs_id_validator.py`: Tests the validation utility functions
3. `tests/openai_vs/test_vs_id_integration.py`: Demonstrates integration with existing tools

## Best Practices

1. **Use the validation utilities**: Instead of writing custom validation logic, use the provided utilities.
2. **Choose appropriate validation level**: 
   - Use basic validation for general operations
   - Use strict validation for critical operations or when directly interfacing with the OpenAI API
3. **Error handling**: Catch validation errors and provide meaningful messages to users
4. **Testing**: Include tests for both valid and invalid vector store IDs 