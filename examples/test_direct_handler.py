#!/usr/bin/env python3
"""Test script for DirectHandlerTask.

This script creates a simple workflow with DirectHandlerTask to test
the correct handler signature and function passing.
"""  # noqa: D202

import os
import sys
import logging
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_direct_handler")

# Import workflow components
from core.services import get_services, reset_services
from core.workflow import Workflow
from core.task import DirectHandlerTask
from core.engine import WorkflowEngine

# Simple task handler
def simple_handler(task, input_data: dict) -> dict:
    """Simple handler function for testing.
    
    Args:
        task: The DirectHandlerTask object
        input_data: Dictionary containing input data
        
    Returns:
        Dictionary with result
    """
    # Log the input
    logger.info(f"Simple handler called with input: {input_data}")
    
    # Extract message from input
    message = input_data.get("message", "No message provided")
    
    # Process the message
    result = f"Processed: {message.upper()}"
    
    logger.info(f"Simple handler processed message: {result}")
    
    return {
        "status": "success",
        "result": result
    }

# Dependent task handler
def dependent_handler(task, input_data: dict) -> dict:
    """Handler that depends on the result of another task.
    
    Args:
        task: The DirectHandlerTask object
        input_data: Dictionary containing processed_result
        
    Returns:
        Dictionary with final result
    """
    # Log the input
    logger.info(f"Dependent handler called with input: {input_data}")
    
    # Extract processed result from input
    processed_result = input_data.get("processed_result", "No result provided")
    
    # Add additional processing
    final_result = f"Final: {processed_result} + EXTRA PROCESSING"
    
    logger.info(f"Dependent handler processed result: {final_result}")
    
    return {
        "status": "success",
        "result": final_result
    }

def main():
    """Run the test workflow."""
    # Reset services
    reset_services()
    services = get_services()
    
    logger.info("Services initialized")
    
    # Create a simple workflow
    workflow = Workflow(workflow_id="test_workflow", name="Test Workflow")
    
    # Create the first task
    first_task = DirectHandlerTask(
        task_id="first_task",
        name="First Task",
        handler=simple_handler,
        input_data={
            "message": "hello world"
        }
    )
    workflow.add_task(first_task)
    
    # Create the second task that depends on the first
    second_task = DirectHandlerTask(
        task_id="second_task",
        name="Second Task",
        handler=dependent_handler,
        input_data={
            "processed_result": "${first_task.result}"
        },
        depends_on=["first_task"]
    )
    workflow.add_task(second_task)
    
    # Create the workflow engine
    engine = services.create_workflow_engine(workflow)
    
    # Run the workflow
    logger.info("Running test workflow")
    results = engine.run({})
    
    # Print results
    logger.info("Workflow execution completed")
    try:
        # Print each task result
        for task_id, output in results.items():
            if hasattr(output, 'to_dict'):
                logger.info(f"Task '{task_id}' result: {output.to_dict()}")
            else:
                logger.info(f"Task '{task_id}' result: {output}")
    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}")
        for task_id, output in results.items():
            logger.info(f"Task '{task_id}' type: {type(output)}")
    
    return results

if __name__ == "__main__":
    main() 