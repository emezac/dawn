#!/usr/bin/env python
"""
Test script to demonstrate error propagation between tasks in a workflow.

This script creates a simple workflow with tasks that intentionally fail
and shows how error information is propagated between them.
"""  # noqa: D202

import os
import sys
import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Dawn framework components
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.errors import ErrorCode, create_error_response
from core.error_propagation import ErrorContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_error_propagation")

# Simple mock classes for demonstration
class MockToolRegistry:
    """A simple mock tool registry for demonstration."""
    def execute_tool(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Mock executing tool: {tool_name}")
        return {"success": True, "result": f"Result from {tool_name}"}

class MockLLMInterface:
    """A simple mock LLM interface for demonstration."""
    def execute_llm_call(self, prompt: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Mock LLM received prompt: {prompt[:50]}...")
        return {"success": True, "response": f"Response to: {prompt[:30]}..."}

class SimpleWorkflowEngine:
    """A simplified workflow engine for demonstrating error propagation."""  # noqa: D202
    
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.error_context = ErrorContext(workflow_id=workflow.id)
    
    def process_task_input(self, task: Task) -> Dict[str, Any]:
        """Process template references in task input."""
        processed_input = task.input_data.copy() if task.input_data else {}
        
        # Get completed tasks
        completed_tasks = {
            task_id: t for task_id, t in self.workflow.tasks.items()
            if t.status in ["completed", "failed"] and t.id != task.id
        }
        
        # Process string values for references
        for key, value in processed_input.items():
            if isinstance(value, str) and "${" in value:
                # Look for references
                matches = re.findall(r"\${([^}]+)}", value)
                for match in matches:
                    # Check if this is an error reference
                    if match.startswith("error."):
                        parts = match.split(".", 2)
                        if len(parts) >= 3:
                            task_id = parts[1]
                            error_path = parts[2] if len(parts) > 2 else None
                            
                            # Get the error from the error context
                            error_data = self.error_context.get_task_error(task_id)
                            if error_data:
                                from core.error_propagation import get_error_value
                                error_value = get_error_value(error_data, error_path)
                                
                                if error_value is not None:
                                    if value == f"${{{match}}}":
                                        processed_input[key] = error_value
                                    else:
                                        processed_input[key] = value.replace(f"${{{match}}}", str(error_value))
                    else:
                        # Standard task output reference
                        parts = match.split(".")
                        ref_task_id = parts[0]
                        
                        if ref_task_id in completed_tasks:
                            ref_task = completed_tasks[ref_task_id]
                            field = ".".join(parts[1:]) if len(parts) > 1 else None
                            
                            try:
                                replacement = ref_task.get_output_value(field)
                                if replacement is not None:
                                    if value == f"${{{match}}}":
                                        processed_input[key] = replacement
                                    else:
                                        processed_input[key] = value.replace(f"${{{match}}}", str(replacement))
                            except Exception as e:
                                logger.error(f"Error resolving reference ${{{match}}}: {str(e)}")
        
        return processed_input
    
    def execute_task(self, task: Task) -> bool:
        """Execute a single task."""
        logger.info(f"Executing task: {task.id} ({task.name})")
        task.set_status("running")
        
        # Process task input
        processed_input = self.process_task_input(task)
        logger.info(f"Task input: {processed_input}")
        
        # Execute the task
        if hasattr(task, "is_direct_handler") and task.is_direct_handler:
            result = task.handler(processed_input)
        else:
            # For our test, all non-direct handler tasks succeed
            result = {"success": True, "result": f"Result from task {task.id}"}
        
        # Handle the result
        if result.get("success", False):
            task.set_status("completed")
            task.set_output(result)
            logger.info(f"Task {task.id} completed successfully")
            return True
        else:
            # Record the error
            self.error_context.record_task_error(task.id, result)
            
            # Handle task failure
            task.set_status("failed")
            task.set_output(result)
            logger.info(f"Task {task.id} failed: {result.get('error', 'Unknown error')}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """Run the workflow."""
        logger.info(f"Running workflow: {self.workflow.id}")
        self.workflow.set_status("running")
        
        # Execute tasks in order
        for task_id in self.workflow.task_order:
            task = self.workflow.tasks[task_id]
            success = self.execute_task(task)
            
            # Check for next task based on success/failure
            if success:
                if task.next_task_id_on_success:
                    # Next task explicitly defined on success
                    next_task_id = task.next_task_id_on_success
                    logger.info(f"Moving to task {next_task_id} on success")
            else:
                if task.next_task_id_on_failure:
                    # Next task explicitly defined on failure
                    next_task_id = task.next_task_id_on_failure
                    logger.info(f"Moving to task {next_task_id} on failure")
        
        # Set workflow status
        has_failed_tasks = any(task.status == "failed" for task in self.workflow.tasks.values())
        self.workflow.set_status("failed" if has_failed_tasks else "completed")
        
        # Create result summary
        result = {
            "workflow_id": self.workflow.id,
            "workflow_name": self.workflow.name,
            "status": self.workflow.status,
            "tasks": {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()},
        }
        
        # Include error summary if there were errors
        if self.error_context.task_errors:
            result["error_summary"] = self.error_context.get_error_summary()
        
        return result

def create_workflow_with_error_propagation():
    """Create a workflow that demonstrates error propagation between tasks."""  # noqa: D202
    
    # Create a new workflow
    workflow = Workflow("error_propagation_test", "Error Propagation Test Workflow")
    
    # Task 1: Initial task that will succeed
    def task1_handler(input_data):
        logger.info("Executing Task 1 (will succeed)")
        return {"success": True, "result": "Task 1 completed successfully"}
    
    task1 = DirectHandlerTask(
        task_id="task1",
        name="Initial Successful Task",
        handler=task1_handler,
        input_data={"message": "Start workflow"},
        next_task_id_on_success="task2"
    )
    
    # Task 2: This task will fail intentionally
    def task2_handler(input_data):
        logger.info("Executing Task 2 (will fail)")
        return create_error_response(
            message="Intentional failure in Task 2",
            error_code=ErrorCode.EXECUTION_TASK_FAILED,
            details={"reason": "This is a simulated error for testing"}
        )
    
    task2 = DirectHandlerTask(
        task_id="task2",
        name="Failing Task",
        handler=task2_handler,
        input_data={},
        next_task_id_on_failure="task3"  # Continue to task3 on failure
    )
    
    # Task 3: This task will access the error from task2
    def task3_handler(input_data):
        logger.info("Executing Task 3 (will access error from Task 2)")
        # The error reference will be resolved by the engine
        error_message = input_data.get("previous_error")
        error_reason = input_data.get("error_reason")
        
        logger.info(f"Task 3 received error: {error_message}")
        logger.info(f"Error reason: {error_reason}")
        
        return {
            "success": True,
            "result": {
                "handled_error": error_message,
                "error_reason": error_reason,
                "recovery_status": "Success"
            }
        }
    
    task3 = DirectHandlerTask(
        task_id="task3",
        name="Error Handler Task",
        handler=task3_handler,
        input_data={
            "previous_error": "${error.task2}",  # Reference to task2's error
            "error_reason": "${error.task2.error_details.reason}"  # Reference to a specific error detail
        },
        next_task_id_on_success="task4"
    )
    
    # Task 4: Final task that processes the error handling result
    def task4_handler(input_data):
        logger.info("Executing Task 4 (final task)")
        recovery_status = input_data.get("recovery_status")
        
        return {
            "success": True,
            "result": {
                "workflow_completed": True,
                "recovery_successful": recovery_status == "Success",
                "final_message": "Workflow completed with error recovery"
            }
        }
    
    task4 = DirectHandlerTask(
        task_id="task4",
        name="Final Task",
        handler=task4_handler,
        input_data={
            "recovery_status": "${task3.result.recovery_status}"  # Reference to task3's output
        }
    )
    
    # Add all tasks to the workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    workflow.add_task(task4)
    
    return workflow

def print_box(title, content):
    """Print information in a nice box format."""
    width = 80
    print("\n" + "=" * width)
    print(f" {title} ".center(width, "="))
    print("=" * width)
    for line in content.split("\n"):
        print(f"| {line:<{width-4}} |")
    print("=" * width + "\n")

def main():
    """Run the error propagation test workflow."""
    # Create the workflow
    workflow = create_workflow_with_error_propagation()
    
    # Create the simplified workflow engine
    engine = SimpleWorkflowEngine(workflow)
    
    print_box("WORKFLOW EXECUTION", "Starting workflow execution with error propagation test")
    
    # Run the workflow and capture the result
    result = engine.run()
    
    # Print task results
    task_results = []
    for task_id, task_data in result['tasks'].items():
        status = task_data['status']
        task_line = f"Task: {task_id} ({task_data['name']}) - Status: {status}"
        
        if status == "completed":
            if "result" in task_data["output_data"]:
                if isinstance(task_data["output_data"]["result"], dict):
                    result_str = json.dumps(task_data["output_data"]["result"], indent=2)
                    task_line += f"\n  Result: {result_str}"
                else:
                    task_line += f"\n  Result: {task_data['output_data']['result']}"
        elif status == "failed":
            error = task_data['output_data'].get('error', 'Unknown error')
            task_line += f"\n  Error: {error}"
            
            if "error_details" in task_data["output_data"]:
                details = json.dumps(task_data["output_data"]["error_details"], indent=2)
                task_line += f"\n  Details: {details}"
        
        task_results.append(task_line)
    
    print_box("TASK RESULTS", "\n\n".join(task_results))
    
    # Print error summary if available
    if "error_summary" in result and result["error_summary"]:
        summary = result["error_summary"]
        summary_lines = [
            f"Error Count: {summary['error_count']}",
            f"Tasks with errors: {summary['tasks_with_errors']}"
        ]
        
        if "latest_error" in summary and summary["latest_error"]:
            latest = summary["latest_error"]
            summary_lines.append(f"Latest Error: {latest.get('error', 'Unknown')}")
            summary_lines.append(f"Error Code: {latest.get('error_code', 'None')}")
        
        print_box("ERROR SUMMARY", "\n".join(summary_lines))
    
    print_box("TEST COMPLETE", "Error propagation test completed successfully!")

if __name__ == "__main__":
    main() 