"""
Workflow Engine for the AI Agent Framework.

This module provides the engine that executes workflows by processing
tasks in the correct order, handling dependencies, and managing execution.
"""

import re
from typing import Any, Dict, Optional, Callable
import time

from core.llm.interface import LLMInterface
from core.task import Task
from core.tools.registry import ToolRegistry
from core.task_execution_strategy import TaskExecutionStrategyFactory
from core.utils.logger import (
    log_error,
    log_info,
    log_warning,
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
        
        # Initialize strategy factory for task execution strategies
        self.strategy_factory = TaskExecutionStrategyFactory(llm_interface, tool_registry)
        
        # Initialize the condition evaluation helper functions
        self._condition_helper_funcs = {}
        
        # Keep essential init logs
        log_info(f"WorkflowEngine initialized for workflow '{workflow.name}' (ID: {workflow.id})")
        log_info(f"Using ToolRegistry instance {id(tool_registry)} with tools: {list(tool_registry.tools.keys())}")

    def register_condition_helper(self, name: str, function: Callable) -> None:
        """Register a helper function for use in condition evaluation.
        
        Args:
            name: The name to use when calling the function from conditions
            function: The function to register
        """
        if name in self._condition_helper_funcs:
            log_info(f"Replacing existing condition helper function '{name}'")
        self._condition_helper_funcs[name] = function
        log_info(f"Registered condition helper function '{name}'")
        
    def _build_condition_context(self, task: Task) -> Dict[str, Any]:
        """Build a context dictionary for condition evaluation with safe variable access.
        
        Args:
            task: The task whose condition is being evaluated
            
        Returns:
            A dictionary with variable bindings for condition evaluation
        """
        context = {
            "output_data": task.output_data,  # Current task's output
            "task": task,  # Current task object (for advanced conditions)
            "workflow_id": self.workflow.id,  # Workflow ID
            "workflow_name": self.workflow.name,  # Workflow name
            "task_id": task.id,  # Current task ID (convenience)
            "task_status": task.status,  # Current task status (convenience)
        }
        
        # Add helper functions
        for func_name, func in self._condition_helper_funcs.items():
            context[func_name] = func
            
        # Add access to other task outputs with safety checks
        task_outputs = {}
        for task_id, other_task in self.workflow.tasks.items():
            if other_task.status == "completed":
                task_outputs[task_id] = other_task.output_data
            else:
                task_outputs[task_id] = None
        context["task_outputs"] = task_outputs
        
        # Add workflow variables 
        if hasattr(self.workflow, "variables") and isinstance(self.workflow.variables, dict):
            context["workflow_vars"] = self.workflow.variables
        else:
            context["workflow_vars"] = {}
            
        return context

    def process_task_input(self, task: Task) -> Dict[str, Any]:
        """
        Process a task's input data, resolving references to outputs of previous tasks.
        
        Args:
            task: The task whose input data should be processed
            
        Returns:
            Processed input data with resolved references
        """
        original_input = task.input_data.copy() if task.input_data else {}
        processed_input = original_input.copy()
        log_info(f"[PROCESS_INPUT:{task.id}] Original input: {original_input}")
        
        # Get all tasks that might be referenced
        completed_tasks = {
            task_id: t for task_id, t in self.workflow.tasks.items() 
            if t.status in ["completed", "failed"] and t.id != task.id
        }
        
        if not completed_tasks:
            log_info(f"[PROCESS_INPUT:{task.id}] No completed tasks to reference.")
            return processed_input
        
        # Process string values that might contain references
        for key, value in original_input.items(): # Iterate over original to avoid modifying during iteration
            if isinstance(value, str) and "${" in value:
                log_info(f"[PROCESS_INPUT:{task.id}] Found potential reference in key '{key}': {value}")
                # Look for references to task outputs
                matches = re.findall(r"\${([^}]+)}", value)
                current_value_in_processed = processed_input[key]
                replaced_something = False
                for match in matches:
                    log_info(f"[PROCESS_INPUT:{task.id}] Evaluating match: {match}")
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
                                        replaced_something = True
                                        break
                                    processed_input[key] = value.replace(f"${{{match}}}", str(error_value))
                    else:
                        # Standard task output reference
                        parts = match.split(".")
                        ref_task_id = parts[0]
                        log_info(f"[PROCESS_INPUT:{task.id}] Referenced task ID: {ref_task_id}")
                        
                        if ref_task_id in completed_tasks:
                            ref_task = completed_tasks[ref_task_id]
                            log_info(f"[PROCESS_INPUT:{task.id}] Found ref_task '{ref_task_id}' with status '{ref_task.status}'")
                            # Extract the referenced field from the task output
                            field = ".".join(parts[1:]) if len(parts) > 1 else None
                            log_info(f"[PROCESS_INPUT:{task.id}] Referenced field: {field}")
                            try:
                                if field:
                                    # Check if the field is specifically 'output_data'
                                    if field == 'output_data':
                                        replacement = ref_task.output_data
                                    else:
                                        replacement = ref_task.get_output_value(field)
                                else:
                                    # Default to getting the full 'result' or 'response' if no field specified
                                    replacement = ref_task.get_output_value("result") # Prioritize result
                                    if replacement is None:
                                        replacement = ref_task.get_output_value("response") # Fallback to response
                                
                                log_info(f"[PROCESS_INPUT:{task.id}] Resolved value for '{match}': {type(replacement)} {str(replacement)[:100]}...")
                                
                                if replacement is not None:
                                    # Check if the entire value is the variable
                                    if current_value_in_processed == f"${{{match}}}":
                                        log_info(f"[PROCESS_INPUT:{task.id}] Replacing entire value for key '{key}'")
                                        processed_input[key] = replacement
                                        replaced_something = True
                                        # Since the entire value was replaced, break from inner loop for this key
                                        break 
                                    else:
                                        # Replace the variable within the string
                                        log_info(f"[PROCESS_INPUT:{task.id}] Replacing substring for key '{key}'")
                                        processed_input[key] = current_value_in_processed.replace(f"${{{match}}}", str(replacement))
                                        # Update current_value_in_processed for potential further replacements in the same string
                                        current_value_in_processed = processed_input[key]
                                        replaced_something = True
                                else:
                                     log_warning(f"[PROCESS_INPUT:{task.id}] Resolved value for '{match}' was None.")
                            except Exception as e:
                                log_error(f"[PROCESS_INPUT:{task.id}] Error resolving reference ${{{match}}}: {str(e)}")
                        else:
                             log_warning(f"[PROCESS_INPUT:{task.id}] Referenced task '{ref_task_id}' not found or not completed/failed.")
            else:
                 log_info(f"[PROCESS_INPUT:{task.id}] Key '{key}' is not a string or doesn't contain '${{'")
        
        log_info(f"[PROCESS_INPUT:{task.id}] Final processed input: {processed_input}")
        return processed_input

    def execute_task(self, task: Task) -> bool:
        """
        Execute a task and return whether it was successful.

        This method handles different types of tasks using the strategy pattern.

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

        try:
            # Get the appropriate strategy for the task
            strategy = self.strategy_factory.get_strategy(task)
            
            # Execute the task using the strategy
            import asyncio
            # Since the strategies are defined to work async, we need to run them in an event loop
            execution_result = asyncio.run(strategy.execute(task, processed_input=processed_input))

            if execution_result.get("success"):
                task.set_status("completed")
                output_key = "response" if task.is_llm_task else "result"
                # Ensure we have a complete output with both result and response
                output_data = execution_result.copy()
                if "result" in execution_result and "response" not in execution_result:
                    output_data["response"] = execution_result["result"]
                elif "response" in execution_result and "result" not in execution_result:
                    output_data["result"] = execution_result["response"]
                
                task.set_output(output_data)
                log_task_end(task.id, task.name, "completed", self.workflow.id)
                return True
            else:
                return self.handle_task_failure(task, execution_result)
        except Exception as e:
            log_error(
                f"Unhandled exception during execution wrapper for task '{task.id}': {e}",
                exc_info=True,
            )
            return self.handle_task_failure(task, {"error": f"Unhandled engine error: {str(e)}"})

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
        Determine the next task to execute based on the current task's condition or status.
        
        Args:
            current_task: The current task that has completed execution
            
        Returns:
            The next task to execute, or None if workflow should end
        """
        if current_task.status == "completed" and current_task.condition:
            # Evaluate condition to determine next task
            try:
                # Build a rich context for condition evaluation
                eval_context = self._build_condition_context(current_task)
                
                # Create a restricted builtins dict with only safe operations
                safe_builtins = {
                    "True": True, "False": False, "None": None,
                    "abs": abs, "all": all, "any": any, "bool": bool, 
                    "dict": dict, "float": float, "int": int, "len": len,
                    "list": list, "max": max, "min": min, "round": round,
                    "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
                    "type": type
                }
                
                # Execute the condition with the prepared context
                condition_met = bool(
                    eval(
                        current_task.condition,
                        {"__builtins__": safe_builtins},
                        eval_context
                    )
                )
                log_info(f"Condition '{current_task.condition}' for task '{current_task.id}' evaluated to: {condition_met}")
                
                next_task_id = current_task.next_task_id_on_success if condition_met else current_task.next_task_id_on_failure
            except Exception as e:
                log_error(f"Error evaluating condition for task {current_task.id}: {str(e)}. Defaulting to failure path.")
                next_task_id = current_task.next_task_id_on_failure
        else:
            # Use success/failure IDs based on task status
            if current_task.status == "completed":
                next_task_id = current_task.next_task_id_on_success
            else:
                next_task_id = current_task.next_task_id_on_failure
        
        # Get the next task if defined - safely access tasks dictionary
        if next_task_id:
            # First try using get_task method if it exists
            if hasattr(self.workflow, "get_task") and callable(getattr(self.workflow, "get_task")):
                return self.workflow.get_task(next_task_id)
            # Otherwise access the tasks dictionary directly
            else:
                return self.workflow.tasks.get(next_task_id)
        else:
            # End of workflow or branch
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

    def execute(self, workflow=None, execution_context=None):
        """
        Execute the workflow (alias for run method).
        
        Args:
            workflow: Optional workflow to execute (otherwise uses self.workflow)
            execution_context: Optional execution context (otherwise uses self.execution_context)
            
        Returns:
            Dictionary containing the result of the workflow execution
        """
        # If workflow is provided, update the instance
        if workflow is not None:
            self.workflow = workflow
            
        # If execution_context is provided, update the instance
        if execution_context is not None:
            self.execution_context = execution_context
            
        # Call the run method
        return self.run()
