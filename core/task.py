"""
Task class for the AI Agent Framework.

This module defines the Task class which represents a single unit of work
in a workflow. Tasks can be executed by an LLM or a tool.
"""

from typing import Dict, Optional, Any


class Task:
    """
    Represents a single task in a workflow.
    
    A task can be executed by an LLM or a tool, and has a status that
    tracks its execution state.
    """
    
    def __init__(
        self,
        task_id: str,
        name: str,
        is_llm_task: bool = False,
        tool_name: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 0,
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        condition: Optional[str] = None  # New optional condition field
    ):
        """
        Initialize a new Task.
        
        Args:
            task_id: Unique identifier for the task
            name: Human-readable name for the task
            is_llm_task: Whether this task requires an LLM to execute
            tool_name: Name of the tool to use (if not an LLM task)
            input_data: Initial input data for the task
            max_retries: Maximum number of retry attempts if the task fails
            next_task_id_on_success: ID of the task to execute after this one succeeds
            next_task_id_on_failure: ID of the task to execute after this one fails
            condition: Optional condition (as a string expression) used to choose next task
        """
        self.id = task_id
        self.name = name
        self.status = "pending"  # One of: pending, running, completed, failed
        self.input_data = input_data or {}
        self.output_data = {}
        self.is_llm_task = is_llm_task
        self.tool_name = tool_name
        self.retry_count = 0
        self.max_retries = max_retries
        self.next_task_id_on_success = next_task_id_on_success
        self.next_task_id_on_failure = next_task_id_on_failure
        self.condition = condition  # New field for conditional branching
        
        # Validate that non-LLM tasks have a tool_name
        if not is_llm_task and not tool_name:
            raise ValueError("Non-LLM tasks must specify a tool_name")
    
    def set_status(self, status: str) -> None:
        """
        Update the status of the task.
        """
        valid_statuses = ["pending", "running", "completed", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        self.status = status
    
    def increment_retry(self) -> None:
        """Increment the retry counter for this task."""
        self.retry_count += 1
    
    def can_retry(self) -> bool:
        """Check if the task can be retried."""
        return self.retry_count < self.max_retries
    
    def set_input(self, data: Dict[str, Any]) -> None:
        """Set or update the input data for this task."""
        self.input_data = data
    
    def set_output(self, data: Dict[str, Any]) -> None:
        """Set the output data for this task."""
        self.output_data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "is_llm_task": self.is_llm_task,
            "tool_name": self.tool_name,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "next_task_id_on_success": self.next_task_id_on_success,
            "next_task_id_on_failure": self.next_task_id_on_failure,
            "condition": self.condition,
        }
    
    def __repr__(self) -> str:
        """String representation of the task."""
        return f"Task(id={self.id}, name={self.name}, status={self.status})"
