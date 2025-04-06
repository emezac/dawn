"""
Utility functions for logging in the AI Agent Framework.

This module provides a simple logging mechanism for tracking the execution
of workflows and tasks.
"""

import logging
from typing import Any, Dict, Optional

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger
logger = logging.getLogger('ai_agent_framework')


def log_workflow_start(workflow_id: str, workflow_name: str) -> None:
    """
    Log the start of a workflow execution.
    
    Args:
        workflow_id: ID of the workflow
        workflow_name: Name of the workflow
    """
    logger.info(f"Starting workflow: {workflow_name} (ID: {workflow_id})")


def log_workflow_end(workflow_id: str, workflow_name: str, status: str) -> None:
    """
    Log the end of a workflow execution.
    
    Args:
        workflow_id: ID of the workflow
        workflow_name: Name of the workflow
        status: Final status of the workflow (completed, failed)
    """
    logger.info(f"Workflow {workflow_name} (ID: {workflow_id}) ended with status: {status}")


def log_task_start(task_id: str, task_name: str, workflow_id: str) -> None:
    """
    Log the start of a task execution.
    
    Args:
        task_id: ID of the task
        task_name: Name of the task
        workflow_id: ID of the parent workflow
    """
    logger.info(f"Starting task: {task_name} (ID: {task_id}) in workflow {workflow_id}")


def log_task_end(task_id: str, task_name: str, status: str, workflow_id: str) -> None:
    """
    Log the end of a task execution.
    
    Args:
        task_id: ID of the task
        task_name: Name of the task
        status: Final status of the task (completed, failed)
        workflow_id: ID of the parent workflow
    """
    logger.info(f"Task {task_name} (ID: {task_id}) in workflow {workflow_id} ended with status: {status}")


def log_task_retry(task_id: str, task_name: str, retry_count: int, max_retries: int) -> None:
    """
    Log a task retry attempt.
    
    Args:
        task_id: ID of the task
        task_name: Name of the task
        retry_count: Current retry count
        max_retries: Maximum number of retries allowed
    """
    logger.info(f"Retrying task {task_name} (ID: {task_id}). Attempt {retry_count} of {max_retries}")


def log_task_input(task_id: str, input_data: Dict[str, Any]) -> None:
    """
    Log the input data for a task.
    
    Args:
        task_id: ID of the task
        input_data: Input data dictionary
    """
    logger.debug(f"Task {task_id} input data: {input_data}")


def log_task_output(task_id: str, output_data: Dict[str, Any]) -> None:
    """
    Log the output data from a task.
    
    Args:
        task_id: ID of the task
        output_data: Output data dictionary
    """
    logger.debug(f"Task {task_id} output data: {output_data}")


def log_error(message: str, error: Optional[Exception] = None) -> None:
    """
    Log an error message.
    
    Args:
        message: Error message
        error: Optional exception object
    """
    if error:
        logger.error(f"{message}: {str(error)}")
    else:
        logger.error(message)
