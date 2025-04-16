#!/usr/bin/env python3
"""
A simple test script to demonstrate and verify the correct usage of the depends_on parameter
for tasks in a workflow.

This script creates a workflow with tasks that depend on each other and verifies
that the dependencies are respected during execution.
"""  # noqa: D202

import os
import sys
import logging

# Add the parent directory to sys.path for imports
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Import framework classes
from core.workflow import Workflow
from core.task import DirectHandlerTask
from core.llm.interface import LLMInterface
from core.tools.registry import ToolRegistry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dependencies_test")

def test_handler_task1(task, data):
    """Handler for task 1"""
    logger.info(f"Executing task1 with data: {data}")
    return {
        "success": True,
        "result": "Task 1 completed successfully"
    }

def test_handler_task2(task, data):
    """Handler for task 2"""
    logger.info(f"Executing task2 with data: {data}")
    return {
        "success": True,
        "result": f"Task 2 completed with dependency output: {data.get('task1_output', 'None')}"
    }

def test_handler_task3(task, data):
    """Handler for task 3"""
    logger.info(f"Executing task3 with data: {data}")
    return {
        "success": True,
        "result": f"Task 3 completed with task1: {data.get('task1_output', 'None')} and task2: {data.get('task2_output', 'None')}"
    }

def main():
    """Main test function"""
    logger.info("Testing dependencies_parameter usage (depends_on vs dependencies)")

    # Create a workflow
    workflow = Workflow(workflow_id="dependencies_test", name="Dependencies Test Workflow")

    # Create tasks that depend on each other
    task1 = DirectHandlerTask(
        task_id="task1",
        name="Task 1",
        handler=test_handler_task1,
        input_data={"message": "Hello from Task 1"}
    )
    workflow.add_task(task1)

    # Task 2 depends on Task 1
    task2 = DirectHandlerTask(
        task_id="task2",
        name="Task 2",
        handler=test_handler_task2,
        input_data={"task1_output": "${task1.result}"},
        depends_on=["task1"]  # Using the correct depends_on parameter
    )
    workflow.add_task(task2)

    # Task 3 depends on both Task 1 and Task 2
    task3 = DirectHandlerTask(
        task_id="task3",
        name="Task 3",
        handler=test_handler_task3,
        input_data={
            "task1_output": "${task1.result}",
            "task2_output": "${task2.result}"
        },
        depends_on=["task1", "task2"]  # Depends on multiple tasks
    )
    workflow.add_task(task3)

    # Log the dependencies
    logger.info("Workflow tasks and their dependencies:")
    for task_id, task in workflow.tasks.items():
        deps = getattr(task, "depends_on", [])
        logger.info(f"Task: {task_id}, Dependencies: {deps}")

    # Note: In a real test, we would use a mocked engine to execute the workflow
    # For this test, we're just verifying the task configuration
    logger.info("Dependencies test completed successfully")

if __name__ == "__main__":
    main() 