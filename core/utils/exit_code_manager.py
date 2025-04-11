"""
Exit Code Manager

Utilities to standardize exit code handling across the framework.
"""

import sys
import logging
import traceback
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

# Configure logger
logger = logging.getLogger("dawn.exit_code_manager")

# Define standard exit codes as an Enum for better type hinting and documentation
class ExitCode(Enum):
    """Standard exit codes used throughout the Dawn framework."""  # noqa: D202
    
    SUCCESS = 0
    """Workflow or process completed successfully."""  # noqa: D202
    
    GENERAL_ERROR = 1
    """General unexpected error occurred."""  # noqa: D202
    
    CONFIG_ERROR = 2
    """Configuration error (missing API keys, invalid settings, etc.)."""  # noqa: D202
    
    RESOURCE_ERROR = 3
    """Resource error (missing tools, vector store creation failure, etc.)."""  # noqa: D202
    
    EXECUTION_ERROR = 4
    """Execution error (task failures, workflow routing issues, etc.)."""  # noqa: D202
    
    INPUT_ERROR = 5
    """Input validation error (invalid input data format, missing required fields, etc.)."""  # noqa: D202


# Type variable for the return type of the wrapped function
T = TypeVar('T')


def exit_on_error(
    error_type: Union[Type[Exception], tuple[Type[Exception], ...]], 
    exit_code: ExitCode,
    error_message: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that catches specified exceptions and exits with the given exit code.
    
    Args:
        error_type: Exception type or tuple of exception types to catch
        exit_code: ExitCode enum value to use when exiting
        error_message: Optional message to log before exiting (default: use exception message)
        
    Returns:
        A decorator function that wraps the target function
    
    Example:
        @exit_on_error(ValueError, ExitCode.INPUT_ERROR, "Invalid input provided")
        def process_data(data):
            # process data
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except error_type as e:
                message = error_message or str(e)
                logger.error(f"{message}: {str(e)}")
                sys.exit(exit_code.value)
        return wrapper
    return decorator


def run_with_standard_exceptions(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that handles common exceptions with appropriate exit codes.
    
    This decorator wraps a function with standardized exception handling that maps
    common exception types to our standard exit codes.
    
    Args:
        func: The function to wrap
        
    Returns:
        A wrapped function with standardized exception handling
        
    Example:
        @run_with_standard_exceptions
        def main():
            # main function logic
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            # Run the wrapped function
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            # Handle user interruption
            logger.info("Process interrupted by user")
            sys.exit(130)  # Standard exit code for SIGINT
        except (FileNotFoundError, PermissionError) as e:
            # Handle resource access errors
            logger.error(f"Resource error: {str(e)}")
            sys.exit(ExitCode.RESOURCE_ERROR.value)
        except (ValueError, TypeError) as e:
            # Handle input validation errors
            logger.error(f"Input error: {str(e)}")
            sys.exit(ExitCode.INPUT_ERROR.value)
        except Exception as e:
            # Handle all other exceptions as general errors
            logger.error(f"Unexpected error: {str(e)}")
            traceback.print_exc()
            sys.exit(ExitCode.GENERAL_ERROR.value)
    return wrapper


def wrap_main_function(func: Callable[..., Any]) -> Callable[..., None]:
    """
    Wrapper for main functions in workflow scripts to standardize exit code handling.
    
    This wrapper:
    1. Sets up standard exception handling with appropriate exit codes
    2. Ensures success exit code (0) when the function completes normally
    3. Provides consistent logging of errors
    
    Args:
        func: The main function to wrap
        
    Returns:
        A wrapped function that handles exit codes consistently
        
    Example:
        if __name__ == "__main__":
            wrap_main_function(main)()
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        try:
            # Run the main function
            result = func(*args, **kwargs)
            
            # If the function returned a status dict, check for errors
            if isinstance(result, dict) and 'success' in result:
                if not result['success']:
                    error_message = result.get('error', 'Unknown error')
                    error_code = ExitCode.EXECUTION_ERROR
                    
                    # Check for specific error types in the result
                    error_type = result.get('error_type')
                    if error_type == 'config':
                        error_code = ExitCode.CONFIG_ERROR
                    elif error_type == 'resource':
                        error_code = ExitCode.RESOURCE_ERROR
                    elif error_type == 'input':
                        error_code = ExitCode.INPUT_ERROR
                    
                    logger.error(f"Execution failed: {error_message}")
                    sys.exit(error_code.value)
                else:
                    # Function succeeded
                    sys.exit(ExitCode.SUCCESS.value)
            else:
                # No status returned, assume success
                sys.exit(ExitCode.SUCCESS.value)
                
        except KeyboardInterrupt:
            # Handle user interruption
            logger.info("Process interrupted by user")
            sys.exit(130)  # Standard exit code for SIGINT
        except Exception as e:
            # Catch any unhandled exceptions
            logger.error(f"Unhandled error in main function: {str(e)}")
            traceback.print_exc()
            sys.exit(ExitCode.GENERAL_ERROR.value)
    
    return wrapper


def map_exception_to_exit_code(exception: Exception) -> ExitCode:
    """
    Maps exception types to standard exit codes.
    
    Args:
        exception: The exception to map
        
    Returns:
        The appropriate ExitCode enum value
    """
    if isinstance(exception, (ValueError, TypeError)):
        return ExitCode.INPUT_ERROR
    elif isinstance(exception, (FileNotFoundError, PermissionError)):
        return ExitCode.RESOURCE_ERROR
    elif isinstance(exception, (ImportError, ModuleNotFoundError)):
        return ExitCode.CONFIG_ERROR
    else:
        return ExitCode.GENERAL_ERROR


def exit_with_error(
    message: str, 
    error_code: ExitCode = ExitCode.GENERAL_ERROR,
    exception: Optional[Exception] = None
) -> None:
    """
    Logs an error message and exits with the specified exit code.
    
    Args:
        message: Error message to log
        error_code: ExitCode enum value to use (default: GENERAL_ERROR)
        exception: Optional exception to include in the log
        
    Example:
        if not api_key:
            exit_with_error("API key is required", ExitCode.CONFIG_ERROR)
    """
    if exception:
        logger.error(f"{message}: {str(exception)}")
        if error_code == ExitCode.GENERAL_ERROR:
            traceback.print_exc()
    else:
        logger.error(message)
    
    sys.exit(error_code.value) 