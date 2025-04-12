#!/usr/bin/env python3
"""
Example demonstrating how to use DirectHandlerTask with HandlerRegistry.

This example shows:
1. Registering handlers in the global HandlerRegistry
2. Creating DirectHandlerTask instances that reference handlers by name
3. Executing a workflow with different handler types
"""  # noqa: D202

import logging
import sys
from typing import Dict, Any

from core.task import DirectHandlerTask, Task
from core.workflow import Workflow
from core.utils.logger import configure_logging
from core.services import get_services, get_handler_registry

# Set up logging
configure_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define some sample handler functions that will be registered in the HandlerRegistry

@get_handler_registry().register()
def calculate_sum(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add two numbers and return the result."""
    a = input_data.get("a", 0)
    b = input_data.get("b", 0)
    result = a + b
    
    logger.info(f"Calculating sum: {a} + {b} = {result}")
    
    return {
        "success": True,
        "result": result,
        "input_values": [a, b],
        "operation": "sum"
    }


@get_handler_registry().register(name="multiply_numbers")
def multiply_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Multiply two numbers and return the result."""
    a = input_data.get("a", 0)
    b = input_data.get("b", 0)
    result = a * b
    
    logger.info(f"Calculating product: {a} * {b} = {result}")
    
    return {
        "success": True,
        "result": result,
        "input_values": [a, b],
        "operation": "multiply"
    }


def format_result(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format the calculation result as a string."""
    operation = input_data.get("operation", "calculation")
    result = input_data.get("result", 0)
    input_values = input_data.get("input_values", [])
    
    formatted_result = f"The result of the {operation} {' and '.join([str(v) for v in input_values])} is {result}"
    
    logger.info(f"Formatted result: {formatted_result}")
    
    return {
        "success": True,
        "result": formatted_result
    }


# Register the third handler manually instead of using the decorator
get_handler_registry().register_handler("format_result", format_result)


def create_calculation_workflow() -> Workflow:
    """Create a workflow that performs calculations and formats the results."""
    workflow = Workflow(
        workflow_id="calculation_workflow",
        name="Calculation Workflow Example"
    )
    
    # Step 1: Add task
    addition_task = DirectHandlerTask(
        task_id="addition_task",
        name="Addition Operation",
        handler_name="calculate_sum",  # Reference handler by registered name
        input_data={"a": 10, "b": 20}
    )
    workflow.add_task(addition_task)
    
    # Step 2: Multiply task
    multiplication_task = DirectHandlerTask(
        task_id="multiplication_task",
        name="Multiplication Operation",
        handler_name="multiply_numbers",  # Reference handler by registered name
        input_data={"a": 5, "b": 7}
    )
    workflow.add_task(multiplication_task)
    
    # Step 3: Format addition result
    format_addition_task = DirectHandlerTask(
        task_id="format_addition_task",
        name="Format Addition Result",
        handler_name="format_result",  # Reference handler by registered name
        input_data={
            "result": "${addition_task.output_data.result}",
            "operation": "${addition_task.output_data.operation}",
            "input_values": "${addition_task.output_data.input_values}"
        }
    )
    workflow.add_task(format_addition_task)
    
    # Step 4: Format multiplication result
    format_multiplication_task = DirectHandlerTask(
        task_id="format_multiplication_task",
        name="Format Multiplication Result",
        handler_name="format_result",  # Reference handler by registered name
        input_data={
            "result": "${multiplication_task.output_data.result}",
            "operation": "${multiplication_task.output_data.operation}",
            "input_values": "${multiplication_task.output_data.input_values}"
        }
    )
    workflow.add_task(format_multiplication_task)
    
    # Set up the workflow transitions
    workflow.add_transition("addition_task", "multiplication_task")
    workflow.add_transition("multiplication_task", "format_addition_task")
    workflow.add_transition("format_addition_task", "format_multiplication_task")
    
    return workflow


async def run_workflow():
    """Run the calculation workflow example."""
    # Create workflow
    workflow = create_calculation_workflow()
    
    # Get services container
    services = get_services()
    
    # Create workflow engine
    engine = services.create_workflow_engine(workflow)
    
    # Run the workflow
    logger.info(f"Starting workflow: {workflow.name}")
    result = await engine.async_run()
    
    # Print the workflow result
    logger.info(f"Workflow execution completed with status: {result['status']}")
    
    # Print task results
    for task_id, task in workflow.tasks.items():
        logger.info(f"Task '{task_id}' status: {task.status}")
        if task.status == "completed":
            if "result" in task.output_data:
                logger.info(f"  Result: {task.output_data['result']}")
    
    return result


def main():
    """Run the direct handler example."""
    import asyncio
    
    try:
        # Run the workflow
        asyncio.run(run_workflow())
        return 0
    except Exception as e:
        logger.error(f"Error running example: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 