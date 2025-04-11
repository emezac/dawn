"""
Error propagation utilities for the Dawn framework.

This module provides utilities for tracking and propagating errors between tasks
in a workflow, allowing for detailed error information to be passed from one task
to another and enabling robust error handling.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

from core.errors import ErrorCode, create_error_response

logger = logging.getLogger(__name__)

class ErrorContext:
    """
    Container for tracking error information between tasks.
    
    This class maintains a record of errors that occurred during task execution,
    allowing downstream tasks to access detailed error information from upstream tasks.
    """  # noqa: D202
    
    def __init__(self, workflow_id: str):
        """
        Initialize a new ErrorContext.
        
        Args:
            workflow_id: ID of the workflow this error context belongs to
        """
        self.workflow_id = workflow_id
        self.task_errors: Dict[str, Dict[str, Any]] = {}
        self.propagated_errors: List[Dict[str, Any]] = []
    
    def record_task_error(self, task_id: str, error_data: Dict[str, Any]) -> None:
        """
        Record an error that occurred during a task's execution.
        
        Args:
            task_id: ID of the task that encountered the error
            error_data: Error details including error message, code, etc.
        """
        # Ensure the error_data has the required fields
        if "error" not in error_data:
            error_data["error"] = "Unknown error"
        
        if "timestamp" not in error_data:
            error_data["timestamp"] = datetime.now().isoformat()
        
        if "error_code" not in error_data:
            error_data["error_code"] = ErrorCode.UNKNOWN_ERROR
        
        # Store the error data with the task ID
        self.task_errors[task_id] = error_data
        
        # Log the error
        logger.error(f"Task {task_id} in workflow {self.workflow_id} failed: {error_data['error']}")
    
    def get_task_error(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the error details for a specific task.
        
        Args:
            task_id: ID of the task to get error details for
            
        Returns:
            Error details dict if available, None otherwise
        """
        return self.task_errors.get(task_id)
    
    def propagate_error(self, source_task_id: str, target_task_id: str, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Propagate an error from one task to another with additional context.
        
        Args:
            source_task_id: ID of the task where the error originated
            target_task_id: ID of the task receiving the propagated error
            additional_context: Optional additional context to include
            
        Returns:
            Propagated error details dict
        """
        source_error = self.get_task_error(source_task_id)
        if not source_error:
            # Create a generic error if the source task has no recorded error
            propagated_error = create_error_response(
                message=f"Unknown error propagated from task {source_task_id}",
                error_code=ErrorCode.FRAMEWORK_TASK_ERROR,
                source_task_id=source_task_id,
                target_task_id=target_task_id
            )
        else:
            # Create a propagated error based on the source error
            propagated_error = source_error.copy()
            # Update the error message to indicate propagation
            propagated_error["error"] = f"Error propagated from task {source_task_id}: {source_error['error']}"
            
            # Create a propagation chain if one doesn't exist
            if "propagation_chain" not in propagated_error:
                propagated_error["propagation_chain"] = []
            
            # Add the source task to the propagation chain
            propagated_error["propagation_chain"].append({
                "task_id": source_task_id,
                "timestamp": datetime.now().isoformat()
            })
        
        # Add additional context if provided
        if additional_context:
            if "error_details" not in propagated_error:
                propagated_error["error_details"] = {}
            
            # Merge additional context with existing error details
            propagated_error["error_details"].update(additional_context)
        
        # Record the propagated error
        self.propagated_errors.append({
            "source_task_id": source_task_id,
            "target_task_id": target_task_id,
            "error": propagated_error
        })
        
        # Update the task errors with the propagated error
        self.task_errors[target_task_id] = propagated_error
        
        return propagated_error
    
    def get_latest_error(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently recorded error.
        
        Returns:
            The most recent error details dict if available, None otherwise
        """
        if not self.task_errors:
            return None
        
        # Get the most recent error based on timestamp
        latest_error = None
        latest_timestamp = None
        
        for error in self.task_errors.values():
            timestamp = error.get("timestamp")
            if timestamp and (latest_timestamp is None or timestamp > latest_timestamp):
                latest_timestamp = timestamp
                latest_error = error
        
        return latest_error
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of all errors in this context.
        
        Returns:
            Dict containing an overview of all errors
        """
        return {
            "workflow_id": self.workflow_id,
            "error_count": len(self.task_errors),
            "has_errors": len(self.task_errors) > 0,
            "tasks_with_errors": list(self.task_errors.keys()),
            "propagation_count": len(self.propagated_errors),
            "latest_error": self.get_latest_error(),
        }


def get_error_value(task_output: Dict[str, Any], path: Optional[str] = None, default: Any = None) -> Any:
    """
    Extract error information from a task's output data.
    
    This utility function helps extract error details from task output data,
    making it easier for downstream tasks to access and use error information.
    
    Args:
        task_output: The output data from a task
        path: Dot notation path to a specific error field (e.g., "error_details.field_name")
            If None, returns the entire error object
        default: Default value to return if the path doesn't exist
        
    Returns:
        The extracted error value or the default if not found
    """
    if not task_output:
        return default
    
    # If there's no error in the output, return the default
    if "error" not in task_output:
        return default
    
    if not path:
        # Return the entire error object
        error_obj = {
            "error": task_output.get("error"),
            "error_code": task_output.get("error_code", ErrorCode.UNKNOWN_ERROR),
            "error_details": task_output.get("error_details", {})
        }
        
        # Include other relevant error fields
        for key in ["error_type", "propagation_chain", "timestamp"]:
            if key in task_output:
                error_obj[key] = task_output[key]
        
        return error_obj
    
    # Use the path resolver for extracting specific fields
    from core.utils.variable_resolver import resolve_path
    
    try:
        # Check if the path is directly in the task output
        return resolve_path(task_output, path)
    except (KeyError, IndexError, ValueError):
        # If not found in the main output, check in error_details
        if "error_details" in task_output and isinstance(task_output["error_details"], dict):
            try:
                return resolve_path(task_output["error_details"], path)
            except (KeyError, IndexError, ValueError):
                pass
        
        return default


def format_error_for_template(error_object: Dict[str, Any]) -> str:
    """
    Format an error object for display in a template.
    
    This utility function creates a human-readable string representation of an error object,
    suitable for inclusion in templates or error messages.
    
    Args:
        error_object: The error object to format
        
    Returns:
        Formatted error string
    """
    if not error_object or not isinstance(error_object, dict):
        return "No error information available"
    
    lines = []
    
    # Add the main error message
    if "error" in error_object:
        lines.append(f"Error: {error_object['error']}")
    
    # Add the error code if available
    if "error_code" in error_object:
        lines.append(f"Code: {error_object['error_code']}")
    
    # Add error details if available
    if "error_details" in error_object and error_object["error_details"]:
        lines.append("Details:")
        for key, value in error_object["error_details"].items():
            lines.append(f"  - {key}: {value}")
    
    # Add propagation chain if available
    if "propagation_chain" in error_object and error_object["propagation_chain"]:
        lines.append("Propagation Path:")
        for step in error_object["propagation_chain"]:
            task_id = step.get("task_id", "unknown")
            timestamp = step.get("timestamp", "unknown time")
            lines.append(f"  - Task {task_id} at {timestamp}")
    
    return "\n".join(lines) 