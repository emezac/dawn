#!/usr/bin/env python3
"""
Dawn Framework Debug Mode Example

This example demonstrates how to enable and use debug mode in the Dawn Framework.
It creates a simple workflow and shows how debug features provide detailed
information about execution, performance, and errors.

To run this example:
python examples/debug_mode_example.py

The example will create a simple workflow and execute it with debug mode enabled.
"""  # noqa: D202

import os
import sys
import json
import time
import random
import logging
from pathlib import Path

# Add the project root to the Python path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import debug utilities
from core.utils.debug_initializer import setup_debug_mode
from core.utils.debug import debug_log, measure_execution_time, dump_variables
from core.config import configure, get, set, as_dict

# Import workflow components
from core.workflow.workflow import Workflow
from core.workflow.task import Task
from core.workflow.engine import WorkflowEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debug_example")

# Enable debug mode
setup_debug_mode(force_enable=True)

@measure_execution_time
def create_example_workflow():
    """Create a simple example workflow for debugging."""
    debug_log("Creating example workflow")
    
    workflow = Workflow(workflow_id="debug_example", name="Debug Example Workflow")
    
    # Task 1: Generate data
    async def generate_data(context):
        debug_log("Generating random data")
        
        # Simulate varying execution time
        execution_time = random.uniform(0.1, 0.5)
        time.sleep(execution_time)
        
        # Generate some example data
        data = {
            "user_id": random.randint(1000, 9999),
            "username": f"user_{random.randint(100, 999)}",
            "items": [
                {"id": i, "value": random.randint(1, 100)}
                for i in range(random.randint(3, 7))
            ],
            "timestamp": time.time()
        }
        
        debug_log("Generated data", data)
        
        # Dump variables for debugging
        local_vars = dump_variables()
        debug_log("Local variables in generate_data", local_vars)
        
        return data
    
    # Task 2: Process data
    async def process_data(context):
        input_data = context.get("generate_data", {})
        debug_log("Processing data", input_data)
        
        # Simulate varying execution time
        execution_time = random.uniform(0.2, 0.8)
        time.sleep(execution_time)
        
        # Process the data
        user_id = input_data.get("user_id", 0)
        username = input_data.get("username", "unknown")
        items = input_data.get("items", [])
        
        # Calculate some metrics
        total_value = sum(item.get("value", 0) for item in items)
        avg_value = total_value / len(items) if items else 0
        
        result = {
            "user_id": user_id,
            "username": username,
            "total_value": total_value,
            "avg_value": avg_value,
            "item_count": len(items),
            "processed_at": time.time()
        }
        
        debug_log("Processed data", result)
        
        # Randomly introduce an error for demonstration
        if random.random() < 0.3:
            debug_log("Simulating an error")
            raise ValueError("Simulated error in data processing")
        
        return result
    
    # Task 3: Generate report (always runs, even if task 2 fails)
    async def generate_report(context):
        debug_log("Generating report")
        
        # Check if we had an error in the previous task
        has_error = "error" in context and "process_data" in context.get("error", {})
        
        if has_error:
            error_info = context["error"]["process_data"]
            debug_log("Processing error detected", error_info)
            
            report = {
                "status": "error",
                "error": str(error_info.get("error", "Unknown error")),
                "timestamp": time.time(),
                "partial_data": context.get("generate_data", {})
            }
        else:
            processed_data = context.get("process_data", {})
            debug_log("Using processed data for report", processed_data)
            
            report = {
                "status": "success",
                "user_id": processed_data.get("user_id"),
                "username": processed_data.get("username"),
                "metrics": {
                    "total_value": processed_data.get("total_value"),
                    "avg_value": processed_data.get("avg_value"),
                    "item_count": processed_data.get("item_count")
                },
                "timestamp": time.time()
            }
        
        # Simulate report generation time
        time.sleep(random.uniform(0.1, 0.3))
        
        debug_log("Generated report", report)
        return report
    
    # Register tasks with the workflow
    task1 = Task(task_id="generate_data", name="Generate Data", handler=generate_data)
    task2 = Task(task_id="process_data", name="Process Data", handler=process_data, 
                depends_on=["generate_data"])
    task3 = Task(task_id="generate_report", name="Generate Report", handler=generate_report,
                depends_on=["process_data"], always_run=True)
    
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    
    return workflow

@measure_execution_time
def run_example():
    """Run the debug mode example."""
    logger.info("Starting Debug Mode Example")
    
    try:
        # Create the workflow
        workflow = create_example_workflow()
        
        # Initialize workflow engine
        engine = WorkflowEngine()
        
        # Run the workflow multiple times to generate more debug data
        for i in range(3):
            logger.info(f"\nRunning workflow iteration {i+1}")
            result = engine.run_workflow(workflow)
            
            # In debug mode, the result will contain a _debug field with detailed information
            if isinstance(result, dict) and "_debug" in result:
                debug_info = result["_debug"]
                logger.info(f"Workflow completed with {len(debug_info['execution_path'])} tasks executed")
                
                # Log performance summary
                performance = debug_info["performance_summary"]
                logger.info(f"Total execution time: {performance['total_time']:.4f}s")
                logger.info(f"Success rate: {performance['success_rate'] * 100:.1f}%")
                
                # Log slowest task
                slowest_task = performance["slowest_task"]
                if "name" in slowest_task:
                    logger.info(f"Slowest task: {slowest_task['name']} ({slowest_task['duration']:.4f}s)")
            else:
                logger.info("Workflow completed (debug info not available)")
            
            # Print the final result status
            status = "success"
            if "generate_report" in result:
                report = result["generate_report"]
                if isinstance(report, dict):
                    status = report.get("status", "unknown")
            
            logger.info(f"Final result status: {status}")
            
            # Wait a moment before the next iteration
            if i < 2:
                time.sleep(1)
        
        logger.info("\nDebug Mode Example Completed")
        
        # Print info about accessing debug features
        logger.info("\nDebug Features:")
        logger.info("1. Check the console output above for detailed debug logs.")
        logger.info("2. If using the web server, visit /debug for the debug panel.")
        logger.info("3. Review and use the debug utilities in core.utils.debug for more advanced debugging.")
        
    except Exception as e:
        logger.error(f"Error in debug example: {str(e)}")

if __name__ == "__main__":
    run_example() 