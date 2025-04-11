import os
import sys
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task import DirectHandlerTask

def simple_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """A simple handler function that returns success."""
    print(f"Handler received: {input_data}")
    return {
        "success": True,
        "result": f"Processed: {input_data.get('message', 'No message')}"
    }

try:
    print("Creating DirectHandlerTask...")
    task = DirectHandlerTask(
        task_id="test_task",
        name="Test Task",
        handler=simple_handler,
        input_data={"message": "Hello, world!"}
    )
    print("Task created successfully")
    
    print("Executing task...")
    result = task.execute()
    print(f"Task execution result: {result}")
    
    print("Test completed successfully")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    print(traceback.format_exc()) 