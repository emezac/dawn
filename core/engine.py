"""
Workflow Engine for the AI Agent Framework.

This module provides the engine that executes workflows by processing
tasks in the correct order, handling dependencies, and managing execution.
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
    """
    
    def __init__(
        self, 
        workflow: Workflow, 
        llm_interface: LLMInterface, 
        tool_registry: ToolRegistry
    ):
        self.workflow = workflow
        self.llm_interface = llm_interface
        self.tool_registry = tool_registry
    
    def process_task_input(self, task: Task) -> Dict[str, Any]:
        """
        Resolve references to outputs of other tasks in the task's input data.
        """
        processed_input = task.input_data.copy()
        for key, value in processed_input.items():
            if isinstance(value, str):
                matches = re.findall(r'\${([^}]+)}', value)
                for match in matches:
                    parts = match.split('.')
                    if len(parts) >= 2:
                        ref_task_id = parts[0]
                        try:
                            ref_task = self.workflow.get_task(ref_task_id)
                            if len(parts) == 2 and parts[1] == 'output_data':
                                replacement = ref_task.output_data
                                if value == f"${{{match}}}":
                                    processed_input[key] = replacement
                                    break
                                processed_input[key] = value.replace(f"${{{match}}}", str(replacement))
                            elif len(parts) >= 3 and parts[1] == 'output_data':
                                field = parts[2]
                                if field in ref_task.output_data:
                                    replacement = ref_task.output_data[field]
                                    if value == f"${{{match}}}":
                                        processed_input[key] = replacement
                                        break
                                    processed_input[key] = value.replace(f"${{{match}}}", str(replacement))
                        except KeyError:
                            log_error(f"Referenced task {ref_task_id} not found in workflow")
        return processed_input
    
    def execute_llm_task(self, task: Task) -> Dict[str, Any]:
        processed_input = self.process_task_input(task)
        log_task_input(task.id, processed_input)
        prompt = processed_input.get('prompt', '')
        if not prompt:
            return {"success": False, "error": "No prompt provided for LLM task"}
        result = self.llm_interface.execute_llm_call(prompt)
        if result["success"]:
            log_task_output(task.id, result)
            return result
        else:
            log_error(f"LLM task {task.id} failed: {result.get('error', 'Unknown error')}")
            return result
    
    def execute_tool_task(self, task: Task) -> Dict[str, Any]:
        processed_input = self.process_task_input(task)
        log_task_input(task.id, processed_input)
        result = self.tool_registry.execute_tool(task.tool_name, processed_input)
        if result["success"]:
            log_task_output(task.id, result)
            return result
        else:
            log_error(f"Tool task {task.id} failed: {result.get('error', 'Unknown error')}")
            return result
    
    def execute_task(self, task: Task) -> bool:
        log_task_start(task.id, task.name, self.workflow.id)
        task.set_status("running")
        if task.is_llm_task:
            result = self.execute_llm_task(task)
        else:
            result = self.execute_tool_task(task)
        if result.get("success", False):
            task.set_status("completed")
            task.set_output({"response": result.get("response", result.get("result", {}))})
            log_task_end(task.id, task.name, "completed", self.workflow.id)
            return True
        else:
            return self.handle_task_failure(task, result)
    
    def handle_task_failure(self, task: Task, result: Dict[str, Any]) -> bool:
        if task.can_retry():
            task.increment_retry()
            log_task_retry(task.id, task.name, task.retry_count, task.max_retries)
            task.set_status("pending")
            return self.execute_task(task)
        else:
            task.set_status("failed")
            task.set_output({"error": result.get("error", "Unknown error")})
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
                    self.workflow.set_status("failed")
                    log_workflow_end(self.workflow.id, self.workflow.name, "failed")
                    break
            else:
                current_task = self.get_next_task_by_condition(current_task)
        if self.workflow.status != "failed":
            self.workflow.set_status("completed")
            log_workflow_end(self.workflow.id, self.workflow.name, "completed")
        return {
            "workflow_id": self.workflow.id,
            "workflow_name": self.workflow.name,
            "status": self.workflow.status,
            "tasks": {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()}
        }
