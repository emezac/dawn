"""
Tool response formatting utilities for Dawn framework.

This module provides utilities to ensure all tools in the Dawn framework
return responses in a standardized format, leveraging the error handling
infrastructure defined in core/errors.py.
"""

import functools
import inspect
from datetime import datetime
from typing import Any, Callable, Dict, Optional, TypeVar, cast

# Avoid circular imports by importing only what we need from core.errors
# and using a delayed import pattern where needed
from core.errors import (
    ErrorCode,
    ValidationError, 
    ExecutionError,
    ConnectionError,
    ResourceError,
    DawnError,
    create_error_response,
    create_success_response,
    create_warning_response
)

# Define type variables for callable signatures
F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R')  # Return type


def format_tool_response(tool_result: Any) -> Dict[str, Any]:
    """
    Format a tool's raw result into the standardized response format.
    
    If the result is already in the standard format, it is returned as is.
    Otherwise, it is wrapped in a success response.
    
    Args:
        tool_result: The raw result from a tool function
        
    Returns:
        A standardized response dictionary
    """
    # If the result is already a response dictionary, ensure it has standard fields
    if isinstance(tool_result, dict) and "success" in tool_result:
        response = tool_result.copy()
        
        # Ensure it has a status field
        if "status" not in response:
            response["status"] = "success" if response["success"] else "error"
            
        # Ensure it has a timestamp
        if "timestamp" not in response:
            response["timestamp"] = datetime.now().isoformat()
            
        # For error responses, ensure error_code is present
        if not response["success"] and "error_code" not in response:
            response["error_code"] = ErrorCode.UNKNOWN_ERROR
            
        # Ensure both 'result' and 'response' fields are present for backward compatibility
        if "result" in response and "response" not in response:
            response["response"] = response["result"]
        elif "response" in response and "result" not in response:
            response["result"] = response["response"]
            
        return response
    
    # Otherwise, wrap the result in a success response
    return create_success_response(result=tool_result)


def standardize_tool_response(tool_func: F) -> F:
    """
    Decorator to ensure a tool function returns a standardized response.
    
    This decorator wraps a tool function to handle exceptions and ensure the
    response follows the standard format. It is similar to safe_execute but
    specifically designed for tool handlers.
    
    Args:
        tool_func: The tool function to wrap
        
    Returns:
        Wrapped function that returns standardized response dictionaries
    """
    @functools.wraps(tool_func)
    def wrapper(*args, **kwargs):
        try:
            # Call the original function
            result = tool_func(*args, **kwargs)
            
            # Format the result
            return format_tool_response(result)
            
        except ValidationError as e:
            # Handle validation errors
            return create_error_response(
                message=e.message,
                error_code=e.error_code,
                details=e.details
            )
            
        except ExecutionError as e:
            # Handle execution errors
            return create_error_response(
                message=e.message,
                error_code=e.error_code,
                details=e.details
            )
            
        except ConnectionError as e:
            # Handle connection errors
            return create_error_response(
                message=e.message,
                error_code=e.error_code,
                details=e.details
            )
            
        except ResourceError as e:
            # Handle resource errors
            return create_error_response(
                message=e.message,
                error_code=e.error_code,
                details=e.details
            )
            
        except DawnError as e:
            # Handle generic Dawn errors
            return create_error_response(
                message=e.message,
                error_code=e.error_code,
                details=e.details
            )
            
        except Exception as e:
            # Handle unexpected exceptions
            return create_error_response(
                message=str(e),
                error_code=ErrorCode.UNKNOWN_ERROR,
                details={"exception_type": type(e).__name__}
            )
    
    return cast(F, wrapper)


def validate_tool_input(
    schema: Dict[str, Any],
    required_fields: Optional[list] = None
) -> Callable[[F], F]:
    """
    Decorator to validate tool input against a schema.
    
    Args:
        schema: Dictionary describing expected input fields and types
        required_fields: List of field names that are required
        
    Returns:
        Decorator function that validates input and formats responses
    """
    def decorator(tool_func: F) -> F:
        @functools.wraps(tool_func)
        def wrapper(*args, **kwargs):
            # Extract input_data from positional or keyword arguments
            input_data = None
            
            # If called with positional arguments, assume first is input_data
            if args and len(args) > 0:
                input_data = args[0]
            # If called with keyword arguments, look for input_data
            elif "input_data" in kwargs:
                input_data = kwargs["input_data"]
                
            # If we couldn't find input_data, raise an error
            if input_data is None:
                return create_error_response(
                    error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                    field_name="input_data"
                )
                
            # Validate against required fields
            if required_fields:
                for field in required_fields:
                    if field not in input_data:
                        return create_error_response(
                            error_code=ErrorCode.VALIDATION_MISSING_FIELD,
                            field_name=field
                        )
            
            # Validate against schema
            for field_name, field_info in schema.items():
                if field_name in input_data:
                    # Skip None values if they are allowed
                    if input_data[field_name] is None and field_info.get("allow_none", False):
                        continue
                        
                    # Check type if specified
                    if "type" in field_info:
                        expected_type = field_info["type"]
                        if not isinstance(input_data[field_name], expected_type):
                            return create_error_response(
                                error_code=ErrorCode.VALIDATION_INVALID_TYPE,
                                field_name=field_name,
                                expected_type=expected_type.__name__,
                                received_type=type(input_data[field_name]).__name__
                            )
                    
                    # Check enum values if specified
                    if "enum" in field_info and input_data[field_name] not in field_info["enum"]:
                        return create_error_response(
                            error_code=ErrorCode.VALIDATION_INVALID_VALUE,
                            field_name=field_name,
                            reason="value must be one of the allowed options",
                            allowed_values=field_info["enum"],
                            received_value=input_data[field_name]
                        )
            
            # If validation passes, call the original function with standardized response
            return standardize_tool_response(tool_func)(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator


def with_warning(
    result: Any, 
    warning: str,
    warning_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Helper function to create a success response with a warning.
    
    Args:
        result: The result data
        warning: Warning message
        warning_code: Optional warning code
        details: Additional warning details
        
    Returns:
        Standardized warning response dictionary
    """
    return create_warning_response(
        result=result,
        warning=warning,
        warning_code=warning_code,
        details=details
    ) 