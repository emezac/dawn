"""
Workflow class for the AI Agent Framework.

This module defines the Workflow class which represents a collection of tasks
that can be executed in a specific order with dependencies.
"""

from typing import Any, Dict, List, Optional

from .task import Task
from .errors import ErrorCode


class Workflow:
    """
    Represents a workflow consisting of multiple tasks.
    
    A workflow manages a collection of tasks and tracks their execution status,
    handling task dependencies and error propagation between tasks.
    """  # noqa: D202

    def __init__(self, workflow_id: str, name: str):
        """
        Initialize a new Workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Human-readable name for the workflow
        """
        self.id = workflow_id
        self.name = name
        self.status = "pending"  # pending, running, completed, failed
        self.tasks = {}  # Map of task_id to Task objects
        self.task_order = []  # Ordered list of task_ids
        self.current_task_index = 0
        
        # Error tracking
        self.error = None
        self.error_code = None
        self.error_details = {}
        self.failed_tasks = []

    def add_task(self, task: Task) -> None:
        """
        Add a task to the workflow.
        """
        if task.id in self.tasks:
            raise ValueError(f"Task with id {task.id} already exists in workflow")
        self.tasks[task.id] = task
        self.task_order.append(task.id)

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by its ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            The task with the given ID, or None if not found
        """
        return self.tasks.get(task_id)  # Use dict.get() which returns None if key not found

    def get_next_task(self) -> Optional[Task]:
        """
        Get the next task in default order.
        """
        if self.current_task_index >= len(self.task_order):
            return None
        task_id = self.task_order[self.current_task_index]
        self.current_task_index += 1
        return self.tasks[task_id]

    def get_next_task_by_condition(self, current_task: Task) -> Optional[Task]:
        """
        Get the next task based on the outcome and (optionally) a condition.
        """
        next_task_id = None

        # If a condition is defined, evaluate it.
        if current_task.condition is not None:
            try:
                if eval(current_task.condition, {}, current_task.output_data):
                    next_task_id = current_task.next_task_id_on_success
                else:
                    next_task_id = current_task.next_task_id_on_failure
            except Exception as e:
                next_task_id = current_task.next_task_id_on_success
        else:
            if current_task.status == "completed" and current_task.next_task_id_on_success:
                next_task_id = current_task.next_task_id_on_success
            elif current_task.status == "failed" and current_task.next_task_id_on_failure:
                next_task_id = current_task.next_task_id_on_failure

        if next_task_id is None:
            return self.get_next_task()

        if next_task_id in self.tasks:
            try:
                self.current_task_index = self.task_order.index(next_task_id)
                return self.tasks[next_task_id]
            except ValueError:
                return None
        return None

    def set_status(self, status: str) -> None:
        """
        Update the status of the workflow.
        
        Args:
            status: New status for the workflow (pending, running, completed, failed)
            
        Raises:
            ValueError: If an invalid status is provided
        """
        valid_statuses = ["pending", "running", "completed", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        self.status = status
        
        # If the workflow is marked as failed, record tasks that failed
        if status == "failed":
            self.failed_tasks = [
                task_id for task_id, task in self.tasks.items() 
                if task.status == "failed"
            ]

    def set_error(self, error_message: str, error_code: Optional[str] = None) -> None:
        """
        Set workflow error information.
        
        Args:
            error_message: Error message describing the failure
            error_code: Optional error code identifier
        """
        self.status = "failed"
        self.error = error_message
        
        # Store error code if provided
        if error_code is not None:
            self.error_code = error_code
        
        # Log the error
        print(f"Workflow '{self.id}' error: {error_message}")

    def is_completed(self) -> bool:
        """
        Check if the workflow is completed.
        """
        if self.status in ["completed", "failed"]:
            return True
        return all(task.status == "completed" for task in self.tasks.values())

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary representation.
        
        Returns:
            Dictionary representation of the workflow
        """
        result = {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "task_order": self.task_order,
            "current_task_index": self.current_task_index,
        }
        
        # Include error information if present
        if self.error:
            result["error"] = self.error
            result["error_code"] = self.error_code
            
            if self.error_details:
                result["error_details"] = self.error_details
                
            if self.failed_tasks:
                result["failed_tasks"] = self.failed_tasks
                
        return result

    def __repr__(self) -> str:
        """String representation of the workflow."""
        return f"Workflow(id={self.id}, name={self.name}, status={self.status}, tasks={len(self.tasks)})"
