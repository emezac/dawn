"""
Workflow class for the AI Agent Framework.

This module defines the Workflow class which represents a collection of tasks
that can be executed in a specific order with dependencies.
"""

from typing import Dict, List, Optional, Any
from .task import Task


class Workflow:
    """
    Represents a workflow consisting of multiple tasks.
    
    A workflow manages the execution order of tasks and tracks the overall
    workflow state.
    """
    
    def __init__(self, workflow_id: str, name: str):
        """
        Initialize a new Workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Human-readable name for the workflow
        """
        self.id = workflow_id
        self.name = name
        self.status = "pending"  # One of: pending, running, completed, failed
        self.tasks = {}  # Map of task_id to Task objects
        self.task_order = []  # Ordered list of task_ids
        self.current_task_index = 0
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the workflow.
        
        Args:
            task: Task object to add
        """
        if task.id in self.tasks:
            raise ValueError(f"Task with id {task.id} already exists in workflow")
        
        self.tasks[task.id] = task
        self.task_order.append(task.id)
    
    def get_task(self, task_id: str) -> Task:
        """
        Get a task by its ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            The Task object
            
        Raises:
            KeyError: If the task_id does not exist in the workflow
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with id {task_id} not found in workflow")
        
        return self.tasks[task_id]
    
    def get_next_task(self) -> Optional[Task]:
        """
        Get the next task in the workflow based on the current index.
        
        Returns:
            The next Task object, or None if there are no more tasks
        """
        if self.current_task_index >= len(self.task_order):
            return None
        
        task_id = self.task_order[self.current_task_index]
        self.current_task_index += 1
        return self.tasks[task_id]
    
    def get_next_task_by_condition(self, current_task: Task) -> Optional[Task]:
        """
        Get the next task based on the success/failure of the current task.
        
        Args:
            current_task: The current task that has completed execution
            
        Returns:
            The next Task object based on conditions, or None if there is no next task
        """
        next_task_id = None
        
        # Determine next task based on current task's status
        if current_task.status == "completed" and current_task.next_task_id_on_success:
            next_task_id = current_task.next_task_id_on_success
        elif current_task.status == "failed" and current_task.next_task_id_on_failure:
            next_task_id = current_task.next_task_id_on_failure
        
        # If no conditional next task, use the default order
        if next_task_id is None:
            return self.get_next_task()
        
        # If conditional next task exists, update the current index
        if next_task_id in self.tasks:
            # Find the index of the next task and update current_task_index
            try:
                self.current_task_index = self.task_order.index(next_task_id)
                return self.tasks[next_task_id]
            except ValueError:
                # Task ID exists in tasks but not in task_order (should not happen)
                return None
        
        return None
    
    def set_status(self, status: str) -> None:
        """
        Update the status of the workflow.
        
        Args:
            status: New status (pending, running, completed, failed)
        """
        valid_statuses = ["pending", "running", "completed", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        self.status = status
    
    def is_completed(self) -> bool:
        """
        Check if the workflow is completed.
        
        Returns:
            True if all tasks are completed or the workflow status is completed/failed
        """
        if self.status in ["completed", "failed"]:
            return True
        
        # Check if all tasks are completed
        all_completed = all(task.status == "completed" for task in self.tasks.values())
        return all_completed
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary representation.
        
        Returns:
            Dictionary representation of the workflow
        """
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "task_order": self.task_order,
            "current_task_index": self.current_task_index
        }
    
    def __repr__(self) -> str:
        """String representation of the workflow."""
        return f"Workflow(id={self.id}, name={self.name}, status={self.status}, tasks={len(self.tasks)})"
