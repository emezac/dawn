#!/usr/bin/env python3
"""
Workflow Engine for the AI Agent Framework.

This module provides the engine that executes workflows by processing
tasks in the correct order, handling dependencies, and managing execution.
"""  # noqa: D202

import re
import json # Import json for parsing default values
import asyncio
from typing import Any, Dict, Optional, Callable, Union
import traceback # Add traceback import

# Core imports
from core.llm.interface import LLMInterface
# Import specific task types needed for dispatching
from core.task import Task, DirectHandlerTask, TaskOutput, validate_output_format # Ensure TaskOutput is imported
from core.tools.registry import ToolRegistry
from core.workflow import Workflow
# --- IMPORT ErrorCode CORRECTAMENTE ---
from core.errors import ErrorCode, DawnError # Ensure DawnError is imported if used
# ------------------------------------
from core.error_propagation import ErrorContext
# Assuming ServiceContainer might be type hinted, import if necessary
# from core.services import ServiceContainer

# Logging utilities
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

# --- WorkflowEngine Class ---
class WorkflowEngine:
    """
    Engine for executing workflows defined by Tasks.

    Handles task sequencing, dependency resolution (implicitly via order + variable resolution),
    input/output variable passing, conditional branching, retries, and execution via
    different strategies (Tools, Handlers, LLMs).
    """  # noqa: D202

    def __init__(
        self,
        workflow: Workflow,
        llm_interface: "LLMInterface",
        tool_registry: "ToolRegistry",
        services: "ServiceContainer" = None, # Use forward reference if ServiceContainer defined later/elsewhere
    ):
        """
        Initializes the WorkflowEngine.

        Args:
            workflow: The Workflow object to be executed.
            llm_interface: An instance conforming to LLMInterface for LLM tasks.
            tool_registry: An instance of ToolRegistry containing available tools.
            services: Optional container for shared services (like HandlerRegistry).
        """
        if not isinstance(workflow, Workflow):
            raise TypeError("workflow must be an instance of Workflow")
        if not isinstance(llm_interface, LLMInterface): # Assuming LLMInterface is the base/protocol
             raise TypeError("llm_interface must be an instance implementing LLMInterface")
        if not isinstance(tool_registry, ToolRegistry):
             raise TypeError("tool_registry must be an instance of ToolRegistry")

        self.workflow = workflow
        self.llm_interface = llm_interface
        self.tool_registry = tool_registry
        # Ensure services attribute exists, even if None
        self.services = services
        # Attempt to get handler_registry from services if available
        self.handler_registry = getattr(services, 'handler_registry', None)
        if self.handler_registry is None:
             log_warning("HandlerRegistry not found in services. DirectHandlerTasks using handler_name may fail.") # Adjusted warning


        # Initialize error context for tracking errors across tasks
        self.error_context = ErrorContext(workflow_id=workflow.id)

        # Initialize the condition evaluation helper functions
        self._condition_helper_funcs: Dict[str, Callable] = {}

        log_info(f"WorkflowEngine initialized for workflow '{workflow.name}' (ID: {workflow.id})")
        if self.tool_registry and hasattr(self.tool_registry, 'tools'):
            log_info(f"Using ToolRegistry instance {id(tool_registry)} with tools: {list(self.tool_registry.tools.keys())}")
        else:
             log_warning("ToolRegistry provided, but 'tools' attribute not found or inaccessible.") # Adjusted warning


    def register_condition_helper(self, name: str, function: Callable) -> None:
        """Registers a helper function accessible during condition evaluation."""
        if not isinstance(name, str) or not name:
            log_error("Condition helper name must be a non-empty string.")
            return
        if not callable(function):
            log_error(f"Cannot register non-callable object as condition helper '{name}'.")
            return

        if name in self._condition_helper_funcs:
            log_info(f"Replacing existing condition helper function '{name}'")
        self._condition_helper_funcs[name] = function
        log_info(f"Registered condition helper function '{name}'")

    def _build_condition_context(self, task: Task) -> Dict[str, Any]:
        """Builds the context dictionary for evaluating a task's condition."""
        context = {
            "output_data": task.output_data,
            "task": task.to_dict(),
            "workflow_id": self.workflow.id,
            "workflow_name": self.workflow.name,
            "task_id": task.id,
            "task_status": task.status,
        }
        context.update(self._condition_helper_funcs)
        task_outputs = {}
        for task_id, other_task in self.workflow.tasks.items():
            task_outputs[task_id] = other_task.output_data if other_task.status == "completed" else None
        context["task_outputs"] = task_outputs
        context["workflow_vars"] = getattr(self.workflow, "variables", {})
        return context

    def process_task_input(self, task: Task) -> Dict[str, Any]:
        """
        Resolves variable references in a task's input data, including defaults.

        Format: ${variable_name} or ${task_id.output_path} or ${var:default_value}
                Default value can be string, or JSON for list/dict/bool/null.
        """
        original_input = task.input_data.copy() if isinstance(task.input_data, dict) else {}
        processed_input = {}
        log_info(f"[PROCESS_INPUT:{task.id}] Original input: {original_input}")

        # Build the context for resolution
        resolution_context = {}
        if hasattr(self.workflow, 'variables') and isinstance(self.workflow.variables, dict):
             resolution_context.update(self.workflow.variables)
        for task_id, t in self.workflow.tasks.items():
            # Ensure the task has output data and it's likely a TaskOutput object
            if t.status in ["completed", "failed"] and t.id != task.id and hasattr(t, 'output_data') and t.output_data:
                 # Use the dictionary representation of the output for resolution
                 if hasattr(t.output_data, 'to_dict') and callable(t.output_data.to_dict):
                     resolution_context[task_id] = t.output_data.to_dict()
                 elif isinstance(t.output_data, dict):
                     resolution_context[task_id] = t.output_data # Already a dict
                 else:
                      log_warning(f"[PROCESS_INPUT] Task '{t.id}' output_data is not a dict or TaskOutput object, skipping for context.")

        resolution_context['error'] = self.error_context.task_errors

        # --- Import resolve_path here ---
        try:
            from core.utils.variable_resolver import resolve_path
        except ImportError:
            log_error("[PROCESS_INPUT] CRITICAL: Failed to import resolve_path utility. Variable resolution cannot proceed.", exc_info=True)
            raise ImportError("Failed to import resolve_path for input processing.")
        # --------------------------------

        # --- Loop through input items ---
        for key, value in original_input.items():
            processed_value = value # Default to original

            if isinstance(value, str) and "${" in value:
                log_info(f"[PROCESS_INPUT:{task.id}] Found potential reference(s) in key '{key}': {value}")
                current_value_str = value
                resolution_occurred_for_key = False # Track if *any* substitution happened for this key

                # Find all placeholders like ${...}
                matches = re.findall(r"\${([^}]+)}", value)

                for match_expression_full in matches: # e.g., "var", "task.result", "var:default"
                    log_info(f"[PROCESS_INPUT:{task.id}] Evaluating reference: '{match_expression_full}'")

                    # Separate variable path and potential default value string
                    match_parts = match_expression_full.split(':', 1)
                    match_expression = match_parts[0].strip() # Variable path
                    default_value_str = match_parts[1].strip() if len(match_parts) > 1 else None

                    resolved_part = None
                    found_part = False # Indicates if resolution (or default) was successful
                    resolution_failed_permanently = False # Indicates fatal error like ImportError

                    try:
                        # ---- Check for top-level variable first ----
                        if '.' not in match_expression and match_expression in resolution_context:
                            resolved_part = resolution_context[match_expression]
                            found_part = True
                            log_info(f"[PROCESS_INPUT:{task.id}] Resolved top-level variable '{match_expression}' to type: {type(resolved_part)}")
                        else:
                            # ---- Attempt nested path resolution ----
                            resolved_part = resolve_path(resolution_context, match_expression)
                            found_part = True # Found (even if value is None)
                            log_info(f"[PROCESS_INPUT:{task.id}] Resolved nested path '{match_expression}' to type: {type(resolved_part)}")

                    except (KeyError, IndexError, AttributeError, TypeError, ValueError) as e:
                        # Variable not found (neither top-level nor nested), check for default
                        log_warning(f"[PROCESS_INPUT:{task.id}] Could not resolve '{match_expression}' (checked top-level and nested): {type(e).__name__}. Checking for default.")
                        if default_value_str is not None:
                             try:
                                # Try parsing default as JSON (handles lists, dicts, bools, null)
                                # Use lower() for case-insensitive true/false/null
                                if default_value_str.startswith(('[', '{')) or default_value_str.lower() in ['true', 'false', 'null']:
                                    resolved_part = json.loads(default_value_str.lower())
                                else:
                                    # Assume string literal if not JSON-like
                                    resolved_part = default_value_str # Keep as string
                                log_info(f"[PROCESS_INPUT:{task.id}] Using default value for '{match_expression}': {resolved_part} (Type: {type(resolved_part)})")
                                found_part = True # Default value counts as finding a value
                             except json.JSONDecodeError:
                                 log_warning(f"[PROCESS_INPUT:{task.id}] Default value '{default_value_str}' for '{match_expression}' looks like JSON but failed to parse. Using as string.")
                                 resolved_part = default_value_str # Use as string if JSON parse fails
                                 found_part = True
                             except Exception as e_def:
                                 log_error(f"[PROCESS_INPUT:{task.id}] Error processing default value '{default_value_str}' for '{match_expression}': {e_def}")
                                 found_part = False # Failed to process default
                        # else: No default provided, found_part remains False

                    except ImportError: # Should have been caught before loop, but safety check
                         log_error("[PROCESS_INPUT:{task.id}] Failed to import resolve_path utility during loop.", exc_info=True)
                         resolution_failed_permanently = True
                         break # Exit match loop for this key
                    except Exception as e:
                         log_error(f"[PROCESS_INPUT:{task.id}] Unexpected error resolving reference '${{{match_expression}}}': {e}", exc_info=True)
                         resolution_failed_permanently = True
                         break # Exit match loop for this key

                    # --- Perform substitution if value found ---
                    if found_part:
                        placeholder = f"${{{match_expression_full}}}" # Use the full original placeholder
                        # Check if the entire original string was just this placeholder
                        if value == placeholder: # Compare with original 'value' for this key
                            processed_value = resolved_part # Assign the resolved object directly
                            resolution_occurred_for_key = True
                            log_info(f"[PROCESS_INPUT:{task.id}] Replaced entire value for key '{key}' with resolved/default object.")
                            # Since the whole value is replaced, no need to check other matches for this key
                            break # Exit the 'for match_expression_full...' loop
                        else:
                            # Substitute within the string (convert resolved part to string)
                            try:
                                replacement_str = str(resolved_part)
                            except Exception:
                                replacement_str = f"<{type(resolved_part).__name__}_obj>" # Fallback representation
                            # Use current_value_str for iterative replacement within the same value string
                            current_value_str = current_value_str.replace(placeholder, replacement_str)
                            processed_value = current_value_str # Update the potential final value
                            resolution_occurred_for_key = True
                            log_info(f"[PROCESS_INPUT:{task.id}] Replaced substring '{placeholder}' in key '{key}'. New intermediate value: '{current_value_str}'")
                    # else: No value found and no default, leave the placeholder ${...} in the string

                # --- End of loop for matches in the value string ---
                if resolution_failed_permanently:
                     log_error(f"[PROCESS_INPUT:{task.id}] Aborted resolution for key '{key}' due to fatal error. Reverting to original value.")
                     processed_value = value # Revert to original if fatal error occurred

            # --- Assign the final processed value for this key ---
            processed_input[key] = processed_value

        log_info(f"[PROCESS_INPUT:{task.id}] Final processed input: {processed_input}")
        return processed_input


    def handle_task_failure(self, task: Task, failure_output: TaskOutput) -> bool:
        """Handles task failure, including retry logic and recording errors."""
        task.set_output(failure_output) # failure_output is already a TaskOutput object
        # Record the error using the guaranteed dictionary format from the TaskOutput
        self.error_context.record_task_error(task.id, failure_output.to_dict())

        if task.can_retry():
            task.increment_retry()
            log_task_retry(task.id, task.name, task.retry_count, task.max_retries)
            task.set_status("pending")
            return True # Workflow continues, retry will happen
        else:
            log_task_end(task.id, task.name, "failed", self.workflow.id) # Log permanent failure
            if task.next_task_id_on_failure:
                 log_info(f"Task '{task.id}' failed permanently, proceeding to failure path '{task.next_task_id_on_failure}'.")
                 return True # Workflow continues on failure path
            else:
                 log_error(f"Task '{task.id}' failed permanently with no retries/failure path. Workflow stopping.")
                 return False # Workflow stops


    def get_next_task_id(self, current_task: Task) -> Optional[str]:
        """Determines the ID of the next task based on status and conditions."""
        next_task_id: Optional[str] = None

        if current_task.status == "completed":
            next_task_id = current_task.next_task_id_on_success
            if current_task.condition:
                log_info(f"Evaluating condition for task '{current_task.id}': {current_task.condition}")
                try:
                    eval_context = self._build_condition_context(current_task)
                    safe_builtins = {"True": True, "False": False, "None": None}
                    condition_result = eval(current_task.condition, {"__builtins__": safe_builtins}, eval_context)
                    log_info(f"Condition evaluated to: {condition_result}")

                    if isinstance(condition_result, bool):
                        next_task_id = current_task.next_task_id_on_success if condition_result else current_task.next_task_id_on_failure
                    elif isinstance(condition_result, str) and condition_result: # Allow condition to return next task ID string
                         log_info(f"Condition returned specific next task ID: '{condition_result}'")
                         next_task_id = condition_result
                    # else: Keep default success path if condition result is not bool or string

                except Exception as e:
                    log_error(f"Error evaluating condition for task '{current_task.id}': {e}. Defaulting to failure path.", exc_info=True)
                    next_task_id = current_task.next_task_id_on_failure

        elif current_task.status == "failed":
            next_task_id = current_task.next_task_id_on_failure
        # else: status is pending/running/skipped, no next task determined yet

        log_info(f"Next task ID determined for '{current_task.id}' (status: {current_task.status}): '{next_task_id}'")
        return next_task_id


    def _get_task_by_id(self, task_id: str) -> Optional[Task]:
         """Safely retrieves a task object from the workflow by its ID."""
         # Prefer workflow's get_task method if available
         if hasattr(self.workflow, "get_task") and callable(getattr(self.workflow, "get_task")):
              task = self.workflow.get_task(task_id)
              if task is None:
                  log_error(f"Workflow.get_task('{task_id}') returned None.")
              return task
         # Fallback to accessing tasks dictionary
         elif hasattr(self.workflow, "tasks") and isinstance(self.workflow.tasks, dict):
              task = self.workflow.tasks.get(task_id)
              if task is None:
                   log_error(f"Task ID '{task_id}' not found in workflow.tasks dictionary.")
              return task

         log_error(f"Cannot retrieve task '{task_id}'. Workflow object missing 'get_task' method or 'tasks' dictionary.")
         return None

    def run(self, initial_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes the workflow tasks respecting dependencies."""
        log_workflow_start(self.workflow.id, self.workflow.name)
        self.workflow.set_status("running")

        if initial_input:
            self.workflow.variables.update(initial_input)
            log_info(f"Initialized/Updated workflow variables: {self.workflow.variables}")

        completed_task_ids = set()
        # Get a mutable list of task IDs that need to be run
        tasks_to_process = list(self.workflow.task_order)
        task_map = self.workflow.tasks
        tasks_processed_in_pass = -1 # Ensure loop runs at least once

        # Loop until no tasks are left or no progress can be made
        while tasks_to_process and tasks_processed_in_pass != 0:
            tasks_processed_in_pass = 0
            remaining_tasks_for_next_pass = []
            runnable_tasks_this_pass = []

            # Identify all runnable tasks in the current list
            for task_id in tasks_to_process:
                task = task_map.get(task_id)
                if not task:
                    log_error(f"Task ID '{task_id}' in queue but not found in workflow tasks. Skipping.")
                    tasks_processed_in_pass += 1 # Count as processed to avoid infinite loop
                    continue

                dependencies = getattr(task, 'depends_on', [])
                if not isinstance(dependencies, list):
                    log_warning(f"Task '{task_id}' has non-list depends_on attribute: {dependencies}. Treating as no dependencies.")
                    dependencies = []

                # Check if all dependencies are met
                if all(dep_id in completed_task_ids for dep_id in dependencies):
                    runnable_tasks_this_pass.append(task)
                else:
                    # Dependencies not met, keep for the next pass
                    remaining_tasks_for_next_pass.append(task_id)

            # --- Execute all runnable tasks found in this pass ---            
            for current_task in runnable_tasks_this_pass:
                tasks_processed_in_pass += 1
                log_task_start(current_task.id, current_task.name, self.workflow.id)
                task_output = None

                try:
                    # Process inputs (variable resolution)
                    processed_input = self.process_task_input(current_task)
                    current_task.processed_input = processed_input
                    log_task_input(current_task.id, processed_input)

                    # Execute task
                    task_result_raw = self.execute_task(current_task)

                    # Validate and standardize the raw output
                    if isinstance(task_result_raw, TaskOutput):
                        task_output = task_result_raw # Already a TaskOutput object
                    elif isinstance(task_result_raw, dict):
                        task_output = validate_output_format(task_result_raw)
                    else:
                        # Handle cases where execute_task returns neither dict nor TaskOutput
                        log_error(f"Task '{current_task.id}' execute_task returned unexpected type: {type(task_result_raw)}. Creating error output.")
                        task_output = TaskOutput(
                            success=False,
                            status="failed",
                            error=f"Task execution returned unexpected type: {type(task_result_raw)}",
                            result=task_result_raw,
                            error_code=ErrorCode.UNEXPECTED_OUTPUT_TYPE
                        )

                    # Now task_output is guaranteed to be a TaskOutput instance
                    current_task.set_output(task_output)
                    log_task_output(current_task.id, task_output.to_dict())

                    # Handle Task Completion/Failure based on the TaskOutput object
                    if task_output.success:
                        log_task_end(current_task.id, current_task.name, "completed", self.workflow.id)
                        completed_task_ids.add(current_task.id)
                    else:
                        log_task_end(current_task.id, current_task.name, "failed", self.workflow.id)
                        self.error_context.record_task_error(current_task.id, task_output.to_dict())
                        should_retry = self.handle_task_failure(current_task, task_output)
                        if should_retry:
                            log_task_retry(current_task.id, current_task.retries)
                            # Add back to the list for the next pass if retrying
                            remaining_tasks_for_next_pass.append(current_task.id)
                            tasks_processed_in_pass -= 1 # Don't count retry initiation as progress for stall detection
                        else:
                            if self.workflow.status != "failed":
                                self.workflow.set_error(
                                    f"Task '{current_task.id}' failed permanently.",
                                    ErrorCode.EXECUTION_TASK_FAILED,
                                    current_task.id
                                )
                            # Failed task is not added back, effectively removed

                except Exception as e:
                    error_msg = f"Engine error during task '{current_task.id}' execution: {type(e).__name__}: {e}"
                    log_error(error_msg, exc_info=True)
                    tb_str = traceback.format_exc()
                    # Ensure we create a TaskOutput here as well
                    task_output = TaskOutput(status="failed", success=False, error=error_msg, error_code=ErrorCode.ENGINE_ERROR, error_details={"traceback": tb_str})
                    current_task.set_output(task_output)
                    # Use the correct method: record_task_error
                    self.error_context.record_task_error(current_task.id, task_output.to_dict()) 
                    if self.workflow.status != "failed":
                        self.workflow.set_error(
                            f"Engine error during task '{current_task.id}'.",
                            ErrorCode.ENGINE_ERROR,
                            current_task.id
                        )
                    # Failed task is not added back

            # Update the list of tasks to process for the next iteration
            tasks_to_process = remaining_tasks_for_next_pass

        # --- End of main loop --- 

        # Check for stall condition (tasks remain but none were processed in the last pass)
        if tasks_to_process and tasks_processed_in_pass == 0:
            error_msg = f"Workflow stalled: Tasks {tasks_to_process} remain but cannot run. Check for circular dependencies or missing tasks."
            log_error(error_msg)
            if self.workflow.status != "failed":
                self.workflow.set_error(error_msg, ErrorCode.WORKFLOW_STALLED)

        # Final workflow status determination
        if self.workflow.status != "failed":
            all_tasks_in_workflow_completed = all(
                task.status == "completed" for task in self.workflow.tasks.values()
            )
            if all_tasks_in_workflow_completed:
                 self.workflow.set_status("completed")
            else:
                # If not explicitly failed but not all tasks completed, mark as failed
                self.workflow.set_status("failed")
                if not self.workflow.error:
                    self.workflow.set_error("Workflow finished but not all tasks completed successfully.", ErrorCode.WORKFLOW_INCOMPLETE)

        log_workflow_end(self.workflow.id, self.workflow.name, self.workflow.status)
        return self._get_final_result()

    def _get_final_result(self) -> Dict[str, Any]:
         """Constructs the final result dictionary for the workflow execution."""
         log_workflow_end(self.workflow.id, self.workflow.name, self.workflow.status) # Log end here

         error_summary = self.error_context.get_error_summary() if self.error_context.task_errors else None

         final_output = None
         # Determine final task ID more robustly
         final_task_id = getattr(self.workflow, 'final_task_id', None)
         if not final_task_id and hasattr(self.workflow, 'task_order') and self.workflow.task_order:
              # Find the last task in the order that actually completed or failed (was reached)
              for task_id in reversed(self.workflow.task_order):
                   task = self.workflow.tasks.get(task_id)
                   if task and task.status in ["completed", "failed"]:
                        final_task_id = task_id
                        break

         if final_task_id and final_task_id in self.workflow.tasks:
              final_output = self.workflow.tasks[final_task_id].output_data

         return {
            "success": self.workflow.status == "completed",
            "workflow_id": self.workflow.id,
            "workflow_name": self.workflow.name,
            "status": self.workflow.status,
            "final_output": final_output,
            "tasks": {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()},
            "error_summary": error_summary,
             "workflow_error": getattr(self.workflow, 'error', None), # Safely get error
             "failed_task_id": getattr(self.workflow, 'failed_task_id', None), # Safely get failed_task_id
        }


    # Alias execute to run
    def execute(self, workflow=None, initial_input=None):
        """Alias for the run method."""
        if workflow is not None:
            if not isinstance(workflow, Workflow):
                 raise TypeError("Provided workflow must be an instance of Workflow")
            self.workflow = workflow
            self.error_context = ErrorContext(workflow_id=workflow.id) # Reset error context too
            log_info(f"WorkflowEngine switched to execute new workflow '{workflow.name}' (ID: {workflow.id})")
        return self.run(initial_input=initial_input)
        
    def execute_task(self, task: Task) -> Union[TaskOutput, Dict, Any]: # Update return type hint
        """
        Execute a single task based on its type (DirectHandler, LLM, Tool).

        Returns:
            A TaskOutput object or a dictionary that can be standardized by validate_output_format.
            Can also return Any in case of unexpected failures before standardization.
        """
        try:
            resolved_input = task.processed_input # Use already processed input
            task.set_status("running")

            if isinstance(task, DirectHandlerTask):
                handler = None
                handler_source = "unknown"
                if callable(task.handler):
                    handler = task.handler
                    handler_source = "direct callable"
                elif task.handler_name and self.handler_registry:
                    handler = self.handler_registry.get_handler(task.handler_name)
                    handler_source = f"registry ('{task.handler_name}')"
                    if not handler: raise ValueError(f"Handler '{task.handler_name}' not found in registry.")
                elif task.handler_name:
                    raise ValueError(f"Handler '{task.handler_name}' requires registry, but registry not available.")
                else:
                    raise ValueError(f"DirectHandlerTask '{task.id}' has no valid handler specified.")
                
                log_info(f"Executing {handler_source} for task '{task.id}'")
                # Execute the handler
                raw_output = handler(task, resolved_input)
                # Return the raw output (dict expected, but could be TaskOutput)
                return raw_output 

            elif getattr(task, 'is_llm_task', False) and self.llm_interface:
                log_info(f"Executing LLM task '{task.id}'")
                # LLM Interface should ideally return a dict or TaskOutput
                raw_output = self.llm_interface.execute_llm_call(**resolved_input)
                return raw_output

            elif task.tool_name and self.tool_registry:
                tool_name = task.tool_name
                log_info(f"Executing tool '{tool_name}' for task '{task.id}'")
                if not self.tool_registry.tool_exists(tool_name):
                    raise ValueError(f"Tool '{tool_name}' not found in registry.")
                # ToolRegistry should ideally return a dict or TaskOutput
                raw_output = self.tool_registry.execute_tool(tool_name, resolved_input)
                return raw_output

            else:
                raise ValueError(f"Task '{task.id}' has unknown or incomplete execution configuration.")

        except Exception as e:
            log_error(f"Error during task '{task.id}' execution dispatch: {e}", exc_info=True)
            # Return an error dictionary to be standardized by the caller (run method)
            return {
                "success": False,
                "status": "failed",
                "error": f"Error executing task: {str(e)}",
                "error_code": ErrorCode.TASK_EXECUTION_ERROR,
                "error_type": type(e).__name__,
                "error_details": {"traceback": traceback.format_exc()}
            }