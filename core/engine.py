"""
Workflow Engine for the AI Agent Framework.

This module provides the engine that executes workflows by processing
tasks in the correct order and handling their execution.
"""

from typing import Dict, Any, Optional
import re

from core.workflow import Workflow
from core.task import Task
from core.llm.interface import LLMInterface
from core.tools.registry import ToolRegistry
from core.utils.logger import (
    log_workflow_start, log_workflow_end, log_task_start, 
    log_task_end, log_task_retry, log_task_input, 
    log_task_output, log_error
)


class WorkflowEngine:
    """
    Engine for executing workflows.
    
    The workflow engine is responsible for executing tasks in the correct order,
    handling task dependencies, and managing the overall workflow execution.
    """
    
    def __init__(
        self, 
        workflow: Workflow, 
        llm_interface: LLMInterface, 
        tool_registry: ToolRegistry
    ):
        """
        Initialize the workflow engine.
        
        Args:
            workflow: The workflow to execute
            llm_interface: Interface for LLM interactions
            tool_registry: Registry of available tools
        """
        self.workflow = workflow
        self.llm_interface = llm_interface
        self.tool_registry = tool_registry
    
    def process_task_input(self, task: Task) -> Dict[str, Any]:
        """
        Process the input data for a task, resolving references to outputs of other tasks.
        
        Args:
            task: The task whose input data should be processed
            
        Returns:
            Processed input data with references resolved
        """
        processed_input = task.input_data.copy()
        
        # Look for references to other task outputs in string values
        for key, value in processed_input.items():
            if isinstance(value, str):
                # Look for patterns like "${task_id}.output_data.field"
                matches = re.findall(r'\${([^}]+)}', value)
                for match in matches:
                    parts = match.split('.')
                    if len(parts) >= 2:
                        ref_task_id = parts[0]
                        try:
                            ref_task = self.workflow.get_task(ref_task_id)
                            
                            # Simple case: ${task_id}.output_data
                            if len(parts) == 2 and parts[1] == 'output_data':
                                replacement = ref_task.output_data
                                # If the entire value is just the reference, replace with the object
                                if value == f"${{{match}}}":
                                    processed_input[key] = replacement
                                    break
                                # Otherwise, it's part of a string, so convert to string
                                replacement_str = str(replacement)
                                value = value.replace(f"${{{match}}}", replacement_str)
                                processed_input[key] = value
                            
                            # More specific case: ${task_id}.output_data.field
                            elif len(parts) >= 3 and parts[1] == 'output_data':
                                field = parts[2]
                                if field in ref_task.output_data:
                                    replacement = ref_task.output_data[field]
                                    # If the entire value is just the reference, replace with the value
                                    if value == f"${{{match}}}":
                                        processed_input[key] = replacement
                                        break
                                    # Otherwise, it's part of a string, so convert to string
                                    replacement_str = str(replacement)
                                    value = value.replace(f"${{{match}}}", replacement_str)
                                    processed_input[key] = value
                        
                        except KeyError:
                            log_error(f"Referenced task {ref_task_id} not found in workflow")
        
        return processed_input
    
    def execute_llm_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a task that requires an LLM.
        
        Args:
            task: The task to execute
            
        Returns:
            Dictionary with execution results
        """
        # Process input data to resolve references
        processed_input = self.process_task_input(task)
        log_task_input(task.id, processed_input)
        
        # Extract prompt from input data
        prompt = processed_input.get('prompt', '')
        if not prompt:
            return {
                "success": False,
                "error": "No prompt provided for LLM task"
            }
        
        # Execute LLM call
        result = self.llm_interface.execute_llm_call(prompt)
        
        if result["success"]:
            log_task_output(task.id, result)
            return result
        else:
            log_error(f"LLM task {task.id} failed: {result.get('error', 'Unknown error')}")
            return result
    
    def execute_tool_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a task that requires a tool.
        
        Args:
            task: The task to execute
            
        Returns:
            Dictionary with execution results
        """
        # Process input data to resolve references
        processed_input = self.process_task_input(task)
        log_task_input(task.id, processed_input)
        
        # Execute tool
        result = self.tool_registry.execute_tool(task.tool_name, processed_input)
        
        if result["success"]:
            log_task_output(task.id, result)
            return result
        else:
            log_error(f"Tool task {task.id} failed: {result.get('error', 'Unknown error')}")
            return result
    
    def execute_task(self, task: Task) -> bool:
        """
        Execute a single task.
        
        Args:
            task: The task to execute
            
        Returns:
            True if the task was executed successfully, False otherwise
        """
        log_task_start(task.id, task.name, self.workflow.id)
        task.set_status("running")
        
        # Execute the task based on its type
        if task.is_llm_task:
            result = self.execute_llm_task(task)
        else:
            result = self.execute_tool_task(task)
        
        # Update task status and output based on result
        if result.get("success", False):
            task.set_status("completed")
            task.set_output({"response": result.get("response", result.get("result", {}))})
            log_task_end(task.id, task.name, "completed", self.workflow.id)
            return True
        else:
            # Handle task failure
            return self.handle_task_failure(task, result)
    
    def handle_task_failure(self, task: Task, result: Dict[str, Any]) -> bool:
        """
        Handle a failed task execution.
        
        Args:
            task: The failed task
            result: The execution result containing error information
            
        Returns:
            True if the task was retried successfully, False if it failed permanently
        """
        # Check if we can retry
        if task.can_retry():
            task.increment_retry()
            log_task_retry(task.id, task.name, task.retry_count, task.max_retries)
            
            # Reset status to pending for retry
            task.set_status("pending")
            
            # Execute the task again
            return self.execute_task(task)
        else:
            # No more retries, mark as failed
            task.set_status("failed")
            task.set_output({"error": result.get("error", "Unknown error")})
            log_task_end(task.id, task.name, "failed", self.workflow.id)
            return False
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the entire workflow.
        
        Returns:
            Dictionary with workflow execution results
        """
        log_workflow_start(self.workflow.id, self.workflow.name)
        self.workflow.set_status("running")
        
        # Reset workflow to start from the beginning
        self.workflow.current_task_index = 0
        
        # Get the first task
        current_task = self.workflow.get_next_task()
        
        # Execute tasks until workflow is completed or failed
        while current_task is not None and self.workflow.status != "failed":
            # Execute the current task
            success = self.execute_task(current_task)
            
            if not success:
                # If task failed and couldn't be retried, check if there's a failure path
                if current_task.next_task_id_on_failure:
                    # Continue with the failure path
                    current_task = self.workflow.get_next_task_by_condition(current_task)
                else:
                    # No failure path, mark workflow as failed
                    self.workflow.set_status("failed")
                    log_workflow_end(self.workflow.id, self.workflow.name, "failed")
                    break
            else:
                # Task succeeded, get the next task
                current_task = self.workflow.get_next_task_by_condition(current_task)
        
        # If we've processed all tasks and workflow isn't failed, mark as completed
        if self.workflow.status != "failed":
            self.workflow.set_status("completed")
            log_workflow_end(self.workflow.id, self.workflow.name, "completed")
        
        # Return the workflow results
        return {
            "workflow_id": self.workflow.id,
            "workflow_name": self.workflow.name,
            "status": self.workflow.status,
            "tasks": {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()}
        }
