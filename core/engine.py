"""
Workflow Engine for the AI Agent Framework.

This module provides the engine that executes workflows by processing
tasks in the correct order, handling dependencies, and managing execution.
"""

import re
from typing import Any, Dict, Optional

from core.llm.interface import LLMInterface
from core.task import Task
from core.tools.registry import ToolRegistry
from core.utils.logger import (
    log_error,
    log_task_end,
    log_task_input,
    log_task_output,
    log_task_retry,
    log_task_start,
    log_workflow_end,
    log_workflow_start,
)
from core.workflow import Workflow
from core.errors import ErrorCode, DawnError, create_error_response
from core.error_propagation import ErrorContext


class WorkflowEngine:
    """
    Engine for executing workflows.

    This class handles the execution of workflows by running their tasks
    in the specified order, handling task failures, and maintaining the
    state of the workflow.
    """  # noqa: D202

    def __init__(
        self,
        workflow: Workflow,
        llm_interface: "LLMInterface",
        tool_registry: "ToolRegistry",
        services: "ServiceContainer" = None,
    ):
        """
        Initialize a new WorkflowEngine.

        Args:
            workflow: The workflow to execute
            llm_interface: Interface for executing LLM tasks
            tool_registry: Registry of available tools
            services: Optional service container for accessing shared services
        """
        self.workflow = workflow
        self.llm_interface = llm_interface
        self.tool_registry = tool_registry
        self.services = services
        
        # Initialize error context for tracking errors across tasks
        self.error_context = ErrorContext(workflow_id=workflow.id)

    def process_task_input(self, task: Task) -> Dict[str, Any]:
        """
        Process a task's input data, resolving references to outputs of previous tasks.
        
        Args:
            task: The task whose input data should be processed
            
        Returns:
            Processed input data with resolved references
        """
        processed_input = task.input_data.copy() if task.input_data else {}
        
        # Get all tasks that might be referenced
        completed_tasks = {
            task_id: t for task_id, t in self.workflow.tasks.items() 
            if t.status in ["completed", "failed"] and t.id != task.id
        }
        
        if not completed_tasks:
            return processed_input
            
        # Process string values that might contain references
        for key, value in processed_input.items():
            if isinstance(value, str) and "${" in value:
                # Look for references to task outputs
                matches = re.findall(r"\${([^}]+)}", value)
                for match in matches:
                    # Check if this is an error reference
                    if match.startswith("error."):
                        # Extract the task ID and error path
                        parts = match.split(".", 2)
                        if len(parts) >= 3:
                            task_id = parts[1]
                            error_path = parts[2] if len(parts) > 2 else None
                            
                            # Try to get the error from the error context
                            error_data = self.error_context.get_task_error(task_id)
                            if error_data:
                                # Get the error value using the provided path
                                from core.error_propagation import get_error_value
                                error_value = get_error_value(error_data, error_path)
                                
                                # Replace the reference with the error value
                                if error_value is not None:
                                    if value == f"${{{match}}}":
                                        processed_input[key] = error_value
                                        break
                                    processed_input[key] = value.replace(f"${{{match}}}", str(error_value))
                    else:
                        # Standard task output reference
                        parts = match.split(".")
                        ref_task_id = parts[0]
                        
                        if ref_task_id in completed_tasks:
                            ref_task = completed_tasks[ref_task_id]
                            # Extract the referenced field from the task output
                            field = ".".join(parts[1:]) if len(parts) > 1 else None
                            try:
                                if field:
                                    replacement = ref_task.get_output_value(field)
                                else:
                                    replacement = ref_task.get_output_value()
                                    
                                if replacement is not None:
                                    if value == f"${{{match}}}":
                                        processed_input[key] = replacement
                                        break
                                    processed_input[key] = value.replace(f"${{{match}}}", str(replacement))
                            except Exception as e:
                                log_error(f"Error resolving reference ${{{match}}}: {str(e)}")
        
        return processed_input

    def execute_task(self, task: Task) -> bool:
        """
        Execute a task and return whether it was successful.

        This method handles different types of tasks including LLM tasks, tool tasks,
        and DirectHandlerTasks.

        Args:
            task: The task to execute

        Returns:
            bool: True if execution was successful, False otherwise
        """
        log_task_start(task.id, task.name, self.workflow.id)
        task.set_status("running")

        # Process task input to resolve variable references
        processed_input = self.process_task_input(task)
        log_task_input(task.id, processed_input)

        # Check if this is a DirectHandlerTask
        if hasattr(task, "is_direct_handler") and task.is_direct_handler:
            # Execute DirectHandlerTask directly using its execute method
            result = task.execute(processed_input)
        # Standard task execution based on type
        elif task.is_llm_task:
            result = self.execute_llm_task(task, processed_input)
        else:
            result = self.execute_tool_task(task, processed_input)

        # Process the result
        if result.get("success", False):
            task.set_status("completed")
            # Preserve the complete result structure in the output
            # Make sure both 'result' and 'response' are available for backward compatibility
            output_data = result.copy()
            
            # Ensure at least one of result or response is set
            if "result" in result and "response" not in result:
                output_data["response"] = result["result"]
            elif "response" in result and "result" not in result:
                output_data["result"] = result["response"]
                
            task.set_output(output_data)
            log_task_end(task.id, task.name, "completed", self.workflow.id)
            return True
        else:
            return self.handle_task_failure(task, result)

    def execute_llm_task(self, task: Task, processed_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an LLM task using the LLM interface.

        Args:
            task: The LLM task to execute
            processed_input: Optional pre-processed input data

        Returns:
            Dict with the result of LLM execution
        """
        # Use provided processed input or process it now
        if processed_input is None:
            processed_input = self.process_task_input(task)
            log_task_input(task.id, processed_input)

        prompt = processed_input.get("prompt", "")
        if not prompt:
            return {"success": False, "error": "No prompt provided for LLM task"}

        result = self.llm_interface.execute_llm_call(
            prompt=prompt,
            use_file_search=task.use_file_search,
            file_search_vector_store_ids=task.file_search_vector_store_ids,
            file_search_max_results=task.file_search_max_results,
        )

        if result["success"]:
            log_task_output(task.id, result)
            return result
        else:
            log_error(f"LLM task {task.id} failed: {result.get('error', 'Unknown error')}")
            return result

    def execute_tool_task(self, task: Task, processed_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a tool task using the tool registry.

        Args:
            task: The tool task to execute
            processed_input: Optional pre-processed input data

        Returns:
            Dict with the result of tool execution
        """
        # Use provided processed input or process it now
        if processed_input is None:
            processed_input = self.process_task_input(task)
            log_task_input(task.id, processed_input)

        result = self.tool_registry.execute_tool(task.tool_name, processed_input)
        if result["success"]:
            log_task_output(task.id, result)
            return result
        else:
            log_error(f"Tool task {task.id} failed: {result.get('error', 'Unknown error')}")
            return result

    def handle_task_failure(self, task: Task, result: Dict[str, Any]) -> bool:
        """
        Handle a task failure by retrying if possible or recording the error.
        
        Args:
            task: The task that failed
            result: The error result from task execution
            
        Returns:
            Boolean indicating if execution should continue
        """
        # Record the error in our error context
        self.error_context.record_task_error(task.id, result)
        
        # Check if the task can be retried
        if task.can_retry():
            task.increment_retry()
            log_task_retry(task.id, task.name, task.retry_count, task.max_retries)
            task.set_status("pending")
            return self.execute_task(task)
        else:
            # Task failed permanently
            task.set_status("failed")
            
            # Extract error details
            error_message = result.get("error", "Unknown error")
            error_code = result.get("error_code", ErrorCode.UNKNOWN_ERROR)
            error_details = result.get("error_details", {})
            
            # Set detailed error output on the task
            error_output = {
                "success": False,
                "error": error_message,
                "error_code": error_code,
                "error_details": error_details
            }
            
            # Include any additional fields from the result
            for key, value in result.items():
                if key not in error_output and key != "annotations":
                    error_output[key] = value
            
            task.set_output(error_output)
            log_task_end(task.id, task.name, "failed", self.workflow.id)
            return False

    def get_next_task_by_condition(self, current_task: Task) -> Optional[Task]:
        """
        Get the next task based on the current task's status and an optional condition.
        """
        next_task_id = None

        if current_task.condition is not None:
            try:
                # Pass a local context with 'output_data' to the eval function.
                if eval(current_task.condition, {}, {"output_data": current_task.output_data}):
                    next_task_id = current_task.next_task_id_on_success
                else:
                    next_task_id = current_task.next_task_id_on_failure
            except Exception as e:
                # If evaluation fails, fall back to the success branch.
                next_task_id = current_task.next_task_id_on_success
        else:
            if current_task.status == "completed" and current_task.next_task_id_on_success:
                next_task_id = current_task.next_task_id_on_success
            elif current_task.status == "failed" and current_task.next_task_id_on_failure:
                next_task_id = current_task.next_task_id_on_failure

        if next_task_id is None:
            return self.get_next_task()

        if next_task_id in self.workflow.tasks:
            try:
                self.workflow.current_task_index = self.workflow.task_order.index(next_task_id)
                return self.workflow.tasks[next_task_id]
            except ValueError:
                return None
        return None

    def get_next_task(self) -> Optional[Task]:
        if self.workflow.current_task_index >= len(self.workflow.task_order):
            return None
        task_id = self.workflow.task_order[self.workflow.current_task_index]
        self.workflow.current_task_index += 1
        return self.workflow.tasks[task_id]

    def run(self) -> Dict[str, Any]:
        """
        Run the workflow by executing all its tasks in order.
        
        Returns:
            Dict containing the workflow execution results
        """
        log_workflow_start(self.workflow.id, self.workflow.name)
        self.workflow.set_status("running")
        self.workflow.current_task_index = 0
        current_task = self.get_next_task()
        
        while current_task is not None and self.workflow.status != "failed":
            success = self.execute_task(current_task)
            if not success:
                if current_task.next_task_id_on_failure:
                    current_task = self.get_next_task_by_condition(current_task)
                else:
                    # If no failure path is defined and error propagation is needed,
                    # propagate the error to the workflow level
                    latest_error = self.error_context.get_latest_error()
                    self.workflow.set_error(
                        latest_error.get("error", "Task execution failed") if latest_error else "Task execution failed",
                        latest_error.get("error_code", ErrorCode.FRAMEWORK_WORKFLOW_ERROR) if latest_error else ErrorCode.FRAMEWORK_WORKFLOW_ERROR
                    )
                    
                    self.workflow.set_status("failed")
                    log_workflow_end(self.workflow.id, self.workflow.name, "failed")
                    break
            else:
                current_task = self.get_next_task_by_condition(current_task)
                
        if self.workflow.status != "failed":
            self.workflow.set_status("completed")
            log_workflow_end(self.workflow.id, self.workflow.name, "completed")
            
        # Include error summary in the result if there were errors
        error_summary = None
        if self.error_context.task_errors:
            error_summary = self.error_context.get_error_summary()
            
        return {
            "workflow_id": self.workflow.id,
            "workflow_name": self.workflow.name,
            "status": self.workflow.status,
            "tasks": {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()},
            "error_summary": error_summary
        }
