#!/usr/bin/env python3
"""
Test script to verify correct usage of the depends_on parameter
in both Task and DirectHandlerTask.
"""  # noqa: D202

import json
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to sys.path to allow imports from the dawn framework
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.engine import WorkflowEngine
from core.services import get_services, reset_services

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define handler functions for DirectHandlerTask instances
def task1_handler(task, input_data):
    """Handler for task 1: Generate a simple message."""
    logger.info(f"Executing task1_handler with input: {input_data}")
    return {
        "success": True,
        "result": f"Task 1 completed with message: {input_data.get('message', 'No message provided')}"
    }


def task2_handler(task, input_data):
    """Handler for task 2: Process the output from task 1."""
    logger.info(f"Executing task2_handler with input: {input_data}")
    task1_result = input_data.get('task1_result', 'No result from task 1')
    return {
        "success": True,
        "result": f"Task 2 processed: {task1_result}"
    }


def task3_handler(task, input_data):
    """Handler for task 3: Combine results from tasks 1 and 2."""
    logger.info(f"Executing task3_handler with input: {input_data}")
    task1_result = input_data.get('task1_result', 'No result from task 1')
    task2_result = input_data.get('task2_result', 'No result from task 2')
    
    return {
        "success": True,
        "result": {
            "combined_result": f"Combined results: {task1_result} and {task2_result}",
            "timestamp": "2023-07-15T10:30:00Z"  # Example fixed timestamp
        }
    }


def task4_handler(task, input_data):
    """Handler for task 4: Format the final output."""
    logger.info(f"Executing task4_handler with input: {input_data}")
    task3_result = input_data.get('combined_result', 'No combined result')
    
    # Create a formatted output
    formatted_output = f"""
FINAL REPORT
============
{task3_result}

Generated at: {input_data.get('timestamp', 'unknown time')}
"""
    
    return {
        "success": True,
        "result": formatted_output.strip()
    }


def construct_test_workflow():
    """
    Construct a simple workflow with dependencies between tasks.
    This demonstrates the correct usage of depends_on parameter.
    """
    # Create a new workflow
    workflow = Workflow(workflow_id="test_depends_on_workflow", name="Test Depends On Parameter Workflow")
    
    # Task 1: Initial task with no dependencies
    task1 = DirectHandlerTask(
        task_id="task1",
        name="Generate Message",
        handler=task1_handler,
        input_data={
            "message": "Hello, this is a test workflow!"
        }
    )
    workflow.add_task(task1)
    
    # Task 2: Depends on Task 1
    task2 = DirectHandlerTask(
        task_id="task2",
        name="Process Message",
        handler=task2_handler,
        input_data={
            "task1_result": "${task1.result}"
        },
        depends_on=["task1"]  # Using depends_on to specify dependency
    )
    workflow.add_task(task2)
    
    # Task 3: Depends on both Task 1 and Task 2
    task3 = DirectHandlerTask(
        task_id="task3",
        name="Combine Results",
        handler=task3_handler,
        input_data={
            "task1_result": "${task1.result}",
            "task2_result": "${task2.result}"
        },
        depends_on=["task1", "task2"]  # Multiple dependencies
    )
    workflow.add_task(task3)
    
    # Task 4: Depends on Task 3
    task4 = DirectHandlerTask(
        task_id="task4",
        name="Format Output",
        handler=task4_handler,
        input_data={
            "combined_result": "${task3.result.combined_result}",
            "timestamp": "${task3.result.timestamp}"
        },
        depends_on=["task3"]
    )
    workflow.add_task(task4)
    
    return workflow


def main():
    """
    Main function to run the test workflow.
    """
    logger.info("Starting test_depends_on_parameter.py")
    
    # Construct the workflow
    workflow = construct_test_workflow()
    
    # Log the workflow structure
    logger.info(f"Created workflow with {len(workflow.tasks)} tasks")
    for task_id, task in workflow.tasks.items():
        if hasattr(task, 'depends_on'):
            dependencies = task.depends_on
        else:
            dependencies = []
        logger.info(f"Task: {task_id}, Dependencies: {dependencies}")
    
    # Create a workflow engine
    engine = WorkflowEngine()
    
    # Execute the workflow
    logger.info("Executing workflow...")
    results = engine.run(workflow, {})
    
    # Check if the workflow executed successfully
    if results.get("success", False):
        logger.info("Workflow executed successfully!")
        task4_results = results.get("tasks", {}).get("task4", {}).get("output_data", {}).get("result", "No result found")
        logger.info(f"Final result: {task4_results}")
    else:
        error_msg = results.get("error", "Unknown error")
        logger.error(f"Workflow execution failed: {error_msg}")
    
    # Export the workflow execution result to JSON
    output_path = os.path.join(project_root, "examples", "test_depends_on_result.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Workflow result saved to {output_path}")


if __name__ == "__main__":
    main() 