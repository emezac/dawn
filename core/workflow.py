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
    """
    
    def __init__(self, workflow_id: str, name: str):
        """
        Initialize a new Workflow.
        """
        self.id = workflow_id
        self.name = name
        self.status = "pending"  # pending, running, completed, failed
        self.tasks = {}  # Map of task_id to Task objects
        self.task_order = []  # Ordered list of task_ids
        self.current_task_index = 0
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the workflow.
        """
        if task.id in self.tasks:
            raise ValueError(f"Task with id {task.id} already exists in workflow")
        self.tasks[task.id] = task
        self.task_order.append(task.id)
    
    def get_task(self, task_id: str) -> Task:
        """
        Get a task by its ID.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with id {task_id} not found in workflow")
        return self.tasks[task_id]
    
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
        """
        valid_statuses = ["pending", "running", "completed", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        self.status = status
    
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
