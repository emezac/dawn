"""
Simple DirectHandlerTask Example with Improved Variable Resolution

This example demonstrates:
1. Using DirectHandlerTask for custom processing
2. The improved variable resolution capabilities
3. Executing a workflow with the WorkflowEngine

No external API calls are needed to run this example.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path to import framework modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.engine import WorkflowEngine
from core.llm.interface import LLMInterface
from core.task import DirectHandlerTask, Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow


# Define DirectHandler functions for the workflow
def generate_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate sample data with nested structure.
    
    Args:
        input_data: Dictionary containing parameters
        
    Returns:
        Dictionary with generated data
    """
    try:
        # Get parameters with defaults
        user_id = input_data.get("user_id", 12345)
        user_name = input_data.get("user_name", "Sample User")
        
        # Create a nested data structure
        result = {
            "user": {
                "id": user_id,
                "name": user_name,
                "metadata": {
                    "joined_date": "2023-04-15",
                    "status": "active",
                    "settings": {
                        "theme": "dark",
                        "notifications": True
                    }
                }
            },
            "metrics": {
                "views": 1250,
                "actions": 75,
                "conversion_rate": 0.06
            },
            "tags": ["user", "active", "premium"]
        }
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate data: {str(e)}",
            "error_type": type(e).__name__
        }


def process_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process data using values from previous task.
    
    Args:
        input_data: Dictionary containing data to process
        
    Returns:
        Dictionary with processed data
    """
    try:
        # Extract values from input
        user_name = input_data.get("user_name", "Unknown")
        theme = input_data.get("theme", "default")
        tags = input_data.get("tags", [])
        views = input_data.get("views", 0)
        
        # Process the data
        processed_data = {
            "summary": f"User {user_name} has a {theme} theme preference",
            "tag_count": len(tags),
            "popular": views > 1000,
            "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            "success": True,
            "result": processed_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to process data: {str(e)}",
            "error_type": type(e).__name__
        }


def generate_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a final report using processed data.
    
    Args:
        input_data: Dictionary containing data for the report
        
    Returns:
        Dictionary with the generated report
    """
    try:
        # Extract values
        summary = input_data.get("summary", "No summary available")
        tag_count = input_data.get("tag_count", 0)
        is_popular = input_data.get("is_popular", False)
        timestamp = input_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Generate report content
        popularity_status = "popular" if is_popular else "not popular"
        report = f"""# User Report

## Summary
{summary}

## Details
- Tags: {tag_count}
- Status: {popularity_status}
- Generated at: {timestamp}

## Recommendations
- {"Increase promotion for this popular user" if is_popular else "Engage with this user to increase activity"}
- {"Analyze tags for content preferences" if tag_count > 0 else "Encourage user to add interest tags"}

"""
        
        return {
            "success": True,
            "result": report
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate report: {str(e)}",
            "error_type": type(e).__name__
        }


def write_file_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        input_data: Dictionary containing file path and content
        
    Returns:
        Dictionary with the result
    """
    try:
        file_path = input_data.get("file_path")
        content = input_data.get("content", "")
        
        if not file_path:
            return {
                "success": False,
                "error": "No file path provided",
                "error_type": "InputValidationError"
            }
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return {
            "success": True,
            "result": file_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to write file: {str(e)}",
            "error_type": type(e).__name__
        }


def main():
    """Run the example workflow."""
    print("=== Starting Simple DirectHandlerTask Example ===")
    
    # Create workflow
    workflow = Workflow(
        workflow_id="simple_direct_handler_workflow",
        name="Simple DirectHandlerTask Example"
    )
    
    # Task 1: Generate sample data
    task1 = DirectHandlerTask(
        task_id="generate_data_task",
        name="Generate Sample Data",
        handler=generate_data_handler,
        input_data={
            "user_id": 42,
            "user_name": "Alice Smith"
        },
        next_task_id_on_success="process_data_task"
    )
    
    # Task 2: Process data with input from Task 1 using variable resolution
    task2 = DirectHandlerTask(
        task_id="process_data_task",
        name="Process Data",
        handler=process_data_handler,
        input_data={
            "user_name": "${generate_data_task.output_data.result.user.name}",
            "theme": "${generate_data_task.output_data.result.user.metadata.settings.theme}",
            "tags": "${generate_data_task.output_data.result.tags}",
            "views": "${generate_data_task.output_data.result.metrics.views}"
        },
        next_task_id_on_success="generate_report_task"
    )
    
    # Task 3: Generate report with processed data
    task3 = DirectHandlerTask(
        task_id="generate_report_task",
        name="Generate Report",
        handler=generate_report_handler,
        input_data={
            "summary": "${process_data_task.output_data.result.summary}",
            "tag_count": "${process_data_task.output_data.result.tag_count}",
            "is_popular": "${process_data_task.output_data.result.popular}",
            "timestamp": "${process_data_task.output_data.result.processed_at}"
        },
        next_task_id_on_success="write_report_task"
    )
    
    # Task 4: Write the report to a file
    task4 = DirectHandlerTask(
        task_id="write_report_task",
        name="Write Report to File",
        handler=write_file_handler,
        input_data={
            "file_path": os.path.join(os.path.dirname(__file__), "output", "user_report.md"),
            "content": "${generate_report_task.output_data.result}"
        }
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    workflow.add_task(task4)
    
    # Create an agent and run the workflow
    print("\nInitializing Agent...")
    registry = ToolRegistry()
    llm_interface = LLMInterface()
    
    agent = Agent(
        agent_id="direct_handler_agent",
        name="DirectHandlerTask Example Agent",
        llm_interface=llm_interface,
        tool_registry=registry
    )
    agent.load_workflow(workflow)
    
    # Run the workflow
    print("\nExecuting workflow...")
    results = agent.run()
    
    # Display the results
    print("\nWorkflow execution completed!")
    print(f"Status: {results.get('status')}")
    
    # Check if the workflow was successful
    if results.get('status') == 'completed':
        # Print the output of each task
        print("\nTask Outputs:")
        tasks_data = results.get('tasks', {})
        for task_id in workflow.task_order:
            if task_id in tasks_data:
                task_data = tasks_data[task_id]
                task_status = task_data.get('status', 'unknown')
                print(f"  {task_id}: {task_status}")
        
        # Get the report file path
        report_file_path = None
        if 'write_report_task' in tasks_data:
            write_task_data = tasks_data['write_report_task']
            if write_task_data.get('status') == 'completed':
                output_data = write_task_data.get('output_data', {})
                report_file_path = output_data.get('result')
        
        # Read and print the report file
        if report_file_path:
            try:
                with open(report_file_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                print("\nFinal Report Content:\n")
                print(report_content)
            except Exception as e:
                print(f"Error reading report file: {e}")
    else:
        print("Workflow failed to complete successfully.")
    
    print("\n=== Example Completed ===")


if __name__ == "__main__":
    main() 