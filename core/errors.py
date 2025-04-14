"""
Standardized error handling and reporting for the Dawn framework.

This module provides a consistent approach to error handling across the framework,
including standardized error codes, error response formats, and utilities for
error propagation and handling.
"""

import logging
import sys
import traceback
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, cast

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severity levels for errors in the framework."""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class ErrorCategory(Enum):
    """Categories of errors in the framework."""
    VALIDATION = "VALIDATION"  # Input/output validation errors
    EXECUTION = "EXECUTION"    # Errors during task/tool execution
    AUTHENTICATION = "AUTH"    # Authentication/authorization errors
    CONNECTION = "CONNECTION"  # Network/connection errors
    RESOURCE = "RESOURCE"      # Resource-related errors (not found, access denied)
    FRAMEWORK = "FRAMEWORK"    # Framework internal errors
    PLUGIN = "PLUGIN"          # Errors in plugin system
    UNKNOWN = "UNKNOWN"        # Uncategorized errors


class ErrorCode:
    """Standardized error codes for the Dawn framework.
    
    Format: <CATEGORY>_<DESCRIPTION>_<NUMBER>
    Example: VALIDATION_MISSING_FIELD_101
    """  # noqa: D202
    
    # Validation errors (100-199)
    VALIDATION_MISSING_FIELD = "VALIDATION_MISSING_FIELD_101"
    VALIDATION_INVALID_TYPE = "VALIDATION_INVALID_TYPE_102"
    VALIDATION_INVALID_FORMAT = "VALIDATION_INVALID_FORMAT_103"
    VALIDATION_INVALID_VALUE = "VALIDATION_INVALID_VALUE_104"
    VALIDATION_MISSING_DEPENDENCY = "VALIDATION_MISSING_DEPENDENCY_105"
    
    # Execution errors (200-299)
    EXECUTION_TASK_FAILED = "EXECUTION_TASK_FAILED_201"
    EXECUTION_TOOL_FAILED = "EXECUTION_TOOL_FAILED_202"
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT_203"
    EXECUTION_INTERRUPTED = "EXECUTION_INTERRUPTED_204"
    EXECUTION_MAX_RETRIES = "EXECUTION_MAX_RETRIES_205"
    
    # Authentication errors (300-399)
    AUTH_MISSING_CREDENTIALS = "AUTH_MISSING_CREDENTIALS_301"
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS_302"
    AUTH_EXPIRED_CREDENTIALS = "AUTH_EXPIRED_CREDENTIALS_303"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS_304"
    
    # Connection errors (400-499)
    CONNECTION_FAILED = "CONNECTION_FAILED_401"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT_402"
    CONNECTION_RATE_LIMIT = "CONNECTION_RATE_LIMIT_403"
    CONNECTION_API_ERROR = "CONNECTION_API_ERROR_404"
    
    # Resource errors (500-599)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND_501"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS_502"
    RESOURCE_ACCESS_DENIED = "RESOURCE_ACCESS_DENIED_503"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE_504"
    
    # Framework errors (600-699)
    FRAMEWORK_INITIALIZATION_ERROR = "FRAMEWORK_INITIALIZATION_ERROR_601"
    FRAMEWORK_CONFIGURATION_ERROR = "FRAMEWORK_CONFIGURATION_ERROR_602"
    FRAMEWORK_WORKFLOW_ERROR = "FRAMEWORK_WORKFLOW_ERROR_603"
    FRAMEWORK_TASK_ERROR = "FRAMEWORK_TASK_ERROR_604"
    FRAMEWORK_ENGINE_ERROR = "FRAMEWORK_ENGINE_ERROR_605"
    
    # Plugin errors (700-799)
    PLUGIN_LOADING_ERROR = "PLUGIN_LOADING_ERROR_701"
    PLUGIN_EXECUTION_ERROR = "PLUGIN_EXECUTION_ERROR_702"
    PLUGIN_VALIDATION_ERROR = "PLUGIN_VALIDATION_ERROR_703"
    
    # Unknown/uncategorized errors (900-999)
    UNKNOWN_ERROR = "UNKNOWN_ERROR_901"

    TASK_EXECUTION_FAILED = "TASK_EXECUTION_FAILED_201"


class DawnError(Exception):
    """Base exception class for all framework errors."""  # noqa: D202
    
    def __init__(
        self, 
        message: Optional[str] = None, 
        error_code: str = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        cause: Optional[Exception] = None,
        **kwargs
    ):
        """
        Initialize a new DawnError.
        
        Args:
            message: Human-readable error message (optional if using template)
            error_code: Error code from ErrorCode class
            details: Additional error details
            severity: Error severity level 
            cause: Original exception that caused this error
            **kwargs: Additional context variables for message template
        """
        self.error_code = error_code
        self.details = details or {}
        
        # Add any additional kwargs to details
        self.details.update({k: v for k, v in kwargs.items() 
                            if k not in ["message", "error_code", "details", "severity", "cause"]})
        
        # Generate the message if not provided using the template system
        if message is None:
            message = get_error_message(error_code, **self.details)
            
        self.message = message
        self.severity = severity
        self.cause = cause
        self.timestamp = datetime.now().isoformat()
        
        # Call the parent constructor with the message
        super().__init__(self.message)
        
        # Extract useful info from cause if available
        if cause:
            self.details["cause_type"] = type(cause).__name__
            self.details["cause_message"] = str(cause)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a standardized dictionary format."""
        result = {
            "error": self.message,
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "severity": self.severity.name,
        }
        
        if self.details:
            result["details"] = self.details
            
        if self.cause:
            result["cause"] = {
                "type": type(self.cause).__name__,
                "message": str(self.cause)
            }
            
        return result
    
    def get_traceback(self) -> str:
        """Get the formatted traceback for this error."""
        if self.cause:
            # If we have a cause, provide its traceback
            return ''.join(traceback.format_exception(
                type(self.cause), 
                self.cause, 
                self.cause.__traceback__
            ))
        return ''.join(traceback.format_exception(
            type(self), 
            self, 
            self.__traceback__
        ))
    
    def log(self, include_traceback: bool = True) -> None:
        """Log this error with appropriate severity level."""
        log_method = {
            ErrorSeverity.DEBUG: logger.debug,
            ErrorSeverity.INFO: logger.info,
            ErrorSeverity.WARNING: logger.warning,
            ErrorSeverity.ERROR: logger.error,
            ErrorSeverity.CRITICAL: logger.critical
        }.get(self.severity, logger.error)
        
        log_message = f"{self.error_code}: {self.message}"
        
        if include_traceback:
            log_method(log_message, exc_info=True)
        else:
            log_method(log_message)


# Custom exception for tool failures
class ToolExecutionError(DawnError):
    """Exception for errors during tool execution."""  # noqa: D202
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        **kwargs
    ):
        """Initialize a new ToolExecutionError.
        
        Args:
            message: Human-readable error message
            tool_name: Name of the tool that failed
            **kwargs: Additional keyword arguments to pass to DawnError
        """
        details = kwargs.pop("details", {})
        if tool_name:
            details["tool_name"] = tool_name
            
        super().__init__(
            message=message,
            error_code=kwargs.pop("error_code", ErrorCode.EXECUTION_TOOL_FAILED),
            details=details,
            severity=kwargs.pop("severity", ErrorSeverity.ERROR),
            **kwargs
        )


# Specific exception types for different error categories
class ValidationError(DawnError):
    """Error raised when validation fails."""  # noqa: D202

    def __init__(
        self, 
        message: Optional[str] = None, 
        error_code: str = ErrorCode.VALIDATION_MISSING_FIELD,
        field_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        received_value: Optional[Any] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a new ValidationError.
        
        Args:
            message: Human-readable error message (optional)
            error_code: Error code from ErrorCode class
            field_name: Name of the field that failed validation
            expected_type: Expected data type for the field
            received_value: Value that was received
            reason: Specific reason for validation failure
            **kwargs: Additional context variables for message template
        """
        details = kwargs.pop("details", {})
        
        # Add standard validation fields to details
        if field_name:
            details["field_name"] = field_name
        if expected_type:
            details["expected_type"] = expected_type
        if received_value:
            details["received_value"] = received_value
        if reason:
            details["reason"] = reason
            
        # Call DawnError constructor with details
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            severity=ErrorSeverity.WARNING,
            **kwargs
        )


class ExecutionError(DawnError):
    """Error raised during task or tool execution."""  # noqa: D202

    def __init__(
        self, 
        message: Optional[str] = None, 
        error_code: str = ErrorCode.EXECUTION_TASK_FAILED,
        task_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a new ExecutionError.
        
        Args:
            message: Human-readable error message (optional)
            error_code: Error code from ErrorCode class
            task_id: ID of the task that failed
            tool_name: Name of the tool that failed
            reason: Specific reason for the execution failure
            **kwargs: Additional context variables for message template
        """
        details = kwargs.pop("details", {})
        
        # Add standard execution fields to details
        if task_id:
            details["task_id"] = task_id
        if tool_name:
            details["tool_name"] = tool_name
        if reason:
            details["reason"] = reason
            
        # Call DawnError constructor with details
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class ConnectionError(DawnError):
    """Error raised during API or network connections."""  # noqa: D202

    def __init__(
        self, 
        message: Optional[str] = None, 
        error_code: str = ErrorCode.CONNECTION_FAILED,
        service_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        reason: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize a new ConnectionError.
        
        Args:
            message: Human-readable error message (optional)
            error_code: Error code from ErrorCode class
            service_name: Name of the service connection failed to
            retry_after: Seconds to wait before retrying
            reason: Specific reason for the connection failure
            timeout: Timeout duration in seconds
            **kwargs: Additional context variables for message template
        """
        details = kwargs.pop("details", {})
        
        # Add standard connection fields to details
        if service_name:
            details["service_name"] = service_name
        if retry_after:
            details["retry_after"] = retry_after
        if reason:
            details["reason"] = reason
        if timeout:
            details["timeout"] = timeout
            
        # Call DawnError constructor with details
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class ResourceError(DawnError):
    """Error raised when accessing resources."""  # noqa: D202

    def __init__(
        self, 
        message: Optional[str] = None, 
        error_code: str = ErrorCode.RESOURCE_NOT_FOUND,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a new ResourceError.
        
        Args:
            message: Human-readable error message (optional)
            error_code: Error code from ErrorCode class
            resource_type: Type of resource
            resource_id: Identifier for the resource
            reason: Specific reason for the resource error
            **kwargs: Additional context variables for message template
        """
        details = kwargs.pop("details", {})
        
        # Add standard resource fields to details
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        if reason:
            details["reason"] = reason
            
        # Call DawnError constructor with details
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


# --- Response Creation Utilities ---

def create_error_response(
    message: Optional[str] = None,
    error_code: str = ErrorCode.UNKNOWN_ERROR,
    details: Optional[Dict[str, Any]] = None,
    status_code: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a standardized error response dictionary.
    
    Args:
        message: Human-readable error message (optional if using template)
        error_code: Error code from ErrorCode class
        details: Additional error details 
        status_code: Optional HTTP status code
        **kwargs: Additional context variables for message template
        
    Returns:
        Standardized error response dictionary
    """
    details = details or {}
    
    # Update details with any provided kwargs
    details.update({k: v for k, v in kwargs.items() if k not in ['message', 'error_code', 'details', 'status_code']})
    
    # Generate the message if not provided using the template system
    if message is None:
        message = get_error_message(error_code, **details)
    
    response = {
        "success": False,
        "status": "error",
        "error": message,
        "error_code": error_code,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        response["error_details"] = details
        
    if status_code:
        response["status_code"] = status_code
        
    return response


def create_success_response(
    result: Any,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized success response dictionary.
    
    Args:
        result: The result data
        message: Optional success message
        metadata: Optional metadata about the operation
        
    Returns:
        Standardized success response dictionary
    """
    response = {
        "success": True,
        "status": "success",
        "result": result,
        "response": result,  # For backward compatibility
        "timestamp": datetime.now().isoformat()
    }
    
    if message:
        response["message"] = message
        
    if metadata:
        response["metadata"] = metadata
        
    return response


def create_warning_response(
    result: Any,
    warning: str,
    warning_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized warning response dictionary.
    
    This is for cases where the operation succeeded but with warnings.
    
    Args:
        result: The result data
        warning: Human-readable warning message
        warning_code: Optional warning code
        details: Additional warning details
        
    Returns:
        Standardized warning response dictionary
    """
    response = {
        "success": True,
        "status": "warning",
        "result": result,
        "response": result,  # For backward compatibility
        "warning": warning,
        "timestamp": datetime.now().isoformat()
    }
    
    if warning_code:
        response["warning_code"] = warning_code
        
    if details:
        response["warning_details"] = details
        
    return response


# --- Error Handling Wrapper ---

def safe_execute(
    func: callable,
    error_map: Optional[Dict[type, str]] = None,
    default_code: str = ErrorCode.UNKNOWN_ERROR,
    log_errors: bool = True
) -> callable:
    """Decorator for safely executing functions with standardized error handling.
    
    Args:
        func: The function to wrap
        error_map: Mapping from exception types to error codes
        default_code: Default error code for unmapped exceptions
        log_errors: Whether to log errors
        
    Returns:
        Wrapped function that returns standardized response dictionaries
    """
    error_map = error_map or {}
    
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If the result is already a response dictionary, return it
            if isinstance(result, dict) and "success" in result:
                # Ensure it has the standard fields
                if "status" not in result:
                    result["status"] = "success" if result["success"] else "error"
                
                if "timestamp" not in result:
                    result["timestamp"] = datetime.now().isoformat()
                    
                return result
            
            # Otherwise, wrap the result in a success response
            return create_success_response(result)
        
        except Exception as e:
            # Map the exception to an error code
            error_code = default_code
            for exc_type, code in error_map.items():
                if isinstance(e, exc_type):
                    error_code = code
                    break
            
            # Log the error if requested
            if log_errors:
                logger.error(
                    f"Error executing {func.__name__}: {str(e)}",
                    exc_info=True
                )
            
            # Create the error response
            if isinstance(e, DawnError):
                # Use the DawnError's fields
                return create_error_response(
                    message=e.message,
                    error_code=e.error_code,
                    details=e.details
                )
            else:
                # Create a new error response
                return create_error_response(
                    message=str(e),
                    error_code=error_code,
                    details={"exception_type": type(e).__name__}
                )
    
    return wrapper


# --- Exit Code Handling ---

class ExitCodes:
    """Standard exit codes for Dawn framework applications."""  # noqa: D202
    
    # Success
    SUCCESS = 0
    
    # General errors
    GENERAL_ERROR = 1
    
    # Configuration errors
    CONFIG_ERROR = 2
    MISSING_ENV_VARS = 3
    INVALID_CONFIG = 4
    
    # Resource errors
    RESOURCE_ERROR = 5
    FILE_NOT_FOUND = 6
    PERMISSION_DENIED = 7
    
    # Workflow errors
    WORKFLOW_ERROR = 10
    TASK_FAILED = 11
    
    # Connection errors
    CONNECTION_ERROR = 20
    API_ERROR = 21
    TIMEOUT_ERROR = 22
    
    # User input errors
    USER_INPUT_ERROR = 30
    MISSING_ARGUMENT = 31
    INVALID_ARGUMENT = 32
    
    # Internal errors
    INTERNAL_ERROR = 40
    UNHANDLED_EXCEPTION = 41

    @classmethod
    def get_description(cls, exit_code: int) -> str:
        """Get a human-readable description for an exit code."""
        descriptions = {
            cls.SUCCESS: "Success - Operation completed successfully",
            cls.GENERAL_ERROR: "General Error - An unspecified error occurred",
            cls.CONFIG_ERROR: "Configuration Error - Error in configuration",
            cls.MISSING_ENV_VARS: "Missing Environment Variables - Required environment variables are missing",
            cls.INVALID_CONFIG: "Invalid Configuration - Configuration is invalid",
            cls.RESOURCE_ERROR: "Resource Error - Error accessing a resource",
            cls.FILE_NOT_FOUND: "File Not Found - Required file was not found",
            cls.PERMISSION_DENIED: "Permission Denied - Access to a resource was denied",
            cls.WORKFLOW_ERROR: "Workflow Error - Error in workflow execution",
            cls.TASK_FAILED: "Task Failed - A task in the workflow failed",
            cls.CONNECTION_ERROR: "Connection Error - Error connecting to a service",
            cls.API_ERROR: "API Error - Error from an external API",
            cls.TIMEOUT_ERROR: "Timeout Error - Operation timed out",
            cls.USER_INPUT_ERROR: "User Input Error - Error in user input",
            cls.MISSING_ARGUMENT: "Missing Argument - Required argument is missing",
            cls.INVALID_ARGUMENT: "Invalid Argument - Argument is invalid",
            cls.INTERNAL_ERROR: "Internal Error - Internal framework error",
            cls.UNHANDLED_EXCEPTION: "Unhandled Exception - An unhandled exception occurred"
        }
        return descriptions.get(exit_code, f"Unknown Exit Code: {exit_code}")


def handle_exit(
    exception: Optional[Exception] = None,
    exit_code: int = ExitCodes.GENERAL_ERROR,
    message: Optional[str] = None,
    log_exception: bool = True
) -> int:
    """Handle exit with proper logging and clean exit code.
    
    Args:
        exception: Exception that caused the exit, if any
        exit_code: Exit code to use
        message: Message to display, if not using the exception message
        log_exception: Whether to log the exception
        
    Returns:
        Exit code that can be passed to sys.exit()
    """
    # Use exception message if no message provided
    if message is None and exception is not None:
        message = str(exception)
    elif message is None:
        message = "Exiting with code {exit_code}: {ExitCodes.get_description(exit_code)}"
    
    # Log the exception if requested
    if log_exception and exception is not None:
        logger.error(message, exc_info=True)
    elif message:
        log_level = logging.ERROR if exit_code != ExitCodes.SUCCESS else logging.INFO
        logger.log(log_level, message)
    
    return exit_code


def main_wrapper(func):
    """Decorator for wrapping main functions with standardized exit handling.
    
    This ensures that all exceptions are caught and proper exit codes are returned.
    
    Args:
        func: The main function to wrap
        
    Returns:
        Wrapped function that returns an exit code
    """
    def wrapper(*args, **kwargs):
        try:
            # Call the main function
            result = func(*args, **kwargs)
            
            # If the result is an integer, use it as the exit code
            if isinstance(result, int):
                return result
            
            # Otherwise, assume success
            return ExitCodes.SUCCESS
        
        except ValidationError as e:
            return handle_exit(
                exception=e,
                exit_code=ExitCodes.USER_INPUT_ERROR,
                message=f"Validation error: {e.message}"
            )
        
        except ResourceError as e:
            if ErrorCode.RESOURCE_NOT_FOUND in e.error_code:
                return handle_exit(
                    exception=e,
                    exit_code=ExitCodes.FILE_NOT_FOUND,
                    message=f"Resource not found: {e.message}"
                )
            elif ErrorCode.RESOURCE_ACCESS_DENIED in e.error_code:
                return handle_exit(
                    exception=e,
                    exit_code=ExitCodes.PERMISSION_DENIED,
                    message=f"Permission denied: {e.message}"
                )
            else:
                return handle_exit(
                    exception=e,
                    exit_code=ExitCodes.RESOURCE_ERROR,
                    message=f"Resource error: {e.message}"
                )
        
        except ExecutionError as e:
            return handle_exit(
                exception=e,
                exit_code=ExitCodes.TASK_FAILED,
                message=f"Execution error: {e.message}"
            )
        
        except ConnectionError as e:
            if ErrorCode.CONNECTION_TIMEOUT in e.error_code:
                return handle_exit(
                    exception=e,
                    exit_code=ExitCodes.TIMEOUT_ERROR,
                    message=f"Connection timeout: {e.message}"
                )
            elif ErrorCode.CONNECTION_API_ERROR in e.error_code:
                return handle_exit(
                    exception=e,
                    exit_code=ExitCodes.API_ERROR,
                    message=f"API error: {e.message}"
                )
            else:
                return handle_exit(
                    exception=e,
                    exit_code=ExitCodes.CONNECTION_ERROR,
                    message=f"Connection error: {e.message}"
                )
        
        except DawnError as e:
            # Map other DawnError types to appropriate exit codes
            return handle_exit(
                exception=e,
                exit_code=ExitCodes.GENERAL_ERROR,
                message=f"Error: {e.message}"
            )
        
        except Exception as e:
            # Handle unexpected exceptions
            return handle_exit(
                exception=e,
                exit_code=ExitCodes.UNHANDLED_EXCEPTION,
                message=f"Unhandled exception: {str(e)}"
            )
    
    return wrapper


# --- Standardized Error Message Templates ---

ERROR_TEMPLATES = {
    # Validation errors
    ErrorCode.VALIDATION_MISSING_FIELD: "Required field '{field_name}' is missing",
    ErrorCode.VALIDATION_INVALID_TYPE: "Invalid type for field '{field_name}': expected {expected_type}, received {received_type}",
    ErrorCode.VALIDATION_INVALID_FORMAT: "Invalid format for field '{field_name}': {reason}",
    ErrorCode.VALIDATION_INVALID_VALUE: "Invalid value for field '{field_name}': {reason}",
    ErrorCode.VALIDATION_MISSING_DEPENDENCY: "Field '{field_name}' requires '{dependency_field}' to be present",
    
    # Execution errors
    ErrorCode.EXECUTION_TASK_FAILED: "Task '{task_id}' failed: {reason}",
    ErrorCode.EXECUTION_TOOL_FAILED: "Tool '{tool_name}' execution failed: {reason}",
    ErrorCode.EXECUTION_TIMEOUT: "Operation timed out after {timeout} seconds",
    ErrorCode.EXECUTION_INTERRUPTED: "Operation was interrupted: {reason}",
    ErrorCode.EXECUTION_MAX_RETRIES: "Maximum retries ({max_retries}) exceeded for '{resource_name}'",
    
    # Authentication errors
    ErrorCode.AUTH_MISSING_CREDENTIALS: "Missing credentials for '{service_name}'",
    ErrorCode.AUTH_INVALID_CREDENTIALS: "Invalid credentials for '{service_name}'",
    ErrorCode.AUTH_EXPIRED_CREDENTIALS: "Expired credentials for '{service_name}'",
    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS: "Insufficient permissions to access '{resource_name}'",
    
    # Connection errors
    ErrorCode.CONNECTION_FAILED: "Failed to connect to '{service_name}': {reason}",
    ErrorCode.CONNECTION_TIMEOUT: "Connection to '{service_name}' timed out after {timeout} seconds",
    ErrorCode.CONNECTION_RATE_LIMIT: "Rate limit exceeded for '{service_name}'. Try again in {retry_after} seconds",
    ErrorCode.CONNECTION_API_ERROR: "API error from '{service_name}': {reason}",
    
    # Resource errors
    ErrorCode.RESOURCE_NOT_FOUND: "Resource '{resource_type}' with ID '{resource_id}' not found",
    ErrorCode.RESOURCE_ALREADY_EXISTS: "Resource '{resource_type}' with ID '{resource_id}' already exists",
    ErrorCode.RESOURCE_ACCESS_DENIED: "Access denied to resource '{resource_type}' with ID '{resource_id}'",
    ErrorCode.RESOURCE_UNAVAILABLE: "Resource '{resource_type}' is currently unavailable: {reason}",
    
    # Framework errors
    ErrorCode.FRAMEWORK_INITIALIZATION_ERROR: "Framework initialization error: {reason}",
    ErrorCode.FRAMEWORK_CONFIGURATION_ERROR: "Configuration error: {reason}",
    ErrorCode.FRAMEWORK_WORKFLOW_ERROR: "Workflow error in '{workflow_id}': {reason}",
    ErrorCode.FRAMEWORK_TASK_ERROR: "Task error in '{task_id}': {reason}",
    ErrorCode.FRAMEWORK_ENGINE_ERROR: "Engine error: {reason}",
    
    # Plugin errors
    ErrorCode.PLUGIN_LOADING_ERROR: "Error loading plugin '{plugin_name}': {reason}",
    ErrorCode.PLUGIN_EXECUTION_ERROR: "Error executing plugin '{plugin_name}': {reason}",
    ErrorCode.PLUGIN_VALIDATION_ERROR: "Plugin validation error for '{plugin_name}': {reason}",
    
    # Unknown errors
    ErrorCode.UNKNOWN_ERROR: "An unexpected error occurred: {message}"
}

def get_error_message(error_code: str, **kwargs) -> str:
    """
    Generate a standardized error message based on error code and context.
    
    Args:
        error_code: Error code from ErrorCode class
        **kwargs: Context variables to format into the message template
        
    Returns:
        Standardized error message string
    """
    # Get the template for this error code
    template = ERROR_TEMPLATES.get(error_code, "Error: {message}")
    
    # For unknown error codes, if message isn't provided, create a generic one
    if error_code not in ERROR_TEMPLATES and "message" not in kwargs:
        kwargs["message"] = f"Error code {error_code}"
    
    # Attempt to format the template with the provided kwargs
    try:
        return template.format(**kwargs)
    except KeyError as e:
        # If missing required template variables, return a fallback message
        missing_key = str(e).strip("'")
        return f"Error {error_code}: Missing required context '{missing_key}' for error message"
    except Exception:
        # For any other formatting error, return the raw template
        return f"Error {error_code}: {template}"
