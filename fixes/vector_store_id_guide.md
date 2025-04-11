# Vector Store ID Validation in Dawn Framework

This guide explains how vector store IDs are validated throughout the Dawn framework and provides a reference for implementing proper validation in your code.

## Vector Store ID Format

In the Dawn framework, vector store IDs follow a consistent format:

- They always start with the prefix `vs_`
- After the prefix, they typically contain 24 alphanumeric characters
- Example: `vs_abcdef1234567890abcdef12`

## Validation Implementation

The primary validation code is located in `tools/openai_vs/utils/vs_id_validator.py` and includes several utility functions:

### Basic Validation

```python
def is_valid_vector_store_id(vector_store_id):
    """Check if a vector store ID is valid.
    
    Args:
        vector_store_id: The ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return (
        vector_store_id is not None and
        isinstance(vector_store_id, str) and
        len(vector_store_id) > 3 and
        vector_store_id.startswith("vs_")
    )
```

This function performs basic validation to ensure the ID:
- Is not None
- Is a string
- Has a minimum length (greater than 3 characters)
- Starts with the "vs_" prefix

### Strict Validation

```python
def is_strict_valid_vector_store_id(vector_store_id):
    """Strictly validate a vector store ID against expected format.
    
    Args:
        vector_store_id: The ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r"^vs_[a-zA-Z0-9]{24}$"
    return (
        is_valid_vector_store_id(vector_store_id) and
        bool(re.match(pattern, vector_store_id))
    )
```

This function applies stricter validation using a regex pattern to ensure:
- The ID starts with "vs_"
- It contains exactly 24 alphanumeric characters after the prefix

### Validation with Error Messages

```python
def validate_vector_store_id(vector_store_id):
    """Validate a vector store ID and return an error message if invalid.
    
    Args:
        vector_store_id: The ID to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if vector_store_id is None:
        return False, "Vector store ID cannot be None"
        
    if not isinstance(vector_store_id, str):
        return False, f"Vector store ID must be a string, got {type(vector_store_id)}"
        
    if not vector_store_id:
        return False, "Vector store ID cannot be empty"
        
    if not vector_store_id.startswith("vs_"):
        return False, "Vector store ID must start with 'vs_'"
        
    return True, ""
```

This function provides more detailed error messages explaining why validation failed.

### Assertion Validation

```python
def assert_valid_vector_store_id(vector_store_id):
    """Assert that a vector store ID is valid.
    
    Args:
        vector_store_id: The ID to validate
        
    Raises:
        ValueError: If the ID is invalid
    """
    is_valid, error = validate_vector_store_id(vector_store_id)
    if not is_valid:
        raise ValueError(f"Invalid vector store ID: {error}")
```

This function raises a ValueError with a descriptive message if validation fails.

## Where Vector Store IDs Are Used

Vector store IDs are used in several components of the framework:

### 1. Vector Store Creation

```python
# tools/openai_vs/create_vector_store.py
def create_vector_store(self, name, file_ids=None):
    # ... implementation ...
    return {
        "status": "success",
        "data": {
            "vector_store_id": vector_store_id,  # Returns ID starting with "vs_"
            "name": name
        }
    }
```

### 2. Vector Store Deletion

```python
# tools/openai_vs/delete_vector_store.py
def delete_vector_store(self, vector_store_id):
    is_valid, error = validate_vector_store_id(vector_store_id)
    if not is_valid:
        return {"status": "error", "error": error}
    # ... implementation ...
```

### 3. File Upload

```python
# tools/openai_vs/upload_file.py
def upload_file_to_vector_store(self, vector_store_id, file_path):
    is_valid, error = validate_vector_store_id(vector_store_id)
    if not is_valid:
        return {"status": "error", "error": error}
    # ... implementation ...
```

### 4. Vector Store Querying

```python
# tools/openai_vs/query.py
def query_vector_store(self, vector_store_id, query, n_results=5):
    is_valid, error = validate_vector_store_id(vector_store_id)
    if not is_valid:
        return {"status": "error", "error": error}
    # ... implementation ...
```

### 5. Testing

```python
# tests/openai_vs/test_vs_id_validator.py
def test_is_valid_vector_store_id(self):
    # Valid IDs
    self.assertTrue(is_valid_vector_store_id("vs_abcdef1234567890abcdef12"))
    self.assertTrue(is_valid_vector_store_id("vs_x"))
    
    # Invalid IDs
    self.assertFalse(is_valid_vector_store_id(None))
    self.assertFalse(is_valid_vector_store_id(""))
    self.assertFalse(is_valid_vector_store_id("invalid"))
    self.assertFalse(is_valid_vector_store_id("vs"))
```

## Common Issues and Solutions

### Issue: Using IDs Without Validation

```python
# BAD: No validation
def some_function(vector_store_id):
    client.get_vector_store(vector_store_id)  # May fail with invalid ID
```

```python
# GOOD: With validation
def some_function(vector_store_id):
    is_valid, error = validate_vector_store_id(vector_store_id)
    if not is_valid:
        return {"status": "error", "error": error}
    
    client.get_vector_store(vector_store_id)
```

### Issue: Testing with Invalid IDs

```python
# BAD: Using invalid test IDs
def test_something():
    result = tool.do_something("invalid_id")
    assert result["status"] == "success"  # Will fail
```

```python
# GOOD: Using valid test IDs
def test_something():
    result = tool.do_something("vs_test123456789012345678901")
    assert result["status"] == "success"
```

### Issue: Inconsistent ID Generation

```python
# BAD: Manual ID creation
vector_store_id = "vs_" + generate_random_string(24)
```

```python
# GOOD: Use framework functions
from tools.openai_vs.utils.id_generator import generate_vector_store_id
vector_store_id = generate_vector_store_id()
```

## Best Practices

1. **Always Validate Inputs**: Validate vector store IDs as early as possible in your functions.

2. **Use the Provided Utilities**: Use the validation functions in `vs_id_validator.py` rather than implementing your own checks.

3. **Return Standardized Errors**: Follow the pattern of returning `{"status": "error", "error": error_message}` when validation fails.

4. **Generate IDs Correctly**: Use the framework's ID generation utilities when creating new vector stores.

5. **Test with Valid IDs**: In tests, always use IDs that conform to the expected format.

6. **Use Descriptive Error Messages**: When validation fails, provide clear error messages that help identify the issue.

7. **Check Registry Implementations**: For examples of proper validation, look at existing tools in the registry that handle vector store IDs.

By following these practices and understanding how vector store IDs are validated, you'll ensure that your code integrates properly with the Dawn framework and handles vector store operations correctly. 