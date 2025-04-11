"""
Data Validation Utilities for Dawn Framework.

This module provides functionality for validating task inputs and outputs,
including type checking and schema validation.
"""

from typing import Any, Dict, List, Optional, Union, get_type_hints, get_origin, get_args
import inspect
import json


class ValidationError(Exception):
    """Exception raised when data validation fails."""  # noqa: D202
    
    def __init__(self, message: str, field_path: Optional[str] = None, details: Optional[Dict] = None):
        self.message = message
        self.field_path = field_path
        self.details = details or {}
        error_message = message
        if field_path:
            error_message = f"{field_path}: {message}"
        super().__init__(error_message)


def create_schema_from_type_hints(func) -> Dict[str, Any]:
    """
    Create a validation schema from a function's type hints.
    
    Args:
        func: The function to analyze
        
    Returns:
        A schema dictionary with param name -> expected type
    """
    if not callable(func):
        raise ValueError("Expected a callable function")
        
    # Get function signature and type hints
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    schema = {}
    
    # Process each parameter
    for param_name, param in sig.parameters.items():
        if param_name in type_hints:
            param_type = type_hints[param_name]
            schema[param_name] = {
                "type": param_type,
                "required": param.default is inspect.Parameter.empty,
                "default": None if param.default is inspect.Parameter.empty else param.default
            }
        else:
            # No type hint, assume Any
            schema[param_name] = {
                "type": Any,
                "required": param.default is inspect.Parameter.empty,
                "default": None if param.default is inspect.Parameter.empty else param.default
            }
            
    return schema


def validate_type(value: Any, expected_type: Any, field_path: str = "") -> None:
    """
    Validate that a value matches the expected type.
    
    Args:
        value: The value to validate
        expected_type: The expected type (can be a Union, List, Dict, etc.)
        field_path: Path to the field for error reporting
        
    Raises:
        ValidationError: If validation fails
    """
    # Handle Any type - always valid
    if expected_type is Any:
        return
    
    # Handle None
    if value is None:
        if expected_type is None or expected_type is type(None):
            return
        # Optional types are represented as Union[Type, None]
        if hasattr(expected_type, "__origin__") and expected_type.__origin__ is Union:
            if type(None) in expected_type.__args__:
                return
        raise ValidationError(f"Expected {expected_type}, got None", field_path)
    
    # Handle Union types
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ is Union:
        # Try each type in the union
        errors = []
        for arg_type in expected_type.__args__:
            try:
                validate_type(value, arg_type, field_path)
                return  # If any type validates, we're good
            except ValidationError as e:
                errors.append(str(e))
        raise ValidationError(
            f"Value didn't match any expected types: {', '.join(str(t) for t in expected_type.__args__)}",
            field_path,
            {"attempted_validations": errors}
        )
    
    # Handle List type
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ in (list, List):
        if not isinstance(value, list):
            raise ValidationError(f"Expected list, got {type(value).__name__}", field_path)
        
        # If a type is specified for list items
        if hasattr(expected_type, "__args__") and expected_type.__args__:
            item_type = expected_type.__args__[0]
            for i, item in enumerate(value):
                validate_type(item, item_type, f"{field_path}[{i}]")
        return
    
    # Handle Dict type
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ in (dict, Dict):
        if not isinstance(value, dict):
            raise ValidationError(f"Expected dict, got {type(value).__name__}", field_path)
        
        # If key and value types are specified
        if hasattr(expected_type, "__args__") and len(expected_type.__args__) == 2:
            key_type, val_type = expected_type.__args__
            for k, v in value.items():
                # Validate key type
                validate_type(k, key_type, f"{field_path} (key: {k})")
                # Validate value type
                validate_type(v, val_type, f"{field_path}.{k}")
        return
    
    # Handle basic types
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Expected {expected_type.__name__}, got {type(value).__name__}",
            field_path
        )


def validate_data(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]], base_path: str = "") -> List[ValidationError]:
    """
    Validate data against a schema.
    
    Args:
        data: The data to validate
        schema: Dictionary mapping field names to type information
        base_path: Base path for error reporting
        
    Returns:
        List of ValidationError objects, empty if validation passed
    """
    errors = []
    
    # Check required fields
    for field_name, field_info in schema.items():
        if field_info.get("required", False) and field_name not in data:
            errors.append(ValidationError(
                f"Missing required field",
                f"{base_path}.{field_name}" if base_path else field_name
            ))
    
    # Check field types
    for field_name, field_value in data.items():
        if field_name in schema:
            field_info = schema[field_name]
            expected_type = field_info.get("type", Any)
            
            field_path = f"{base_path}.{field_name}" if base_path else field_name
            
            try:
                validate_type(field_value, expected_type, field_path)
            except ValidationError as e:
                errors.append(e)
    
    return errors


def validate_task_input(task_handler, input_data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate task input data against the handler's expected parameters.
    
    Args:
        task_handler: The function that will handle the task
        input_data: The input data to validate
        
    Returns:
        List of ValidationError objects, empty if validation passed
    """
    # Create schema from handler function
    schema = create_schema_from_type_hints(task_handler)
    
    # Validate the data
    return validate_data(input_data, schema)


def validate_task_output(output_data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate task output data against the standard output format.
    
    Args:
        output_data: The output data to validate
        
    Returns:
        List of ValidationError objects, empty if validation passed
    """
    # Define standard output schema
    schema = {
        "success": {
            "type": bool,
            "required": True
        },
        "result": {
            "type": Any,
            "required": False  # Not required if error is present
        },
        "response": {
            "type": Any,
            "required": False  # Not required if result or error is present
        },
        "error": {
            "type": str,
            "required": False  # Required if success is False
        },
        "error_type": {
            "type": str,
            "required": False  # Optional
        }
    }
    
    errors = validate_data(output_data, schema)
    
    # Check logical constraints
    if output_data.get("success") is False and "error" not in output_data:
        errors.append(ValidationError(
            "Field 'error' is required when 'success' is False",
            "error"
        ))
    
    if output_data.get("success") is True and "result" not in output_data and "response" not in output_data:
        errors.append(ValidationError(
            "Either 'result' or 'response' is required when 'success' is True",
            ""
        ))
    
    return errors


def format_validation_errors(errors: List[ValidationError]) -> str:
    """
    Format validation errors into a human-readable string.
    
    Args:
        errors: List of ValidationError objects
        
    Returns:
        Formatted error message
    """
    if not errors:
        return "No validation errors"
    
    error_messages = []
    for error in errors:
        if error.field_path:
            error_messages.append(f"- Field '{error.field_path}': {error.message}")
        else:
            error_messages.append(f"- {error.message}")
    
    return "\n".join(error_messages) 