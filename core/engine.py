#!/usr/bin/env python3
"""
Workflow Engine for the AI Agent Framework.

This module provides the engine that executes workflows by processing
tasks in the correct order, handling dependencies, and managing execution.
"""  # noqa: D202

import re
import json # Import json for parsing default values
import asyncio
from typing import Any, Dict, Optional, Callable

# Core imports
from core.llm.interface import LLMInterface
# Import specific task types needed for dispatching
from core.task import Task, DirectHandlerTask, TaskOutput # Ensure TaskOutput is imported
from core.tools.registry import ToolRegistry
from core.workflow import Workflow
# --- IMPORT ErrorCode CORRECTAMENTE ---
from core.errors import ErrorCode # Asegúrate que ErrorCode se importe desde aquí
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
            if t.status in ["completed", "failed"] and t.id != task.id:
                 resolution_context[task_id] = t.output_data
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
                        # Attempt to resolve the main variable path
                        resolved_part = resolve_path(resolution_context, match_expression)
                        found_part = True # Found (even if value is None)
                        log_info(f"[PROCESS_INPUT:{task.id}] Resolved '{match_expression}' to type: {type(resolved_part)}")

                    except (KeyError, IndexError, AttributeError, TypeError, ValueError) as e:
                        # Variable not found, check for default
                        log_warning(f"[PROCESS_INPUT:{task.id}] Could not resolve '{match_expression}': {type(e).__name__}. Checking for default.")
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
        """Handles task failure, including retries and final failure state."""
        task.set_output(failure_output) # Ensure task state reflects failure
        self.error_context.record_task_error(task.id, task.output_data)

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
        """
        Executes the defined workflow sequentially based on task order and branching.
        """
        log_workflow_start(self.workflow.id, self.workflow.name)
        self.workflow.set_status("running")

        if initial_input is not None:
            if not hasattr(self.workflow, 'variables') or not isinstance(self.workflow.variables, dict):
                self.workflow.variables = {} # Initialize if needed
            self.workflow.variables.update(initial_input)
            log_info(f"Initialized/Updated workflow variables: {self.workflow.variables}")

        if not hasattr(self.workflow, 'task_order') or not self.workflow.task_order:
             log_error(f"Workflow '{self.workflow.id}' has no task_order defined. Cannot execute.")
             self.workflow.set_status("failed")
             self.workflow.set_error("Workflow has no task execution order defined.", ErrorCode.WORKFLOW_CONFIGURATION_ERROR) # Check ErrorCode name
             return self._get_final_result()

        current_task_id: Optional[str] = self.workflow.task_order[0]
        executed_task_ids = set() # Simple loop prevention

        while current_task_id is not None:
            # --- Loop Detection ---
            if current_task_id in executed_task_ids:
                  log_error(f"Workflow execution stopped due to potential loop (re-encountered task '{current_task_id}').")
                  self.workflow.set_status("failed")
                  self.workflow.set_error(f"Workflow loop detected at task '{current_task_id}'.", ErrorCode.WORKFLOW_EXECUTION_ERROR, task_id=current_task_id) # Check ErrorCode name
                  break
            executed_task_ids.add(current_task_id)
            # --------------------

            current_task = self._get_task_by_id(current_task_id)
            if current_task is None:
                log_error(f"Task ID '{current_task_id}' specified in task_order or branch not found. Stopping.")
                self.workflow.set_status("failed")
                self.workflow.set_error(f"Task '{current_task_id}' not found.", ErrorCode.WORKFLOW_CONFIGURATION_ERROR, task_id=current_task_id) # Check ErrorCode name
                break

            # Only execute tasks that are pending
            if current_task.status != "pending":
                log_info(f"Task '{current_task.id}' status is '{current_task.status}', skipping execution phase.")
                # Decide next step based on its *current* status
                next_task_id = self.get_next_task_id(current_task)
                current_task_id = next_task_id
                continue

            # --- Execute the pending task ---
            log_task_start(current_task.id, current_task.name, self.workflow.id)
            success = False
            output: Optional[Dict] = None # Ensure output is initialized

            try:
                # 1. Resolve Inputs
                resolved_input = self.process_task_input(current_task)
                current_task.set_status("running")

                # 2. Execute based on Type (Dispatch Logic)
                if isinstance(current_task, DirectHandlerTask):
                    handler_name = current_task.handler_name
                    handler = None
                    if callable(current_task.handler):
                         handler = current_task.handler
                         handler_source = "direct callable"
                    elif handler_name and self.handler_registry:
                         handler = self.handler_registry.get_handler(handler_name)
                         handler_source = f"registry lookup ('{handler_name}')"
                         if not handler: raise ValueError(f"Handler '{handler_name}' not found in registry.")
                    elif handler_name: raise ValueError(f"Handler '{handler_name}' needs registry, but registry not available.")
                    else: raise ValueError(f"DirectHandlerTask '{current_task.id}' misconfigured.")

                    log_info(f"Engine: Executing {handler_source} for task '{current_task.id}'")
                    # Assume handler signature is handler(task, input_data)
                    output = handler(current_task, resolved_input)

                elif getattr(current_task, 'is_llm_task', False):
                    if not self.llm_interface: raise RuntimeError(f"LLMInterface needed for '{current_task.id}'.")
                    log_info(f"Engine: Executing LLM task '{current_task.id}'")
                    prompt = resolved_input.get("prompt", "")
                    if not prompt: raise ValueError("Missing 'prompt' for LLM task.")
                    
                    # Create a copy of resolved_input without the prompt key to avoid passing it twice
                    other_params = resolved_input.copy()
                    other_params.pop("prompt", None)
                    
                    output = self.llm_interface.execute_llm_call(
                        prompt=prompt, # Pass required args
                        **other_params # Pass other resolved inputs as potential kwargs
                        # TODO: Map specific LLM args if needed, like temperature etc.
                    )

                elif current_task.tool_name:
                    if not self.tool_registry: raise RuntimeError(f"ToolRegistry needed for '{current_task.id}'.")
                    tool_name = current_task.tool_name
                    # Check tool existence using dictionary access
                    if not hasattr(self.tool_registry, 'tools') or tool_name not in self.tool_registry.tools:
                         raise ValueError(f"Tool '{tool_name}' not found in registry.")
                    log_info(f"Engine: Executing tool '{tool_name}' for task '{current_task.id}'")
                    output = self.tool_registry.execute_tool(tool_name, resolved_input)

                else:
                    raise TypeError(f"Task '{current_task.id}' has unknown execution type.")

                # 3. Process Output (Standardize and set status)
                current_task.set_output(output) # This now also sets task status internally
                success = current_task.output_data.get('success', False)
                        # --- DEBUG: Log output of think_analyze_plan ---
                if current_task.id == 'think_analyze_plan':
                    import pprint
                    print("\n--- DEBUG: Output data from 'think_analyze_plan' ---")
                    pprint.pprint(current_task.output_data)
                    print("--- END DEBUG ---\n")
                # ---------------------------------------------

            except Exception as e:
                # Catch errors during resolution, dispatch, or execution call
                import traceback
                log_error(f"Engine error executing task '{current_task.id}': {e}", exc_info=True)
                # Ensure task output reflects the engine-level error
                current_task.set_output({
                    "success": False,
                    "error": f"Engine execution error: {str(e)}",
                    "error_type": type(e).__name__,
                    "error_details": {"traceback": traceback.format_exc()},
                    "status": "failed" # Explicitly set status in output dict
                })
                success = False # Ensure success is False

            # --- Handle Task Outcome ---
            if success:
                 log_task_end(current_task.id, current_task.name, "completed", self.workflow.id)
                 next_task_id = self.get_next_task_id(current_task)
                 current_task_id = next_task_id # Move to next task ID
            else:
                 # Failure occurred
                 should_continue = self.handle_task_failure(current_task, current_task.output_data)
                 if should_continue:
                      # Check if retry was triggered (status reset to pending)
                      if current_task.status == "pending":
                           executed_task_ids.remove(current_task_id) # Allow re-execution
                           log_info(f"Task '{current_task_id}' will be retried.")
                           # Stay on the current task ID for the next loop iteration
                           continue
                      else:
                           # No retry, move to failure path if defined
                           next_task_id = self.get_next_task_id(current_task) # Gets failure path ID
                           current_task_id = next_task_id
                           log_info(f"Proceeding to failure path task: {current_task_id}")
                 else:
                      # Permanent failure, stop workflow.
                      self.workflow.set_status("failed")
                      latest_error = self.error_context.get_task_error(current_task.id)
                      # --- USE CORRECT ErrorCode ---
                      # Ensure EXECUTION_TASK_FAILED exists in core/errors.py
                      error_code_to_use = ErrorCode.EXECUTION_TASK_FAILED
                      # -----------------------------
                      self.workflow.set_error(
                            latest_error.get("error", f"Task '{current_task.id}' failed.") if latest_error else f"Task '{current_task.id}' failed.",
                            latest_error.get("error_code", error_code_to_use) if latest_error else error_code_to_use,
                            task_id=current_task.id # Pass task_id if set_error accepts it
                        )
                      current_task_id = None # Stop the loop

        # --- End of Workflow Loop ---
        if self.workflow.status != "failed":
             # If loop finished because current_task_id is None (natural end)
             if current_task_id is None:
                  self.workflow.set_status("completed")
             # else: loop might have exited due to other reasons (e.g., explicit stop command - not implemented here)

        return self._get_final_result() # Always return final result

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
        
    def execute_task(self, task):
        """
        Execute a single task for testing purposes.
        
        This method is provided for backward compatibility with tests.
        In production code, use run() which executes full workflows.
        
        Args:
            task: The task to execute
            
        Returns:
            bool: True if task executed successfully, False otherwise
        """
        try:
            log_info(f"Executing single task '{task.id}' for testing purposes")
            
            # Resolve inputs
            resolved_input = self.process_task_input(task)
            task.set_status("running")
            
            # Execute based on type
            if isinstance(task, DirectHandlerTask) and callable(task.handler):
                output = task.execute(resolved_input)
            elif getattr(task, 'is_llm_task', False):
                output = self.llm_interface.execute_llm_call(prompt=resolved_input.get("prompt", ""))
            elif task.tool_name:
                output = self.tool_registry.execute_tool(task.tool_name, resolved_input)
            else:
                raise ValueError(f"Task '{task.id}' has unknown execution type")
                
            # Process output
            task.set_output(output)
            success = task.output_data.get('success', False)
            
            return success
        except Exception as e:
            log_error(f"Error executing task '{task.id}': {e}")
            task.set_output({"success": False, "error": str(e), "status": "failed"})
            return False