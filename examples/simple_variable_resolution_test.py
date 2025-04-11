#!/usr/bin/env python
"""
Simple Variable Resolution Test with DirectHandlerTask

This script demonstrates the improved variable resolution with nested data structures
and DirectHandlerTask. It doesn't require any external API calls to run.
"""  # noqa: D202

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask


def generate_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a nested data structure for testing."""
    print("\nGenerating nested data structure...")
    
    data = {
        "user": {
            "name": "Test User",
            "id": 123,
            "preferences": {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "mobile": False
                }
            }
        },
        "items": [
            {"id": 1, "name": "First Item", "tags": ["important", "new"]},
            {"id": 2, "name": "Second Item", "tags": ["archived"]}
        ],
        "metadata": {
            "generated": datetime.now().isoformat(),
            "version": "1.0"
        }
    }
    
    return {
        "success": True,
        "result": data
    }


def access_nested_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Access nested fields from input data."""
    print("\nAccessing nested data fields...")
    
    # Extract values from input
    user_name = input_data.get("user_name", "Unknown")
    theme = input_data.get("theme", "Unknown")
    email_notifications = input_data.get("email_notifications", False)
    first_item_name = input_data.get("first_item_name", "Unknown")
    first_item_tags = input_data.get("first_item_tags", [])
    
    print(f"- User Name: {user_name}")
    print(f"- Theme: {theme}")
    print(f"- Email Notifications: {email_notifications}")
    print(f"- First Item Name: {first_item_name}")
    print(f"- First Item Tags: {first_item_tags}")
    
    result = {
        "summary": f"User {user_name} prefers {theme} theme with email notifications set to {email_notifications}",
        "items": {
            "first_item": first_item_name,
            "tags_count": len(first_item_tags),
            "tags": first_item_tags
        }
    }
    
    return {
        "success": True,
        "result": result
    }


def final_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a final report from the processed data."""
    print("\nGenerating final report...")
    
    summary = input_data.get("summary", "No summary available")
    first_item = input_data.get("first_item", "Unknown")
    tags_count = input_data.get("tags_count", 0)
    
    print(f"- Summary: {summary}")
    print(f"- First Item: {first_item}")
    print(f"- Tags Count: {tags_count}")
    
    report = f"""
# Variable Resolution Test Report

## User Information
{summary}

## Item Information
- First Item: {first_item}
- Number of Tags: {tags_count}

## Test Summary
This report demonstrates successful variable resolution with nested data structures.

Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Write report to file
    file_path = os.path.join(output_dir, "variable_resolution_report.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    return {
        "success": True,
        "result": file_path
    }


def main():
    """Run the simple variable resolution test."""
    print("Starting Simple Variable Resolution Test with DirectHandlerTask")
    
    # Create a workflow
    workflow = Workflow(
        workflow_id="variable_resolution_test",
        name="Variable Resolution Test"
    )
    
    # Task 1: Generate nested data
    task1 = DirectHandlerTask(
        task_id="generate_data",
        name="Generate Nested Data",
        handler=generate_data_handler,
        input_data={},
        next_task_id_on_success="access_nested_data"
    )
    
    # Task 2: Access nested data via variable resolution
    task2 = DirectHandlerTask(
        task_id="access_nested_data",
        name="Access Nested Data",
        handler=access_nested_data_handler,
        input_data={
            "user_name": "${generate_data.output_data.result.user.name}",
            "theme": "${generate_data.output_data.result.user.preferences.theme}",
            "email_notifications": "${generate_data.output_data.result.user.preferences.notifications.email}",
            "first_item_name": "${generate_data.output_data.result.items[0].name}",
            "first_item_tags": "${generate_data.output_data.result.items[0].tags}"
        },
        next_task_id_on_success="generate_report"
    )
    
    # Task 3: Generate final report
    task3 = DirectHandlerTask(
        task_id="generate_report",
        name="Generate Final Report",
        handler=final_report_handler,
        input_data={
            "summary": "${access_nested_data.output_data.result.summary}",
            "first_item": "${access_nested_data.output_data.result.items.first_item}",
            "tags_count": "${access_nested_data.output_data.result.items.tags_count}"
        }
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    
    # Create Agent
    registry = get_registry() # Get the singleton registry
    agent = Agent(
        agent_id="simple_var_res_agent",
        name="Simple Variable Resolution Agent",
        tool_registry=registry # Pass the registry
    )
    agent.load_workflow(workflow)
    
    # Run workflow
    print("\nRunning workflow...")
    result = agent.run()
    
    # Display results
    if result:
        print("\n✅ Workflow completed successfully!")
        
        # Get output file path
        output_task = workflow.get_task("generate_report")
        if output_task and output_task.status == "completed" and output_task.output_data:
            file_path = output_task.output_data.get("result", "")
            
            if file_path and os.path.exists(file_path):
                print(f"\nReport saved to: {file_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        print("\nReport Content:")
                        print(f.read())
                except Exception as e:
                    print(f"Error reading report: {e}")
    else:
        print("\n❌ Workflow failed!")
        
        # Show task statuses
        print("\nTask Statuses:")
        for task_id in workflow.tasks:
            task = workflow.get_task(task_id)
            if task:
                print(f"- {task.name}: {task.status}")
                if task.status == "failed" and task.output_data:
                    print(f"  Error: {task.output_data.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main() 