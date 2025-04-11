"""
Variable Resolution Test for DirectHandlerTask

This script demonstrates a fix for variable resolution with DirectHandlerTask
in both synchronous and asynchronous workflows.
"""

import os
import sys
import traceback
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.llm.interface import LLMInterface
from core.task import DirectHandlerTask, Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow
from core.tools.registry_access import get_registry


# Define Direct Handler functions
def data_generator(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate sample data with a nested structure.
    """
    try:
        result = {
            "user": {
                "name": "Test User",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            },
            "items": [
                {"id": 1, "value": "first"},
                {"id": 2, "value": "second"}
            ]
        }
        
        print("Generated nested data structure")
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        print(f"Error in data_generator: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def nested_access(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Access nested data from previous task.
    """
    try:
        user_name = input_data.get("user_name", "Unknown")
        theme = input_data.get("theme", "unknown")
        first_item = input_data.get("first_item", "none")
        
        result = f"User {user_name} has {theme} theme and first item is {first_item}"
        print(f"Accessed nested data: {result}")
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        print(f"Error in nested_access: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_variable_resolution():
    """
    Test variable resolution with DirectHandlerTask.
    """
    print("\n=== Testing Variable Resolution with DirectHandlerTask ===")
    
    # Create workflow
    workflow = Workflow(
        workflow_id="variable_resolution_test",
        name="Variable Resolution Test"
    )
    
    # Task 1: Generate Data
    task1 = DirectHandlerTask(
        task_id="generate_data",
        name="Generate Data",
        handler=data_generator,
        input_data={},
        next_task_id_on_success="access_nested_data"
    )
    
    # Task 2: Access Nested Data
    task2 = DirectHandlerTask(
        task_id="access_nested_data",
        name="Access Nested Data",
        handler=nested_access,
        input_data={
            "user_name": "${generate_data.output_data.result.user.name}",
            "theme": "${generate_data.output_data.result.user.preferences.theme}",
            "first_item": "${generate_data.output_data.result.items[0].value}"
        }
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    
    # Create agent and load workflow
    print("Creating agent and loading workflow...")
    registry = get_registry()
    llm_interface = LLMInterface()
    
    agent = Agent(
        agent_id="test_agent",
        name="Test Agent",
        llm_interface=llm_interface,
        tool_registry=get_registry()
    )
    agent.load_workflow(workflow)
    
    # Run workflow synchronously
    print("\nRunning workflow synchronously...")
    sync_results = agent.run()
    
    # Display results
    print("\nSync Results:", sync_results.get("status"))
    if sync_results.get("status") == "completed":
        print("Workflow completed successfully!")
        
        # Check task outputs
        tasks_data = sync_results.get("tasks", {})
        if "access_nested_data" in tasks_data:
            task_data = tasks_data["access_nested_data"]
            output = task_data.get("output_data", {})
            if "result" in output:
                print(f"Final Result: {output['result']}")
            else:
                print("No result in output_data")
        else:
            print("Task 'access_nested_data' not found in results")
    else:
        print(f"Workflow failed with status: {sync_results.get('status')}")
        
    # Run workflow asynchronously
    print("\nRunning workflow asynchronously...")
    try:
        async_results = agent.run_async()
        
        # Display results
        print("\nAsync Results:", async_results.get("status"))
        if async_results.get("status") == "completed":
            print("Workflow completed successfully!")
            
            # Check task outputs
            tasks_data = async_results.get("tasks", {})
            if "access_nested_data" in tasks_data:
                task_data = tasks_data["access_nested_data"]
                output = task_data.get("output_data", {})
                if "result" in output:
                    print(f"Final Result: {output['result']}")
                else:
                    print("No result in output_data")
            else:
                print("Task 'access_nested_data' not found in results")
        else:
            print(f"Workflow failed with status: {async_results.get('status')}")
    except Exception as e:
        print(f"Error running async workflow: {e}")
        print(traceback.format_exc())
    
    print("\n=== Test Completed ===")
    

if __name__ == "__main__":
    try:
        test_variable_resolution()
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc()) 