"""
Workflow module for the Dawn platform.

This module defines the Workflow class, which represents a sequence of tasks
to be executed by the workflow engine.
"""

from typing import Dict, List, Optional, Any, Set
from enum import Enum


class WorkflowStatus(Enum):
    """Status of a workflow."""  # noqa: D202
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workflow:
    """
    Represents a workflow consisting of multiple tasks.
    
    A workflow is a directed graph of tasks, where each task can have
    dependencies on other tasks and can conditionally branch to different
    next tasks based on its output.
    """  # noqa: D202
    
    def __init__(self, workflow_id: str, name: str, description: Optional[str] = None):
        """
        Initialize a new Workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Human-readable name for the workflow
            description: Optional description of the workflow
        """
        self.id = workflow_id
        self.name = name
        self.description = description or ""
        self.tasks = {}  # Dict mapping task IDs to Task objects
        self.task_order = []  # List of task IDs in execution order
        self.variables = {}  # Dict of workflow variables
        self.status = WorkflowStatus.PENDING
        self.tool_registry = None
        
    def add_task(self, task):
        """
        Add a task to the workflow.
        
        Args:
            task: Task object to add
        """
        self.tasks[task.id] = task
        if task.id not in self.task_order:
            self.task_order.append(task.id)
        
    def set_task_order(self, task_ids: List[str]):
        """
        Set the order of task execution.
        
        Args:
            task_ids: List of task IDs in the desired execution order
        """
        # Validate that all task IDs exist
        for task_id in task_ids:
            if task_id not in self.tasks:
                raise ValueError(f"Task ID '{task_id}' not found in workflow")
        
        self.task_order = task_ids
        
    def set_tool_registry(self, tool_registry):
        """
        Set the tool registry for the workflow.
        
        Args:
            tool_registry: Tool registry to use for tool executions
        """
        self.tool_registry = tool_registry
        
        # Set the tool registry for all tasks
        for task in self.tasks.values():
            task.set_tool_registry(tool_registry)
        
    def set_status(self, status_name: str):
        """
        Set the status of the workflow.
        
        Args:
            status_name: Name of the status to set (e.g., "running", "completed")
        """
        if isinstance(status_name, str):
            try:
                # Convert string to enum value if needed
                status_enum = getattr(WorkflowStatus, status_name.upper())
                self.status = status_enum
            except (AttributeError, KeyError):
                # If status string doesn't match any enum value, keep the string
                self.status = status_name
        else:
            # If already an enum or other type, set directly
            self.status = status_name
        
    def execute(self, execution_context=None):
        """
        Execute the workflow.
        
        Args:
            execution_context: Optional execution context to use
            
        Returns:
            Dict containing the workflow result
        """
        # This is a simplified implementation that would be replaced in production
        self.status = WorkflowStatus.RUNNING
        
        try:
            # Execute tasks in order
            last_result = None
            
            for task_id in self.task_order:
                task = self.tasks[task_id]
                last_result = task.execute(execution_context)
                
                # Update execution context with task result
                if execution_context and last_result:
                    execution_context.variables[task.id + "_result"] = last_result.get("result")
                    
                # Handle task failure
                if not last_result.get("success", False):
                    self.status = WorkflowStatus.FAILED
                    return {
                        "success": False,
                        "error": f"Task '{task_id}' failed: {last_result.get('error', 'Unknown error')}",
                        "task_id": task_id,
                        "task_result": last_result
                    }
            
            self.status = WorkflowStatus.COMPLETED
            
            # Return success with the last task's result
            return {
                "success": True,
                "result": last_result.get("result") if last_result else None,
                "variables": execution_context.variables if execution_context else {}
            }
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary representation.
        
        Returns:
            Dict representation of the workflow
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "task_order": self.task_order,
            "status": self.status.value
        }
        
    def __str__(self) -> str:
        """Return a string representation of the workflow."""
        return f"Workflow({self.id}, {self.name}, {len(self.tasks)} tasks)" 