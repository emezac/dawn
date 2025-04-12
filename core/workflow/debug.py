#!/usr/bin/env python3
"""
Debug utilities for the Dawn Framework workflow engine.

This module provides debugging tools for workflows when debug mode is enabled.
"""  # noqa: D202

import json
import time
import logging
from typing import Dict, Any, Optional, List, Set, Callable

from core.utils.debug import is_debug_mode, debug_log
from core.workflow.workflow import Workflow
from core.workflow.task import Task

# Configure logger
logger = logging.getLogger("dawn.workflow.debug")

class WorkflowDebugger:
    """
    Debugger for workflows.
    
    This class provides debugging features for workflows when debug mode is enabled,
    including task execution monitoring, variable resolution tracking, and performance analysis.
    """  # noqa: D202
    
    def __init__(self, workflow: Workflow):
        """
        Initialize the workflow debugger.
        
        Args:
            workflow: The workflow to debug
        """
        self.workflow = workflow
        self.enabled = is_debug_mode()
        self.task_timings: Dict[str, Dict[str, float]] = {}
        self.variable_resolutions: Dict[str, List[Dict[str, Any]]] = {}
        self.errors: List[Dict[str, Any]] = []
        self.execution_path: List[str] = []
        
        if self.enabled:
            logger.info(f"Workflow debugger initialized for workflow '{workflow.name}' (ID: {workflow.workflow_id})")
    
    def start_task(self, task_id: str) -> None:
        """
        Record the start of a task.
        
        Args:
            task_id: The ID of the task being started
        """
        if not self.enabled:
            return
        
        self.task_timings.setdefault(task_id, {})
        self.task_timings[task_id]["start_time"] = time.time()
        self.execution_path.append(task_id)
        
        # Get the task
        task = self.workflow.get_task(task_id)
        task_name = task.name if task else task_id
        
        logger.debug(f"Starting task: {task_name} (ID: {task_id})")
        
        # Log task details
        if task:
            debug_log("Task details", {
                "id": task_id,
                "name": task.name,
                "is_llm_task": getattr(task, "is_llm_task", False),
                "tool_name": getattr(task, "tool_name", None),
                "input_data": getattr(task, "input_data", {}),
                "condition": getattr(task, "condition", None),
                "next_task_id_on_success": getattr(task, "next_task_id_on_success", None),
                "next_task_id_on_failure": getattr(task, "next_task_id_on_failure", None)
            })
    
    def end_task(self, task_id: str, success: bool, output_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Record the end of a task.
        
        Args:
            task_id: The ID of the task being ended
            success: Whether the task was successful
            output_data: The output data from the task
        """
        if not self.enabled:
            return
        
        if task_id in self.task_timings:
            start_time = self.task_timings[task_id].get("start_time")
            if start_time:
                end_time = time.time()
                duration = end_time - start_time
                self.task_timings[task_id]["end_time"] = end_time
                self.task_timings[task_id]["duration"] = duration
                self.task_timings[task_id]["success"] = success
                
                # Get the task
                task = self.workflow.get_task(task_id)
                task_name = task.name if task else task_id
                
                status = "succeeded" if success else "failed"
                logger.debug(f"Task {task_name} (ID: {task_id}) {status} in {duration:.4f}s")
                
                # Log output data (simplified to reduce log size)
                if output_data:
                    simplified_output = self._simplify_large_data(output_data)
                    debug_log("Task output data", simplified_output)
    
    def record_error(self, task_id: str, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an error that occurred during workflow execution.
        
        Args:
            task_id: The ID of the task where the error occurred
            error: The exception that was raised
            context: Additional context about the error
        """
        if not self.enabled:
            return
        
        error_info = {
            "task_id": task_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": time.time(),
            "context": context or {}
        }
        
        self.errors.append(error_info)
        
        # Get the task
        task = self.workflow.get_task(task_id)
        task_name = task.name if task else task_id
        
        logger.error(f"Error in task {task_name} (ID: {task_id}): {str(error)}")
        debug_log("Error details", error_info)
    
    def record_variable_resolution(self, variable_name: str, template: str, resolved_value: Any) -> None:
        """
        Record a variable resolution event.
        
        Args:
            variable_name: The name of the variable being resolved
            template: The template string containing the variable
            resolved_value: The resolved value
        """
        if not self.enabled:
            return
        
        if variable_name not in self.variable_resolutions:
            self.variable_resolutions[variable_name] = []
        
        # Create a simplified value for logging
        simplified_value = self._simplify_large_data(resolved_value)
        
        resolution_info = {
            "timestamp": time.time(),
            "template": template,
            "resolved_value": simplified_value
        }
        
        self.variable_resolutions[variable_name].append(resolution_info)
        logger.debug(f"Resolved variable '{variable_name}' in template '{template}'")
    
    def get_report(self) -> Dict[str, Any]:
        """
        Generate a debug report for the workflow.
        
        Returns:
            A dictionary containing debug information
        """
        if not self.enabled:
            return {}
        
        return {
            "workflow_id": self.workflow.workflow_id,
            "workflow_name": self.workflow.name,
            "execution_path": self.execution_path,
            "task_timings": self.task_timings,
            "errors": self.errors,
            "variable_resolutions": self.variable_resolutions,
            "performance_summary": self._generate_performance_summary()
        }
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """
        Generate a performance summary for the workflow.
        
        Returns:
            A dictionary containing performance metrics
        """
        if not self.task_timings:
            return {}
        
        total_time = 0
        slowest_task = {"id": None, "duration": 0}
        task_count = 0
        success_count = 0
        
        for task_id, timing in self.task_timings.items():
            if "duration" in timing:
                duration = timing["duration"]
                total_time += duration
                task_count += 1
                
                if timing.get("success", False):
                    success_count += 1
                
                if duration > slowest_task["duration"]:
                    slowest_task = {"id": task_id, "duration": duration}
        
        # Get the name of the slowest task
        if slowest_task["id"]:
            task = self.workflow.get_task(slowest_task["id"])
            if task:
                slowest_task["name"] = task.name
        
        return {
            "total_time": total_time,
            "task_count": task_count,
            "average_task_time": total_time / task_count if task_count > 0 else 0,
            "success_rate": success_count / task_count if task_count > 0 else 0,
            "slowest_task": slowest_task
        }
    
    def _simplify_large_data(self, data: Any) -> Any:
        """
        Simplify large data structures for logging.
        
        Args:
            data: The data to simplify
            
        Returns:
            Simplified data structure
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # For large strings, truncate
                if isinstance(value, str) and len(value) > 500:
                    result[key] = value[:500] + "... [truncated]"
                # For nested structures, recurse
                elif isinstance(value, (dict, list)):
                    result[key] = self._simplify_large_data(value)
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            # For large lists, truncate
            if len(data) > 20:
                return [self._simplify_large_data(item) for item in data[:20]] + ["... and more"]
            return [self._simplify_large_data(item) for item in data]
        else:
            return data

def patch_workflow_engine() -> None:
    """
    Patch the workflow engine to add debugging capabilities.
    
    This function should be called at application startup when debug mode is enabled.
    """
    if not is_debug_mode():
        return
    
    logger.info("Patching workflow engine for debug mode")
    
    # Import here to avoid circular imports
    from core.workflow.engine import WorkflowEngine
    
    # Store the original run_workflow method
    original_run_workflow = WorkflowEngine.run_workflow
    
    # Create a wrapper method with debugging
    def run_workflow_with_debug(self, workflow, *args, **kwargs):
        """Wrapper for run_workflow with debugging."""
        # Create a debugger for this workflow
        debugger = WorkflowDebugger(workflow)
        
        # Store the debugger on the workflow
        workflow.debugger = debugger
        
        # Patch the task execution methods
        original_execute_task = self._execute_task
        
        def _execute_task_with_debug(task, *task_args, **task_kwargs):
            """Wrapper for _execute_task with debugging."""
            task_id = task.id
            debugger.start_task(task_id)
            
            try:
                result = original_execute_task(task, *task_args, **task_kwargs)
                success = not hasattr(result, "get") or not result.get("error")
                debugger.end_task(task_id, success, result)
                return result
            except Exception as e:
                debugger.record_error(task_id, e, {"args": task_args, "kwargs": task_kwargs})
                raise
        
        # Replace the method
        self._execute_task = _execute_task_with_debug
        
        logger.debug(f"Running workflow '{workflow.name}' with debug mode enabled")
        start_time = time.time()
        
        try:
            # Run the workflow
            result = original_run_workflow(self, workflow, *args, **kwargs)
            
            # Calculate total time
            end_time = time.time()
            total_time = end_time - start_time
            
            # Log workflow completion
            logger.debug(f"Workflow '{workflow.name}' completed in {total_time:.4f}s")
            
            # Generate and log the debug report
            debug_report = debugger.get_report()
            debug_log(f"Workflow '{workflow.name}' debug report", debug_report)
            
            # Add the debug report to the result
            if isinstance(result, dict):
                result["_debug"] = debug_report
            
            return result
        finally:
            # Restore the original method
            self._execute_task = original_execute_task
    
    # Replace the method
    WorkflowEngine.run_workflow = run_workflow_with_debug
    
    logger.info("Workflow engine patched for debug mode")