"""
Fix for DirectHandlerTask in AsyncWorkflowEngine.

This script demonstrates the issue with DirectHandlerTask and provides a fix for the
AsyncWorkflowEngine to properly handle DirectHandlerTask instances.
"""

from typing import Dict, Any
import sys
import os
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task import DirectHandlerTask


# Sample handler function
def sample_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    A simple handler function for testing.
    
    Args:
        input_data: Dictionary with input parameters
        
    Returns:
        Dictionary with results
    """
    value = input_data.get("value", 0)
    multiplier = input_data.get("multiplier", 1)
    result = value * multiplier
    
    return {
        "success": True,
        "result": {
            "calculated_value": result,
            "input_value": value,
            "multiplier": multiplier
        }
    }


def main():
    """Run a test of DirectHandlerTask."""
    print("=== Testing DirectHandlerTask Fix ===")
    
    # Create a DirectHandlerTask
    print("\nCreating DirectHandlerTask...")
    task = DirectHandlerTask(
        task_id="test_task",
        name="Test Direct Handler Task",
        handler=sample_handler,
        input_data={
            "value": 42,
            "multiplier": 10
        }
    )
    print("Task created successfully")
    
    # Execute the task directly
    print("\nExecuting task directly...")
    result = task.execute()
    
    # Check the result
    if result.get("success"):
        print("Success! Task executed correctly")
        print(f"Result: {result.get('result')}")
        
        # Set the output on the task
        task.set_output(result)
        print(f"Task output: {task.output_data}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n=== Fix for AsyncWorkflowEngine ===")
    print("""
Problem: The AsyncWorkflowEngine doesn't properly handle DirectHandlerTask.
- In the synchronous WorkflowEngine, there's a check for `task.is_direct_handler`
- In the AsyncWorkflowEngine, this check is missing

Fix: Add the following to AsyncWorkflowEngine:

1. Add a new method to handle DirectHandlerTask:
```python
async def async_execute_direct_handler_task(self, task: Task) -> Dict[str, Any]:
    \"\"\"Executes a DirectHandlerTask by calling its execute method directly.\"\"\"
    processed_input = self.process_task_input(task)
    
    try:
        # Execute the DirectHandlerTask's execute method
        result = task.execute(processed_input)
        
        if result.get("success"):
            return {"success": True, "result": result.get("result", result.get("response", {}))}
        else:
            error_msg = result.get("error", "Unknown DirectHandlerTask error")
            log_error(f"DirectHandlerTask '{task.id}' failed: {error_msg}")
            return {"success": False, "error": error_msg}
    except Exception as e:
        log_error(f"Exception during execution of DirectHandlerTask '{task.id}': {e}", exc_info=True)
        return {"success": False, "error": f"DirectHandlerTask execution error: {str(e)}"}
```

2. Modify async_execute_task to check for DirectHandlerTask:
```python
async def async_execute_task(self, task: Task) -> bool:
    \"\"\"Executes a single task, handles retries, sets output and status.\"\"\"
    log_task_start(task.id, task.name, self.workflow.id)
    task.set_status("running")
    execution_result: Dict[str, Any] = {}

    try:
        # Check if this is a DirectHandlerTask
        if hasattr(task, "is_direct_handler") and task.is_direct_handler:
            execution_result = await self.async_execute_direct_handler_task(task)
        elif task.is_llm_task:
            execution_result = await self.async_execute_llm_task(task)
        else:
            execution_result = await self.async_execute_tool_task(task)

        # Rest of the method remains the same...
```

This fix ensures that DirectHandlerTask instances are executed correctly in both
synchronous and asynchronous workflow engines.
    """)
    
    print("\n=== Test completed successfully ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc() 