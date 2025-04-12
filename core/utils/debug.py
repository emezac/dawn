#!/usr/bin/env python3
"""
Debug utilities for the Dawn Framework.

This module provides utilities for debugging and development assistance
when the application is running in debug mode.
"""  # noqa: D202

import logging
import sys
import time
import inspect
import json
from typing import Any, Dict, List, Optional, Union, Callable

from core.config import get, is_development

# Configure the debug logger
logger = logging.getLogger("dawn.debug")

def is_debug_mode() -> bool:
    """
    Check if the application is running in debug mode.
    
    Debug mode must be explicitly enabled in configuration and
    is only available in development environments.
    
    Returns:
        bool: True if debug mode is enabled, False otherwise
    """
    return is_development() and get("debug_mode", False)

def debug_log(message: str, obj: Any = None) -> None:
    """
    Log a debug message if debug mode is enabled.
    
    Args:
        message: The message to log
        obj: Optional object to include in the log (will be formatted as JSON)
    """
    if not is_debug_mode():
        return
    
    # Get caller information for better debug logs
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    function = frame.f_code.co_name
    
    # Format the base message
    formatted_message = f"{filename}:{lineno} ({function}): {message}"
    
    # Include object representation if provided
    if obj is not None:
        try:
            # Try to convert to JSON
            if isinstance(obj, (dict, list)):
                obj_str = json.dumps(obj, indent=2, default=str)
            else:
                obj_str = str(obj)
            
            # Add object to the log
            formatted_message += f"\n{obj_str}"
        except Exception as e:
            formatted_message += f"\nError serializing object: {str(e)}"
    
    logger.debug(formatted_message)

def measure_execution_time(func: Callable) -> Callable:
    """
    Decorator to measure and log function execution time when in debug mode.
    
    Args:
        func: The function to measure
        
    Returns:
        The wrapped function
    """
    def wrapper(*args, **kwargs):
        if not is_debug_mode():
            return func(*args, **kwargs)
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Log execution time
        logger.debug(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper

def dump_variables(frame=None, include_locals=True, include_globals=False) -> Dict[str, Any]:
    """
    Dump variables from the specified frame (or caller's frame) for debugging.
    Only works in debug mode.
    
    Args:
        frame: Optional frame to dump variables from (defaults to caller's frame)
        include_locals: Whether to include local variables
        include_globals: Whether to include global variables
        
    Returns:
        Dictionary containing the requested variables
    """
    if not is_debug_mode():
        return {}
    
    # Get the frame to inspect
    if frame is None:
        frame = inspect.currentframe().f_back
    
    result = {}
    
    # Include local variables if requested
    if include_locals:
        local_vars = {}
        for key, value in frame.f_locals.items():
            # Skip private variables and modules
            if not key.startswith("__") and not inspect.ismodule(value):
                try:
                    # Try to represent the value as a string
                    local_vars[key] = str(value)
                except Exception:
                    local_vars[key] = f"<{type(value).__name__}>"
        
        result["locals"] = local_vars
    
    # Include global variables if requested
    if include_globals:
        global_vars = {}
        for key, value in frame.f_globals.items():
            # Skip private variables, modules, and functions
            if (not key.startswith("__") and not inspect.ismodule(value) 
                    and not inspect.isfunction(value) and not inspect.isclass(value)):
                try:
                    # Try to represent the value as a string
                    global_vars[key] = str(value)
                except Exception:
                    global_vars[key] = f"<{type(value).__name__}>"
        
        result["globals"] = global_vars
    
    return result

def initialize_debug_mode():
    """
    Initialize debug mode if enabled in configuration.
    
    This sets up the necessary logging and debug environment.
    Call this at application startup.
    """
    if is_debug_mode():
        # Configure detailed logging for debug mode
        root_logger = logging.getLogger()
        
        # Set the root logger to DEBUG level
        root_logger.setLevel(logging.DEBUG)
        
        # Check if a console handler already exists
        has_console_handler = False
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                has_console_handler = True
                handler.setLevel(logging.DEBUG)
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
        
        # Add a console handler if none exists
        if not has_console_handler:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            root_logger.addHandler(console_handler)
        
        # Set our debug logger to DEBUG level
        logger.setLevel(logging.DEBUG)
        
        logger.info("Debug mode initialized")
        
        # Log environment info
        import platform
        import os
        
        debug_log("System Information", {
            "python_version": sys.version,
            "platform": platform.platform(),
            "node": platform.node(),
            "cpu_count": os.cpu_count(),
            "cwd": os.getcwd(),
        })
        
        debug_log("Environment Variables", dict(os.environ)) 