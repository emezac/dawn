#!/usr/bin/env python3
"""
Debug Initializer for the Dawn Framework.

This module initializes debug mode for the application when enabled.
It should be imported and called at application startup.
"""  # noqa: D202

import logging
import sys
import os
from typing import Optional

from core.utils.debug import is_debug_mode, initialize_debug_mode
from core.config import get, set

# Configure logger
logger = logging.getLogger("dawn.debug_initializer")

def setup_debug_mode(force_enable: bool = False) -> bool:
    """
    Set up debug mode for the application.
    
    Args:
        force_enable: Force enable debug mode regardless of configuration
        
    Returns:
        True if debug mode is enabled, False otherwise
    """
    # Check environment variable first
    if os.environ.get("DAWN_DEBUG_MODE", "").lower() in ("true", "1", "yes", "y"):
        set("debug_mode", True)
    
    # Force enable if requested
    if force_enable:
        set("debug_mode", True)
    
    # Early exit if debug mode is not enabled
    if not is_debug_mode():
        logger.info("Debug mode is disabled")
        return False
    
    # Debug mode is enabled
    logger.info("Debug mode is ENABLED - initializing debug components")
    
    # Initialize basic debug utilities
    initialize_debug_mode()
    
    # Import and initialize workflow debugging
    try:
        from core.workflow.debug import patch_workflow_engine
        patch_workflow_engine()
        logger.info("Workflow engine patched for debug mode")
    except ImportError:
        logger.warning("Could not import workflow debugging utilities")
    except Exception as e:
        logger.error(f"Failed to patch workflow engine: {str(e)}")
    
    # Set up other debug components
    _setup_debug_components()
    
    logger.info("Debug mode initialization complete")
    return True

def _setup_debug_components() -> None:
    """Set up additional debug components."""
    # Set up logging
    _setup_debug_logging()
    
    # Add debug route handlers if web server is used
    _setup_debug_web()
    
    # Set up performance monitoring if enabled
    if get("debug_mode.performance_monitoring", True):
        _setup_performance_monitoring()

def _setup_debug_logging() -> None:
    """Set up debug logging."""
    # Get logging level from config
    level_name = get("debug_mode.log_level", "DEBUG")
    level = getattr(logging, level_name, logging.DEBUG)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Check if we need to log to a file
    log_file = get("debug_mode.log_file")
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ))
            root_logger.addHandler(file_handler)
            logger.info(f"Debug logs will be written to: {log_file}")
        except Exception as e:
            logger.error(f"Failed to set up debug log file: {str(e)}")

def _setup_debug_web() -> None:
    """Set up debug web components."""
    # Import debug panel if needed
    if get("debug_mode.enable_web_panel", True):
        try:
            from core.web.debug_panel import setup_debug_panel
            # Note: The actual setup will happen when the web app is created
            logger.info("Debug web panel will be enabled for web server")
        except ImportError:
            logger.warning("Could not import debug web panel")
    
    # Import debug middleware if needed
    if get("debug_mode.enable_web_middleware", True):
        try:
            from core.web.debug_middleware import apply_debug_middleware
            # Note: The middleware will be applied when the web app is created
            logger.info("Debug middleware will be applied to web requests")
        except ImportError:
            logger.warning("Could not import debug middleware")

def _setup_performance_monitoring() -> None:
    """Set up performance monitoring."""
    # This is a placeholder for more advanced performance monitoring
    logger.info("Performance monitoring enabled in debug mode")
    
    # Try to import and patch common functions for performance monitoring
    try:
        import core.tools.registry
        import time
        
        # Patch the execute_tool method to add performance metrics
        original_execute_tool = core.tools.registry.ToolRegistry.execute_tool
        
        def execute_tool_with_perf(self, tool_name, input_data, **kwargs):
            """Execute tool with performance monitoring."""
            start_time = time.time()
            
            try:
                result = original_execute_tool(self, tool_name, input_data, **kwargs)
                return result
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.debug(f"Tool {tool_name} executed in {execution_time:.4f}s")
        
        # Replace the method
        core.tools.registry.ToolRegistry.execute_tool = execute_tool_with_perf
        logger.info("Tool registry patched for performance monitoring")
    except (ImportError, AttributeError) as e:
        logger.warning(f"Could not patch tool registry for performance monitoring: {str(e)}")

# Automatically set up debug mode when this module is imported
# This allows users to simply import this module to enable debug mode
setup_debug_mode() 