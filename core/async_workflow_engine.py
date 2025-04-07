# core/async_workflow_engine.py
import asyncio
import re
import copy # Import deepcopy
from typing import Dict, Any, Optional, List
from core.workflow import Workflow
from core.task import Task
from core.llm.interface import LLMInterface
from core.tools.registry import ToolRegistry
# Assuming logger setup is done elsewhere and functions are imported
from core.utils.logger import (
    log_workflow_start, log_workflow_end, log_task_start,
    log_task_end, log_task_retry, log_task_input,
    log_task_output, log_error, log_info, log_warning # Keep imports
)

class AsyncWorkflowEngine:
    """
    Asynchronous engine for executing workflows with support for parallel tasks,
    conditional logic, and input/output variable substitution.
    """
    def __init__(
        self,
        workflow: Workflow,
        llm_interface: LLMInterface,
        tool_registry: ToolRegistry
    ):
        """
        Initializes the asynchronous workflow engine.

        Args:
            workflow: The Workflow object to execute.
            llm_interface: An instance of LLMInterface for LLM tasks.
            tool_registry: An instance of ToolRegistry containing available tools.
        """
        self.workflow = workflow
        self.llm_interface = llm_interface
        self.tool_registry = tool_registry
        # Keep essential init logs
        log_info(f"AsyncWorkflowEngine initialized for workflow '{workflow.name}' (ID: {workflow.id})")
        log_info(f"Using ToolRegistry instance {id(tool_registry)} with tools: {list(tool_registry.tools.keys())}")


    def _resolve_value(self, ref_task_id: str, path_parts: List[str]) -> Any:
        """Helper to get a value from a referenced task's output."""
        # Minimal logging for resolution attempt
        # log_info(f"--> _resolve_value: Attempting to resolve {ref_task_id}.output_data.{'.'.join(path_parts)}")
        try:
            ref_task = self.workflow.get_task(ref_task_id)
            if ref_task.status != 'completed':
                log_warning(f"Substitution skipped: Referenced task '{ref_task_id}' status is '{ref_task.status}'. Cannot resolve value.")
                return None

            current_val = ref_task.output_data
            if not isinstance(current_val, dict):
                 log_error(f"Substitution error: Output data for '{ref_task_id}' is not a dict.")
                 return None

            # Simplified resolution assuming path_parts = ['result'] or ['response'] mostly
            if len(path_parts) == 1 and path_parts[0] in ['result', 'response']:
                key_to_get = path_parts[0]
                if key_to_get in current_val:
                    return current_val[key_to_get]
                else:
                    log_error(f"Substitution error: Key '{key_to_get}' not found in output_data for task '{ref_task_id}'.")
                    return None
            else: # Handle potential deeper nesting if needed (can be expanded)
                 for i, part in enumerate(path_parts):
                     if isinstance(current_val, dict):
                         if part in current_val: current_val = current_val[part]
                         else: log_error(f"Substitution error: Nested key '{part}' not found for task '{ref_task_id}'."); return None
                     elif isinstance(current_val, list): # Basic list index support
                         try:
                             index = int(part)
                             if 0 <= index < len(current_val): current_val = current_val[index]
                             else: log_error(f"Substitution error: Index '{index}' out of bounds for task '{ref_task_id}'."); return None
                         except ValueError: log_error(f"Substitution error: Path part '{part}' not valid index for task '{ref_task_id}'."); return None
                     else: log_error(f"Substitution error: Cannot resolve part '{part}' for task '{ref_task_id}'."); return None
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
                regex_exact = r'\${([^}]+)}'
                exact_match_obj = re.fullmatch(regex_exact, value_stripped)

                if exact_match_obj: # Exact Placeholder Match
                    match_str = exact_match_obj.group(1)
                    parts = match_str.split('.')
                    if len(parts) >= 3 and parts[1] == 'output_data':
                        ref_task_id = parts[0]; path_to_value = parts[2:]
                        resolved_value = self._resolve_value(ref_task_id, path_to_value)
                        if resolved_value is not None:
                            processed_input[key] = resolved_value # Update copy
                            # log_info(f"  Key '{key}': Replaced exact placeholder with resolved value.") # Optional log
                        # else: Keep original on resolution failure (already in copy)
                            # log_error(f"  Key '{key}': Failed to resolve exact placeholder '{current_value_for_key}'.")
                    # else: Keep original on invalid format (already in copy)
                        # log_error(f"  Key '{key}': Invalid exact placeholder format '{current_value_for_key}'.")
                else: # Partial Placeholder Substitution
                    partial_placeholder_regex = r'\${([^}]+)}'
                    placeholders_found = re.findall(partial_placeholder_regex, current_value_for_key)
                    if placeholders_found:
                        resolved_string = current_value_for_key
                        placeholder_substituted = False
                        for match_str in placeholders_found:
                             parts = match_str.split('.')
                             if len(parts) >= 3 and parts[1] == 'output_data':
                                 ref_task_id = parts[0]; path_to_value = parts[2:]
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
                         regex_exact = r'\${([^}]+)}'
                         exact_match_obj = re.fullmatch(regex_exact, item_stripped)
                         if exact_match_obj: # Exact placeholder in list item
                             match_str = exact_match_obj.group(1)
                             parts = match_str.split('.')
                             if len(parts) >= 3 and parts[1] == 'output_data':
                                 ref_task_id = parts[0]; path_to_value = parts[2:]
                                 resolved_value = self._resolve_value(ref_task_id, path_to_value)
                                 if resolved_value is not None:
                                     new_list.append(resolved_value)
                                     list_substituted = True
                                 else: new_list.append(item) # Keep original on failure
                             else: new_list.append(item) # Keep original on invalid format
                         else: new_list.append(item) # Keep non-placeholder strings
                     else: new_list.append(item) # Keep non-string items
                 if list_substituted:
                      processed_input[key] = new_list
                      # log_info(f"  Key '{key}': Finished list processing with substitutions.")

            # else: Keep other types (handled implicitly by using copy)

        # log_info(f"--- Finished processing input for task '{task.id}'. Final: {processed_input} ---") # Reduce verbosity
        return processed_input

    async def async_execute_llm_task(self, task: Task) -> Dict[str, Any]:
        """Executes an LLM task using the LLMInterface."""
        # log_task_input(task.id, task.input_data) # Log original input only if needed
        processed_input = self.process_task_input(task)
        # log_info(f"Processed input for LLM task '{task.id}': {processed_input}") # Reduce verbosity

        prompt = processed_input.get("prompt", "")
        if not prompt:
            log_error(f"No 'prompt' found in processed input for LLM task '{task.id}'.")
            return {"success": False, "error": "No prompt provided for LLM task"}
        try:
            result = await asyncio.to_thread(self.llm_interface.execute_llm_call, prompt)
            if result.get("success"):
                # log_task_output(task.id, result) # Log raw output only if needed
                return {"success": True, "response": result.get("response")}
            else:
                error_msg = result.get('error', 'Unknown LLM error')
                log_error(f"LLM task '{task.id}' failed: {error_msg}")
                return {"success": False, "error": error_msg}
        except Exception as e:
            log_error(f"Exception during async execution of LLM task '{task.id}': {e}", exc_info=True)
            return {"success": False, "error": f"Async execution wrapper error: {str(e)}"}


    async def async_execute_tool_task(self, task: Task) -> Dict[str, Any]:
        """Executes a tool task using the ToolRegistry."""
        # log_task_input(task.id, task.input_data) # Log original input only if needed
        processed_input = self.process_task_input(task)
        # log_info(f"Processed input for tool task '{task.id}' ('{task.tool_name}'): {processed_input}") # Reduce verbosity

        if not task.tool_name:
            log_error(f"No 'tool_name' specified for tool task '{task.id}'.")
            return {"success": False, "error": "Tool name not specified"}
        try:
            result = await asyncio.to_thread(self.tool_registry.execute_tool, task.tool_name, processed_input)
            if result.get("success"):
                # log_task_output(task.id, result) # Log raw output only if needed
                return {"success": True, "result": result.get("result")}
            else:
                error_msg = result.get('error', 'Unknown tool error')
                log_error(f"Tool task '{task.id}' ('{task.tool_name}') failed: {error_msg}")
                return {"success": False, "error": error_msg}
        except Exception as e:
            log_error(f"Exception during async execution of tool task '{task.id}' ('{task.tool_name}'): {e}", exc_info=True)
            return {"success": False, "error": f"Async execution wrapper error: {str(e)}"}


    async def async_execute_task(self, task: Task) -> bool:
        """Executes a single task, handles retries, sets output and status."""
        log_task_start(task.id, task.name, self.workflow.id) # Keep start log
        task.set_status("running")
        execution_result: Dict[str, Any] = {}

        try:
            if task.is_llm_task:
                execution_result = await self.async_execute_llm_task(task)
            else:
                execution_result = await self.async_execute_tool_task(task)

            if execution_result.get("success"):
                task.set_status("completed")
                output_key = "response" if task.is_llm_task else "result"
                task.set_output({output_key: execution_result.get(output_key)})
                log_task_end(task.id, task.name, "completed", self.workflow.id) # Keep end log
                return True
            else:
                return await self.async_handle_task_failure(task, execution_result)
        except Exception as e:
            log_error(f"Unhandled exception during execution wrapper for task '{task.id}': {e}", exc_info=True)
            return await self.async_handle_task_failure(task, {"error": f"Unhandled engine error: {str(e)}"})


    async def async_handle_task_failure(self, task: Task, result_data: Dict[str, Any]) -> bool:
        """Handles failed tasks, including retries."""
        error_message = result_data.get("error", "Unknown failure reason")

        if task.can_retry():
            task.increment_retry()
            log_task_retry(task.id, task.name, task.retry_count, task.max_retries) # Keep retry log
            task.set_status("pending")
            await asyncio.sleep(0.2)
            return await self.async_execute_task(task)
        else:
            task.set_status("failed")
            task.set_output({"error": error_message})
            log_task_end(task.id, task.name, "failed", self.workflow.id) # Keep end log (failed)
            return False


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
                condition_met = bool(eval(current_task.condition, {"__builtins__": {}}, {"output_data": current_task.output_data}))
                # log_info(f"Condition '{current_task.condition}' for task '{current_task.id}' evaluated to: {condition_met}") # Optional log
            except Exception as e:
                log_error(f"Error evaluating condition '{current_task.condition}' for task '{current_task.id}': {e}. Defaulting to failure path.")
                condition_met = False

            next_task_id = current_task.next_task_id_on_success if condition_met else current_task.next_task_id_on_failure
            # log_info(f"Condition path selected for '{current_task.id}': '{next_task_id}'") # Optional log

        elif not condition_evaluated:
            if current_task.status == "completed": next_task_id = current_task.next_task_id_on_success
            elif current_task.status == "failed": next_task_id = current_task.next_task_id_on_failure
            # if next_task_id: log_info(f"Status path selected for '{current_task.id}': '{next_task_id}'") # Optional log

        if next_task_id:
            if next_task_id in self.workflow.tasks:
                try:
                    next_task_index = self.workflow.task_order.index(next_task_id)
                    self.workflow.current_task_index = next_task_index
                    # log_info(f"Jumping workflow index to {next_task_index} for task '{next_task_id}'.") # Optional log
                    return self.workflow.tasks[next_task_id]
                except ValueError:
                    log_error(f"Critical: Next task ID '{next_task_id}' (from '{current_task.id}') not in task_order. Stopping.")
                    self.workflow.set_status("failed")
                    return None
            else:
                log_error(f"Critical: Next task ID '{next_task_id}' (from '{current_task.id}') not in tasks dict. Stopping.")
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
             log_error(f"Task ID '{task_id}' from task_order index {self.workflow.current_task_index} not found. Skipping.")
             self.workflow.current_task_index += 1
             return self.get_next_sequential_task()
        else:
             self.workflow.current_task_index += 1
             return task


    async def async_run(self) -> Dict[str, Any]:
        """Runs the entire workflow asynchronously."""
        log_workflow_start(self.workflow.id, self.workflow.name) # Keep start log
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
                    else: break

                if not parallel_tasks_to_run:
                    log_error(f"Parallel block empty at index {self.workflow.current_task_index}. Skipping.")
                    self.workflow.current_task_index += 1; continue

                log_info(f"Starting parallel execution block: {[t.id for t in parallel_tasks_to_run]}") # Keep essential parallel log
                executed_task_ids.update(t.id for t in parallel_tasks_to_run)

                results = await asyncio.gather(
                     *(self.async_execute_task(task) for task in parallel_tasks_to_run),
                     return_exceptions=True
                 )

                block_failed = False
                last_task_in_block = parallel_tasks_to_run[-1]
                for i, gather_result in enumerate(results):
                    task = parallel_tasks_to_run[i]
                    if isinstance(gather_result, Exception) or not gather_result:
                        if task.status != 'failed': # Ensure status is updated if gather hid failure
                             await self.async_handle_task_failure(task, {"error": f"Gather failure/exception: {gather_result}"})
                        block_failed = True

                self.workflow.current_task_index = start_index
                # log_info(f"Parallel block finished. Index at {self.workflow.current_task_index}.") # Optional log

                if block_failed:
                    log_error(f"Parallel block failed.")
                    self.workflow.set_status("failed")
                    _ = self.get_next_task_by_condition(last_task_in_block) # Navigate based on last task's failure
                else:
                    # log_info(f"Parallel block success.") # Optional log
                    _ = self.get_next_task_by_condition(last_task_in_block) # Navigate based on last task's success/condition
            else:
                # --- Sequential Execution ---
                task_to_execute = self.get_next_sequential_task()
                if task_to_execute is None: break

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
                     log_error(f"Workflow reached end, but not all executed tasks completed. Marking failed.")
                     self.workflow.set_status("failed")
            else:
                 log_error(f"Workflow loop exited unexpectedly at index {self.workflow.current_task_index}. Marking failed.")
                 self.workflow.set_status("failed")

        # Log final status
        log_workflow_end(self.workflow.id, self.workflow.name, self.workflow.status)

        return {
            "workflow_id": self.workflow.id,
            "workflow_name": self.workflow.name,
            "status": self.workflow.status,
            "tasks": {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()}
        }