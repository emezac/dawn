#!/usr/bin/env python
"""
Demo of error propagation between tasks.

This is a minimal, self-contained example that demonstrates how errors
can be propagated between tasks in a workflow.
"""  # noqa: D202

import json
from typing import Dict, Any, Optional
from datetime import datetime

# Simple error code constants
class ErrorCode:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    RESOURCE_ERROR = "RESOURCE_ERROR"

# Simple task implementation
class Task:
    """A simple task that can succeed or fail."""  # noqa: D202
    
    def __init__(self, task_id: str, name: str, handler=None):
        self.id = task_id
        self.name = name
        self.handler = handler
        self.status = "pending"
        self.output = {}
        self.error = None
        self.error_details = {}
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task with the given input data."""
        print(f"Executing task: {self.id} ({self.name})")
        print(f"Input: {json.dumps(input_data, indent=2)}")
        
        if self.handler:
            result = self.handler(input_data)
        else:
            result = {"success": True, "result": f"Default result from {self.id}"}
        
        if result.get("success", True):
            self.status = "completed"
            self.output = result
            print(f"Task {self.id} completed successfully")
        else:
            self.status = "failed"
            self.output = result
            self.error = result.get("error", "Unknown error")
            self.error_details = result.get("error_details", {})
            print(f"Task {self.id} failed: {self.error}")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "error_details": self.error_details
        }

# Error context to track errors between tasks
class ErrorContext:
    """Tracks errors across tasks for propagation."""  # noqa: D202
    
    def __init__(self):
        self.task_errors = {}
    
    def record_error(self, task_id: str, error_data: Dict[str, Any]) -> None:
        """Record an error from a task."""
        self.task_errors[task_id] = {
            "error": error_data.get("error", "Unknown error"),
            "error_code": error_data.get("error_code", "UNKNOWN_ERROR"),
            "error_details": error_data.get("error_details", {}),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_error(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the error for a specific task."""
        return self.task_errors.get(task_id)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors."""
        return {
            "error_count": len(self.task_errors),
            "tasks_with_errors": list(self.task_errors.keys()),
            "errors": self.task_errors
        }

# Helper function to create error responses
def create_error_response(message: str, error_code: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {
        "success": False,
        "error": message,
        "error_code": error_code,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        response["error_details"] = details
    
    return response

# Helper to format output nicely
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
    """Run the error propagation demo."""
    # Create error context
    error_ctx = ErrorContext()
    
    # Task 1: Initial task that will succeed
    def task1_handler(input_data):
        return {"success": True, "result": "Task 1 completed successfully"}
    
    task1 = Task("task1", "Initial Task", task1_handler)
    
    # Task 2: This task will fail intentionally
    def task2_handler(input_data):
        return create_error_response(
            message="Intentional failure in Task 2",
            error_code=ErrorCode.EXECUTION_ERROR,
            details={"reason": "This is a simulated error for testing"}
        )
    
    task2 = Task("task2", "Failing Task", task2_handler)
    
    # Task 3: This task will handle the error from task2
    def task3_handler(input_data):
        # Get the error information provided in input
        error_message = input_data.get("previous_error")
        error_reason = input_data.get("error_reason")
        
        print(f"Task 3 received error: {error_message}")
        print(f"Error reason: {error_reason}")
        
        return {
            "success": True,
            "result": {
                "handled_error": error_message,
                "error_reason": error_reason,
                "recovery_status": "Success"
            }
        }
    
    task3 = Task("task3", "Error Handler Task", task3_handler)
    
    # Task 4: Final task
    def task4_handler(input_data):
        recovery_status = input_data.get("recovery_status")
        
        return {
            "success": True,
            "result": {
                "workflow_completed": True,
                "recovery_successful": recovery_status == "Success",
                "final_message": "Workflow completed with error recovery"
            }
        }
    
    task4 = Task("task4", "Final Task", task4_handler)
    
    # Create a simple workflow by executing tasks in sequence
    print_box("DEMO START", "Starting error propagation demo")
    
    # Step 1: Execute task1
    task1.execute({"message": "Start workflow"})
    
    # Step 2: Execute task2 (will fail)
    result2 = task2.execute({"previous_result": task1.output.get("result")})
    
    # Record the error from task2
    if not result2.get("success", False):
        error_ctx.record_error(task2.id, result2)
    
    # Step 3: Execute task3 with error from task2
    task2_error = error_ctx.get_error(task2.id)
    task3.execute({
        "previous_error": task2_error.get("error") if task2_error else "No error",
        "error_reason": task2_error.get("error_details", {}).get("reason") if task2_error else "Unknown reason"
    })
    
    # Step 4: Execute task4 with recovery status from task3
    task4.execute({
        "recovery_status": task3.output.get("result", {}).get("recovery_status")
    })
    
    # Print final results
    print_box("TASK RESULTS", "\n".join([
        f"Task: {task.id} - Status: {task.status}",
        f"Output: {json.dumps(task.output, indent=2)}" if task.status == "completed" else f"Error: {task.error}"
        for task in [task1, task2, task3, task4]
    ]))
    
    # Print error summary
    error_summary = error_ctx.get_summary()
    if error_summary["error_count"] > 0:
        print_box("ERROR SUMMARY", 
                 f"Error Count: {error_summary['error_count']}\n"
                 f"Tasks with errors: {error_summary['tasks_with_errors']}")
    
    print_box("DEMO COMPLETE", "Error propagation demonstration completed")

if __name__ == "__main__":
    main() 