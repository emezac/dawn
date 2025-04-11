"""
Standardized error handling and response formatting for the Dawn framework.

This module provides a unified approach to error handling across the framework,
including standard error codes, response formatting, and utility functions.
"""

from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(Enum):
    """Standard error codes for the Dawn framework."""

    # Input validation errors (1000-1999)
    INVALID_INPUT = 1000
    MISSING_REQUIRED_FIELD = 1001
    TYPE_ERROR = 1002
    VALUE_ERROR = 1003

    # Resource errors (2000-2999)
    RESOURCE_NOT_FOUND = 2000
    RESOURCE_ALREADY_EXISTS = 2001
    RESOURCE_UNAVAILABLE = 2002
    PERMISSION_DENIED = 2003

    # Service errors (3000-3999)
    SERVICE_UNAVAILABLE = 3000
    SERVICE_TIMEOUT = 3001
    SERVICE_ERROR = 3002

    # Tool errors (4000-4999)
    TOOL_NOT_FOUND = 4000
    TOOL_EXECUTION_ERROR = 4001
    TOOL_TIMEOUT = 4002

    # Task errors (5000-5999)
    TASK_NOT_FOUND = 5000
    TASK_EXECUTION_ERROR = 5001
    TASK_DEPENDENCY_ERROR = 5002
    TASK_CONDITION_ERROR = 5003

    # Workflow errors (6000-6999)
    WORKFLOW_EXECUTION_ERROR = 6000
    WORKFLOW_VALIDATION_ERROR = 6001
    WORKFLOW_NOT_FOUND = 6002


def create_error_response(
    error_code: ErrorCode, message: str, details: Optional[Dict[str, Any]] = None, trace: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        error_code: The error code from the ErrorCode enum
        message: A human-readable error message
        details: Optional dictionary with additional error details
        trace: Optional error traceback or stack trace

    Returns:
        A dictionary with the standardized error response format
    """
    response = {
        "status": "error",
        "success": False,
        "error": {"code": error_code.value, "type": error_code.name, "message": message},
    }

    if details:
        response["error"]["details"] = details

    if trace:
        response["error"]["trace"] = trace

    return response


def create_success_response(
    data: Optional[Any] = None, message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        data: The main response data
        message: Optional success message
        metadata: Optional metadata about the response

    Returns:
        A dictionary with the standardized success response format
    """
    response = {"status": "success", "success": True}

    if data is not None:
        response["data"] = data

    if message:
        response["message"] = message

    if metadata:
        response["metadata"] = metadata

    return response


def is_success_response(response: Dict[str, Any]) -> bool:
    """
    Check if a response is a success response.

    Args:
        response: The response to check

    Returns:
        True if the response is a success response, False otherwise
    """
    return response.get("success", False) is True


def is_error_response(response: Dict[str, Any]) -> bool:
    """
    Check if a response is an error response.

    Args:
        response: The response to check

    Returns:
        True if the response is an error response, False otherwise
    """
    return response.get("success", True) is False


class DawnError(Exception):
    """Base exception class for Dawn framework errors."""

    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a new DawnError.

        Args:
            message: A human-readable error message
            error_code: The error code from the ErrorCode enum
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_response(self, include_trace: bool = True) -> Dict[str, Any]:
        """
        Convert the exception to a standardized error response.

        Args:
            include_trace: Whether to include the stack trace in the response

        Returns:
            A dictionary with the standardized error response format
        """
        import traceback

        trace = traceback.format_exc() if include_trace else None
        return create_error_response(self.error_code, self.message, self.details, trace)


class InputValidationError(DawnError):
    """Error raised when input validation fails."""

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None, error_code: ErrorCode = ErrorCode.INVALID_INPUT
    ):
        super().__init__(message, error_code, details)


class ResourceError(DawnError):
    """Error raised when there is a problem with a resource."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
    ):
        super().__init__(message, error_code, details)


class ServiceError(DawnError):
    """Error raised when there is a problem with a service."""

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None, error_code: ErrorCode = ErrorCode.SERVICE_ERROR
    ):
        super().__init__(message, error_code, details)


class ToolError(DawnError):
    """Error raised when there is a problem with a tool."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.TOOL_EXECUTION_ERROR,
    ):
        super().__init__(message, error_code, details)


class TaskError(DawnError):
    """Error raised when there is a problem with a task."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.TASK_EXECUTION_ERROR,
    ):
        super().__init__(message, error_code, details)


class WorkflowError(DawnError):
    """Error raised when there is a problem with a workflow."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.WORKFLOW_EXECUTION_ERROR,
    ):
        super().__init__(message, error_code, details)
