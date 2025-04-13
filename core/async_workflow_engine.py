"""
Asynchronous workflow engine module for the AI Agent Framework.

This module provides an asynchronous execution engine for workflows, enabling
parallel task execution, conditional branching, and dynamic input/output handling.
It allows for efficient processing of complex workflows with interdependent tasks
and supports both LLM-based and tool-based operations within a single execution context.
"""

# core/async_workflow_engine.py
import asyncio
import copy  # Import deepcopy
import re
import importlib
from typing import Any, Dict, List, Optional, Callable

from core.llm.interface import LLMInterface
from core.task import Task
from core.task_execution_strategy import TaskExecutionStrategyFactory
from core.tools.registry import ToolRegistry
from core.handlers.registry import HandlerRegistry

# Assuming logger setup is done elsewhere and functions are imported
from core.utils.logger import (  # Keep imports
    log_error,
    log_info,
    log_task_end,
    log_task_retry,
    log_task_start,
    log_warning,
    log_workflow_end,
    log_workflow_start,
)
from core.workflow import Workflow


class AsyncWorkflowEngine:
    """Asynchronous engine for executing workflows with support for parallel tasks.

    This engine provides support for parallel tasks, conditional logic, and
    input/output variable substitution.
    """  # noqa: D202

    def __init__(
        self, 
        workflow: Workflow, 
        llm_interface: LLMInterface, 
        tool_registry: ToolRegistry,
        handler_registry: Optional[HandlerRegistry] = None
    ):
        """Initialize the asynchronous workflow engine.

        Args:
            workflow: The Workflow object to execute.
            llm_interface: An instance of LLMInterface for LLM tasks.
            tool_registry: An instance of ToolRegistry containing available tools.
            handler_registry: An optional HandlerRegistry for direct handler tasks.
        """
        self.workflow = workflow
        self.llm_interface = llm_interface
        self.tool_registry = tool_registry
        self.handler_registry = handler_registry
        self.strategy_factory = TaskExecutionStrategyFactory(llm_interface, tool_registry, handler_registry)
        
        # Initialize the condition evaluation helper functions
        self._condition_helper_funcs = {}
        
        # Keep essential init logs
        log_info(f"AsyncWorkflowEngine initialized for workflow '{workflow.name}' (ID: {workflow.id})")
        log_info(f"Using ToolRegistry instance {id(tool_registry)} with tools: {list(tool_registry.tools.keys())}")
        if handler_registry:
            log_info(f"Using HandlerRegistry with handlers: {handler_registry.list_handlers()}")

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

    def set_handler_registry(self, handler_registry: HandlerRegistry) -> None:
        """
        Set the handler registry to be used for direct handler tasks.
        
        Args:
            handler_registry: The HandlerRegistry instance to use
        """
        self.handler_registry = handler_registry
        # Update the strategy factory with the new handler registry
        self.strategy_factory = TaskExecutionStrategyFactory(
            self.llm_interface, 
            self.tool_registry, 
            handler_registry
        )
        log_info(f"Set HandlerRegistry with handlers: {handler_registry.list_handlers()}")

    def _resolve_value(self, ref_task_id: str, path_parts: List[str]) -> Any:
        """Helper to get a value from a referenced task's output."""
        # Minimal logging for resolution attemp
        # log_info(f"--> _resolve_value: Attempting to resolve {ref_task_id}.output_data.{'.'.join(path_parts)}")
        try:
            ref_task = self.workflow.get_task(ref_task_id)
            if ref_task.status != "completed":
                log_warning(
                    f"Substitution skipped: Referenced task '{ref_task_id}' status is "
                    f"'{ref_task.status}'. Cannot resolve value."
                )
                return None

            current_val = ref_task.output_data
            if not isinstance(current_val, dict):
                log_error(f"Substitution error: Output data for '{ref_task_id}' is not a dict.")
                return None

            # Simplified resolution assuming path_parts = ['result'] or ['response'] mostly
            if len(path_parts) == 1 and path_parts[0] in ["result", "response"]:
                key_to_get = path_parts[0]
                if key_to_get in current_val:
                    return current_val[key_to_get]
                else:
                    log_error(
                        f"Substitution error: Key '{key_to_get}' not found in " f"output_data for task '{ref_task_id}'."
                    )
                    return None
            else:  # Handle potential deeper nesting if needed (can be expanded)
                for i, part in enumerate(path_parts):
                    if isinstance(current_val, dict):
                        if part in current_val:
                            current_val = current_val[part]
                        else:
                            log_error(
                                f"Substitution error: Nested key '{part}' not found " f"for task '{ref_task_id}'."
                            )
                            return None
                    elif isinstance(current_val, list):  # Basic list index support
                        try:
                            index = int(part)
                            if 0 <= index < len(current_val):
                                current_val = current_val[index]
                            else:
                                log_error(
                                    f"Substitution error: Index '{index}' out of bounds " f"for task '{ref_task_id}'."
                                )
                                return None
                        except ValueError:
                            log_error(
                                f"Substitution error: Path part '{part}' not valid index " f"for task '{ref_task_id}'."
                            )
                            return None
                    else:
                        log_error(f"Substitution error: Cannot resolve part '{part}' " f"for task '{ref_task_id}'.")
                        return None
                return current_val

        except KeyError:
            log_error(f"Substitution error: Referenced task '{ref_task_id}' not found.")
            return None
        except Exception as e:
            log_error(f"Substitution error: Unexpected error resolving {ref_task_id}.{'.'.join(path_parts)}: {e}")
            return None

    def process_task_input(self, task: Task) -> Dict[str, Any]:
        """
        Processes input_data, resolving placeholders like ${task.output_data.key}.
        Uses re.fullmatch + strip() for exact placeholders.
        Uses simple capture + validation for partial placeholders.
        Operates on a deep copy of input_data.
        """
        if not isinstance(task.input_data, dict):
            # log_warning(f"Task '{task.id}' input_data is not a dictionary.") # Optional warning
            return copy.deepcopy(task.input_data or {})

        processed_input = copy.deepcopy(task.input_data)

        # log_info(f"--- Processing input for task '{task.id}' ---") # Reduce verbosity

        for key, value in processed_input.items():
            current_value_for_key = value

            # Process String Value
            if isinstance(current_value_for_key, str):
                value_stripped = current_value_for_key.strip()
                regex_exact = r"\${([^}]+)}"
                exact_match_obj = re.fullmatch(regex_exact, value_stripped)

                if exact_match_obj:  # Exact Placeholder Match
                    match_str = exact_match_obj.group(1)
                    parts = match_str.split(".")
                    if len(parts) >= 3 and parts[1] == "output_data":
                        ref_task_id = parts[0]
                        path_to_value = parts[2:]
                        resolved_value = self._resolve_value(ref_task_id, path_to_value)
                        if resolved_value is not None:
                            processed_input[key] = resolved_value  # Update copy
                            # log_info(f"  Key '{key}': Replaced exact placeholder with resolved value.") # Optional log
                        # else: Keep original on resolution failure (already in copy)
                        # log_error(f"  Key '{key}': Failed to resolve exact placeholder '{current_value_for_key}'.")
                    # else: Keep original on invalid format (already in copy)
                    # log_error(f"  Key '{key}': Invalid exact placeholder format '{current_value_for_key}'.")
                else:  # Partial Placeholder Substitution
                    partial_placeholder_regex = r"\${([^}]+)}"
                    placeholders_found = re.findall(partial_placeholder_regex, current_value_for_key)
                    if placeholders_found:
                        resolved_string = current_value_for_key
                        placeholder_substituted = False
                        for match_str in placeholders_found:
                            parts = match_str.split(".")
                            if len(parts) >= 3 and parts[1] == "output_data":
                                ref_task_id = parts[0]
                                path_to_value = parts[2:]
                                replacement_val = self._resolve_value(ref_task_id, path_to_value)
                                if replacement_val is not None:
                                    resolved_string = resolved_string.replace(f"${{{match_str}}}", str(replacement_val))
                                    placeholder_substituted = True
                                # else: log_error(f"  Key '{key}': Failed partial resolve for '${match_str}'.")
                            # else: log_warning(f"  Key '{key}': Captured content '{match_str}' invalid format.")
                        if placeholder_substituted:
                            processed_input[key] = resolved_string
                            # log_info(f"  Key '{key}': Finished partial substitution.")

            # Process List Value
            elif isinstance(current_value_for_key, list):
                new_list = []
                list_substituted = False
                for item_index, item in enumerate(current_value_for_key):
                    if isinstance(item, str):
                        item_stripped = item.strip()
                        regex_exact = r"\${([^}]+)}"
                        exact_match_obj = re.fullmatch(regex_exact, item_stripped)
                        if exact_match_obj:  # Exact placeholder in list item
                            match_str = exact_match_obj.group(1)
                            parts = match_str.split(".")
                            if len(parts) >= 3 and parts[1] == "output_data":
                                ref_task_id = parts[0]
                                path_to_value = parts[2:]
                                resolved_value = self._resolve_value(ref_task_id, path_to_value)
                                if resolved_value is not None:
                                    new_list.append(resolved_value)
                                    list_substituted = True
                                else:
                                    new_list.append(item)  # Keep original on failure
                            else:
                                new_list.append(item)  # Keep original on invalid format
                        else:
                            new_list.append(item)  # Keep non-placeholder strings
                    else:
                        new_list.append(item)  # Keep non-string items
                if list_substituted:
                    processed_input[key] = new_list
                    # log_info(f"  Key '{key}': Finished list processing with substitutions.")

            # else: Keep other types (handled implicitly by using copy)

        # log_info(f"--- Finished processing input for task '{task.id}'. Final: {processed_input} ---") # Reduce verbosity
        return processed_input

    async def async_execute_task(self, task: Task) -> bool:
        """Executes a single task, handles retries, sets output and status."""
        log_task_start(task.id, task.name, self.workflow.id)
        task.set_status("running")
        
        try:
            # Process the task input data
            processed_input = self.process_task_input(task)
            
            # Get the appropriate strategy for the task
            strategy = self.strategy_factory.get_strategy(task)
            
            # Execute the task using the strategy
            execution_result = await strategy.execute(task, processed_input=processed_input)

            if execution_result.get("success"):
                task.set_status("completed")
                output_key = "response" if task.is_llm_task else "result"
                task.set_output({output_key: execution_result.get(output_key)})
                log_task_end(task.id, task.name, "completed", self.workflow.id)
                return True
            else:
                return await self.async_handle_task_failure(task, execution_result)
        except Exception as e:
            log_error(
                f"Unhandled exception during execution wrapper for task '{task.id}': {e}",
                exc_info=True,
            )
            return await self.async_handle_task_failure(task, {"error": f"Unhandled engine error: {str(e)}"})

    async def async_handle_task_failure(self, task: Task, execution_result: Dict[str, Any]) -> bool:
        """Handle a task failure, including retries and workflow error handling."""
        retry_count = task.get_retry_count()
        max_retries = task.get_max_retries()

        if retry_count < max_retries:
            task.increment_retry_count()
            log_task_retry(task.id, task.name, retry_count + 1, max_retries)
            task.set_status("retrying")
            await asyncio.sleep(1)  # Small delay before retry
            return await self.async_execute_task(task)
        else:
            task.set_status("failed")
            error_message = execution_result.get("error", "Unknown error")
            task.set_output({"error": error_message})
            log_task_end(task.id, task.name, "failed", self.workflow.id, error_message)
            return False
            
    async def find_next_tasks(self, current_task: Task, success: bool = True) -> List[Task]:
        """Determine the next tasks to execute based on the current task's outcome.
        
        Args:
            current_task: The current Task that has completed execution
            success: Whether the current task completed successfully
            
        Returns:
            A list of Task objects to execute next
        """
        next_task_ids = []
        
        if success:
            # For successful tasks, use the normal transitions
            if current_task.id in self.workflow.transitions:
                next_task_ids = self.workflow.transitions[current_task.id]
        else:
            # For failed tasks, use the on_failure transitions if defined
            if hasattr(current_task, "on_failure") and current_task.on_failure:
                next_task_ids = [current_task.on_failure]
        
        next_tasks = []
        for task_id in next_task_ids:
            if task_id in self.workflow.tasks:
                next_tasks.append(self.workflow.tasks[task_id])
            else:
                log_warning(f"Invalid transition from '{current_task.id}' to non-existent task '{task_id}'")
        
        return next_tasks

    async def find_and_execute_next_tasks(self, current_task: Task, success: bool = True) -> None:
        """Find and execute the next tasks based on the current task's outcome.
        
        Args:
            current_task: The current Task that has completed execution
            success: Whether the current task completed successfully
        """
        next_tasks = await self.find_next_tasks(current_task, success)
        
        if not next_tasks:
            log_info(f"No next tasks found for task '{current_task.id}' (success={success})")
            return
            
        for next_task in next_tasks:
            # Schedule each next task for execution
            self.pending_tasks.append(next_task)

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

    def get_next_task_by_condition(self, current_task: Task) -> Optional[Task]:
        """Determines the next task based on status, condition, and branches."""
        next_task_id: Optional[str] = None
        current_task_index: int = -1
        try:
            current_task_index = self.workflow.task_order.index(current_task.id)
        except ValueError:
            log_error(f"Critical: Task '{current_task.id}' not found in workflow.task_order during navigation.")
            self.workflow.set_status("failed")
            return None

        condition_evaluated: bool = False
        condition_met: bool = False

        if current_task.status == "completed" and current_task.condition:
            condition_evaluated = True
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
            except Exception as e:
                log_error(
                    f"Error evaluating condition '{current_task.condition}' for task '{current_task.id}': {e}. Defaulting to failure path."
                )
                condition_met = False

            next_task_id = (
                current_task.next_task_id_on_success if condition_met else current_task.next_task_id_on_failure
            )
            log_info(f"Condition path selected for '{current_task.id}': '{next_task_id}'")

        elif not condition_evaluated:
            if current_task.status == "completed":
                next_task_id = current_task.next_task_id_on_success
            elif current_task.status == "failed":
                next_task_id = current_task.next_task_id_on_failure
            # if next_task_id: log_info(f"Status path selected for '{current_task.id}': '{next_task_id}'") # Optional log

        if next_task_id:
            if next_task_id in self.workflow.tasks:
                try:
                    next_task_index = self.workflow.task_order.index(next_task_id)
                    self.workflow.current_task_index = next_task_index
                    # log_info(f"Jumping workflow index to {next_task_index} for task '{next_task_id}'.") # Optional log
                    return self.workflow.tasks[next_task_id]
                except ValueError:
                    log_error(
                        f"Critical: Next task ID '{next_task_id}' (from '{current_task.id}') not in task_order. Stopping."
                    )
                    self.workflow.set_status("failed")
                    return None
            else:
                log_error(
                    f"Critical: Next task ID '{next_task_id}' (from '{current_task.id}') not in tasks dict. Stopping."
                )
                self.workflow.set_status("failed")
                return None
        else:
            next_sequential_index = current_task_index + 1
            if next_sequential_index < len(self.workflow.task_order):
                next_task_id_seq = self.workflow.task_order[next_sequential_index]
                # log_info(f"No jump from '{current_task.id}', proceeding sequentially to index {next_sequential_index} ('{next_task_id_seq}').") # Optional log
                self.workflow.current_task_index = next_sequential_index
                return self.workflow.tasks.get(next_task_id_seq)
            else:
                # log_info(f"Reached end of task order after task '{current_task.id}'.") # Optional log
                self.workflow.current_task_index = next_sequential_index
                return None

    def get_next_sequential_task(self) -> Optional[Task]:
        """Gets the next sequential task and increments index."""
        if self.workflow.current_task_index >= len(self.workflow.task_order):
            return None

        task_id = self.workflow.task_order[self.workflow.current_task_index]
        task = self.workflow.tasks.get(task_id)

        if not task:
            log_error(
                f"Task ID '{task_id}' from task_order index {self.workflow.current_task_index} not found. Skipping."
            )
            self.workflow.current_task_index += 1
            return self.get_next_sequential_task()
        else:
            self.workflow.current_task_index += 1
            return task

    async def async_run(self) -> Dict[str, Any]:
        """Runs the entire workflow asynchronously."""
        log_workflow_start(self.workflow.id, self.workflow.name)  # Keep start log
        self.workflow.set_status("running")
        self.workflow.current_task_index = 0
        executed_task_ids = set()

        while self.workflow.current_task_index < len(self.workflow.task_order) and self.workflow.status == "running":
            peek_task_id = self.workflow.task_order[self.workflow.current_task_index]
            current_task_peek = self.workflow.tasks.get(peek_task_id)

            if not current_task_peek:
                log_error(f"Task ID '{peek_task_id}' at index {self.workflow.current_task_index} not found. Stopping.")
                self.workflow.set_status("failed")
                break

            if current_task_peek.parallel:
                # --- Parallel Block ---
                parallel_tasks_to_run: List[Task] = []
                start_index = self.workflow.current_task_index
                while start_index < len(self.workflow.task_order):
                    task_id_in_block = self.workflow.task_order[start_index]
                    task_in_block = self.workflow.tasks.get(task_id_in_block)
                    if task_in_block and task_in_block.parallel:
                        parallel_tasks_to_run.append(task_in_block)
                        start_index += 1
                    else:
                        break

                if not parallel_tasks_to_run:
                    log_error(f"Parallel block empty at index {self.workflow.current_task_index}. Skipping.")
                    self.workflow.current_task_index += 1
                    continue

                log_info(
                    f"Starting parallel execution block: {[t.id for t in parallel_tasks_to_run]}"
                )  # Keep essential parallel log
                executed_task_ids.update(t.id for t in parallel_tasks_to_run)

                results = await asyncio.gather(
                    *(self.async_execute_task(task) for task in parallel_tasks_to_run),
                    return_exceptions=True,
                )

                block_failed = False
                last_task_in_block = parallel_tasks_to_run[-1]
                for i, gather_result in enumerate(results):
                    task = parallel_tasks_to_run[i]
                    if isinstance(gather_result, Exception) or not gather_result:
                        if task.status != "failed":  # Ensure status is updated if gather hid failure
                            await self.async_handle_task_failure(
                                task, {"error": f"Gather failure/exception: {gather_result}"}
                            )
                        block_failed = True

                self.workflow.current_task_index = start_index
                # log_info(f"Parallel block finished. Index at {self.workflow.current_task_index}.") # Optional log

                if block_failed:
                    log_error("Parallel block failed.")
                    self.workflow.set_status("failed")
                    # Navigate based on last task's failure
                    _ = self.get_next_task_by_condition(last_task_in_block)
                else:
                    # log_info(f"Parallel block success.") # Optional log
                    # Navigate based on last task's success/condition
                    _ = self.get_next_task_by_condition(last_task_in_block)
            else:
                # --- Sequential Execution ---
                task_to_execute = self.get_next_sequential_task()
                if task_to_execute is None:
                    break

                executed_task_ids.add(task_to_execute.id)
                success = await self.async_execute_task(task_to_execute)

                if not success:
                    log_error(f"Sequential task '{task_to_execute.id}' failed.")
                    self.workflow.set_status("failed")
                    _ = self.get_next_task_by_condition(task_to_execute)
                else:
                    _ = self.get_next_task_by_condition(task_to_execute)

        # --- Final Status Determination ---
        if self.workflow.status != "failed":
            if self.workflow.current_task_index >= len(self.workflow.task_order):
                all_executed_completed = all(
                    self.workflow.tasks[tid].status == "completed" for tid in executed_task_ids
                )
                if all_executed_completed:
                    # log_info("Workflow reached end and all executed tasks completed.") # Optional log
                    self.workflow.set_status("completed")
                else:
                    log_error("Workflow reached end, but not all executed tasks completed. Marking failed.")
                    self.workflow.set_status("failed")
            else:
                log_error(
                    f"Workflow loop exited unexpectedly at index {self.workflow.current_task_index}. Marking failed."
                )
                self.workflow.set_status("failed")

        # Log final status
        log_workflow_end(self.workflow.id, self.workflow.name, self.workflow.status)

        return {
            "workflow_id": self.workflow.id,
            "workflow_name": self.workflow.name,
            "status": self.workflow.status,
            "tasks": {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()},
        }

    async def run_workflow(self) -> bool:
        """Runs the entire workflow by executing starting tasks and following transitions."""
        log_workflow_start(self.workflow.id, self.workflow.name)
        
        # Start with workflow starting points
        self.pending_tasks = self.workflow.get_starting_tasks()
        
        # Keep executing tasks while there are pending tasks
        while self.pending_tasks:
            # Get next task to execute
            current_task = self.pending_tasks.pop(0)
            
            # Skip tasks already executed or in progress
            if current_task.status in ["completed", "failed", "in_progress"]:
                continue
                
            # Execute the current task
            success = await self.async_execute_task(current_task)
            
            # Find and schedule next tasks based on result
            await self.find_and_execute_next_tasks(current_task, success)
        
        # Check if workflow completed successfully (all tasks completed or terminal tasks reached)
        workflow_success = all(task.status == "completed" for task in self.workflow.tasks.values() 
                             if not task.is_optional)
        
        # Set workflow status
        status = "completed" if workflow_success else "failed"
        self.workflow.set_status(status)
        log_workflow_end(self.workflow.id, self.workflow.name, status)
        
        return workflow_success
