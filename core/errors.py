"""
Core error handling system for the Dawn framework.

This module provides a standardized approach to error handling across the Dawn framework,
including exception classes, error codes, and utility functions for creating error responses.
"""

import traceback
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, Union


class ErrorCode(Enum):
    """
    Error codes for the Dawn framework, organized by category.

    Each error code is a unique integer that identifies a specific error type.
    Error codes are grouped by category:
    - 1000-1999: Input validation errors
    - 2000-2999: Resource errors
    - 3000-3999: Service errors
    - 4000-4999: Tool errors
    - 5000-5999: Task errors
    - 6000-6999: Workflow errors
    - 9000-9999: Generic errors
    """

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

    # Tool errors (4000-4999)
    TOOL_EXECUTION_ERROR = 4000
    TOOL_INITIALIZATION_ERROR = 4001

    # Task errors (5000-5999)
    TASK_EXECUTION_ERROR = 5000
    TASK_INITIALIZATION_ERROR = 5001

    # Workflow errors (6000-6999)
    WORKFLOW_EXECUTION_ERROR = 6000
    WORKFLOW_INITIALIZATION_ERROR = 6001

    # Generic errors (9000-9999)
    UNEXPECTED_ERROR = 9000
    INTERNAL_ERROR = 9001
    NOT_IMPLEMENTED = 9002
    VALUE_ERROR = 9003


class DawnError(Exception):
    """
    Base class for all Dawn framework exceptions.

    This class provides common functionality for all Dawn errors,
    including conversion to a standardized error response format.
    """

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None, error_code: ErrorCode = ErrorCode.UNEXPECTED_ERROR
    ):
        """
        Initialize a new DawnError.

        Args:
            message: Human-readable error message
            details: Additional details about the error (optional)
            error_code: The error code enum value (default: UNEXPECTED_ERROR)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = error_code
        self.traceback = traceback.format_exc() if traceback.format_exc() != "NoneType: None\n" else None

    def to_response(self) -> Dict[str, Any]:
        """
        Convert this error to a standardized response dictionary.

        Returns:
            A dictionary with error details that can be serialized to JSON
        """
        return create_error_response(
            code=self.error_code, message=self.message, details=self.details, trace=self.traceback
        )


class InputValidationError(DawnError):
    """
    Raised when input validation fails.

    Used when user or system input does not meet the required format or constraints.
    """

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None, error_code: ErrorCode = ErrorCode.INVALID_INPUT
    ):
        super().__init__(message, details, error_code)


class ResourceError(DawnError):
    """
    Raised when there's an issue with a resource.

    Used for errors related to files, databases, or other resources.
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
    ):
        super().__init__(message, details, error_code)


class ServiceError(DawnError):
    """
    Raised when there's an issue with a service.

    Used for errors related to external APIs, services, or dependencies.
    """

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None, error_code: ErrorCode = ErrorCode.SERVICE_ERROR
    ):
        super().__init__(message, details, error_code)


class ToolError(DawnError):
    """
    Raised when there's an issue with a tool.

    Used for errors specific to tool execution or initialization.
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.TOOL_EXECUTION_ERROR,
    ):
        super().__init__(message, details, error_code)


class TaskError(DawnError):
    """
    Raised when there's an issue with a task.

    Used for errors specific to task execution or initialization.
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.TASK_EXECUTION_ERROR,
    ):
        super().__init__(message, details, error_code)


class WorkflowError(DawnError):
    """
    Raised when there's an issue with a workflow.

    Used for errors specific to workflow execution or initialization.
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.WORKFLOW_EXECUTION_ERROR,
    ):
        super().__init__(message, details, error_code)


def create_error_response(
    code: ErrorCode, message: str, details: Optional[Dict[str, Any]] = None, trace: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        code: The error code enum value
        message: Human-readable error message
        details: Additional details about the error (optional)
        trace: Exception traceback (optional)

    Returns:
        A dictionary with error details that can be serialized to JSON
    """
    response = {
        "error": {
            "code": code.value,
            "type": code.name,
            "message": message,
        }
    }

    if details:
        response["error"]["details"] = details

    if trace:
        response["error"]["trace"] = trace

    return response


def create_success_response(
    data: Any, message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        data: The response data
        message: An optional message about the success (optional)
        metadata: Additional metadata about the response (optional)

    Returns:
        A dictionary with success details that can be serialized to JSON
    """
    response = {"data": data}

    if message:
        response["message"] = message

    if metadata:
        response["metadata"] = metadata

    return response


def is_error_response(response: Dict[str, Any]) -> bool:
    """
    Check if the response is an error response.

    Args:
        response: The response to check

    Returns:
        True if the response is an error response, False otherwise
    """
    return "error" in response


def is_success_response(response: Dict[str, Any]) -> bool:
    """
    Check if the response is a success response.

    Args:
        response: The response to check

    Returns:
        True if the response is a success response, False otherwise
    """
    return "data" in response


T = TypeVar("T")


def safe_execute(func: Callable[..., T], *args, **kwargs) -> Union[T, Dict[str, Any]]:
    """
    Execute a function and return its result or an error response if it fails.

    Args:
        func: The function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Either the function's return value or an error response dictionary
    """
    try:
        return func(*args, **kwargs)
    except DawnError as e:
        return e.to_response()
    except Exception as e:
        return create_error_response(
            ErrorCode.UNEXPECTED_ERROR, str(e), {"exception_type": type(e).__name__}, traceback.format_exc()
        )


__all__ = [
    "ErrorCode",
    "DawnError",
    "InputValidationError",
    "ResourceError",
    "ServiceError",
    "ToolError",
    "TaskError",
    "WorkflowError",
    "create_error_response",
    "create_success_response",
    "is_error_response",
    "is_success_response",
    "safe_execute",
]
