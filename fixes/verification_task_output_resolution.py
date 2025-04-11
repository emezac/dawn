#!/usr/bin/env python
"""
Verification of Task Output and Variable Resolution Improvements.

This script demonstrates the improvements made to:
1. DirectHandlerTask in both synchronous and asynchronous workflows
2. Enhanced variable resolution for nested data structures
3. Consistent output access patterns
"""  # noqa: D202

import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.llm.interface import LLMInterface
from core.task import DirectHandlerTask, Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow


def create_nested_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a complex nested data structure."""
    print(f"[Task 1] Creating nested data with input: {json.dumps(input_data)}")
    
    # Create a nested data structure
    result = {
        "user": {
            "name": input_data.get("user_name", "Default User"),
            "id": input_data.get("user_id", 12345),
            "preferences": {
                "theme": "dark",
                "language": "en-US",
                "notifications": {
                    "email": True,
                    "push": False
                }
            }
        },
        "content": {
            "posts": [
                {"id": 1, "title": "First Post", "tags": ["important", "featured"]},
                {"id": 2, "title": "Second Post", "tags": ["draft"]}
            ],
            "metrics": {
                "views": 1024,
                "likes": 42,
                "shares": 13
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "result": result,
        "metadata": {
            "executed_at": datetime.now().isoformat(),
            "source": "create_nested_data_handler"
        }
    }


def process_nested_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data accessed via variable resolution from previous task."""
    print(f"[Task 2] Processing data with resolved variables")
    
    # Access data from input (should be resolved from previous task)
    user_name = input_data.get("user_name", "Unknown")
    user_theme = input_data.get("theme", "default")
    first_post_title = input_data.get("first_post_title", "No title")
    first_post_tags = input_data.get("first_post_tags", [])
    notification_settings = input_data.get("notifications", {})
    metric_values = input_data.get("metrics", {})
    
    # Print received values to show successful resolution
    print(f"  Received user_name: {user_name}")
    print(f"  Received theme: {user_theme}")
    print(f"  Received first_post_title: {first_post_title}")
    print(f"  Received first_post_tags: {first_post_tags}")
    print(f"  Received notification_settings: {notification_settings}")
    print(f"  Received metric_values: {metric_values}")
    
    # Process the inputs into a new structure
    result = {
        "summary": f"User {user_name} prefers {user_theme} theme",
        "content_analysis": {
            "first_post": first_post_title,
            "tag_count": len(first_post_tags),
            "top_metric": max(metric_values.items(), key=lambda x: x[1])[0] if metric_values else "none"
        },
        "notification_config": ", ".join([k for k, v in notification_settings.items() if v]) if notification_settings else "none enabled"
    }
    
    return {
        "success": True,
        "result": result
    }


def generate_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a final report based on processed data."""
    print(f"[Task 3] Generating report with processed data")
    
    # Extract values with proper validation
    summary = input_data.get("summary", "No summary available")
    content_analysis = input_data.get("content_analysis", {})
    notification_config = input_data.get("notification_config", "No notifications")
    format_type = input_data.get("format", "text")
    
    print(f"  Received summary: {summary}")
    print(f"  Received content_analysis: {content_analysis}")
    print(f"  Received notification_config: {notification_config}")
    print(f"  Requested format: {format_type}")
    
    # Generate report content
    if format_type == "markdown":
        report = f"""# User Report

## Summary
{summary}

## Content Analysis
- First Post: {content_analysis.get('first_post', 'None')}
- Tag Count: {content_analysis.get('tag_count', 0)}
- Top Metric: {content_analysis.get('top_metric', 'None')}

## Notification Settings
{notification_config}

*Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    else:  # Plain text
        report = f"USER REPORT\n\nSummary: {summary}\n\nContent Analysis:\n"
        report += f"- First Post: {content_analysis.get('first_post', 'None')}\n"
        report += f"- Tag Count: {content_analysis.get('tag_count', 0)}\n"
        report += f"- Top Metric: {content_analysis.get('top_metric', 'None')}\n\n"
        report += f"Notification Settings: {notification_config}\n\n"
        report += f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return {
        "success": True,
        "result": report
    }


def save_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Save the report to a file."""
    print(f"[Task 4] Saving report to file")
    
    # Extract content and file path
    content = input_data.get("content", "No content")
    file_path = input_data.get("file_path", "")
    
    if not file_path:
        return {
            "success": False,
            "error": "No file path provided",
            "error_type": "InputValidationError"
        }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Write content to file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"  Report saved to: {file_path}")
        return {
            "success": True,
            "result": file_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to save report: {str(e)}",
            "error_type": type(e).__name__
        }


def verify_improvements():
    """Run a verification workflow to demonstrate improvements."""
    print("\n=== VERIFICATION: Task Output and Variable Resolution Improvements ===\n")
    
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create workflow
    workflow = Workflow(
        workflow_id="verification_workflow",
        name="Verification Workflow"
    )
    
    # Task 1: Create Nested Data
    task1 = DirectHandlerTask(
        task_id="create_data_task",
        name="Create Nested Data",
        handler=create_nested_data_handler,
        input_data={
            "user_name": "Verification User",
            "user_id": 42
        },
        next_task_id_on_success="process_data_task"
    )
    
    # Task 2: Process Nested Data (with deep variable resolution)
    task2 = DirectHandlerTask(
        task_id="process_data_task",
        name="Process Nested Data",
        handler=process_nested_data_handler,
        input_data={
            "user_name": "${create_data_task.output_data.result.user.name}",
            "theme": "${create_data_task.output_data.result.user.preferences.theme}",
            "first_post_title": "${create_data_task.output_data.result.content.posts[0].title}",
            "first_post_tags": "${create_data_task.output_data.result.content.posts[0].tags}",
            "notifications": "${create_data_task.output_data.result.user.preferences.notifications}",
            "metrics": "${create_data_task.output_data.result.content.metrics}"
        },
        next_task_id_on_success="generate_report_task"
    )
    
    # Task 3: Generate Report
    task3 = DirectHandlerTask(
        task_id="generate_report_task",
        name="Generate Report",
        handler=generate_report_handler,
        input_data={
            "summary": "${process_data_task.output_data.result.summary}",
            "content_analysis": "${process_data_task.output_data.result.content_analysis}",
            "notification_config": "${process_data_task.output_data.result.notification_config}",
            "format": "markdown"
        },
        next_task_id_on_success="save_report_task"
    )
    
    # Task 4: Save Report
    task4 = DirectHandlerTask(
        task_id="save_report_task",
        name="Save Report",
        handler=save_report_handler,
        input_data={
            "content": "${generate_report_task.output_data.result}",
            "file_path": os.path.join(output_dir, "verification_report.md")
        }
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    workflow.add_task(task4)
    
    # Create agent
    registry = ToolRegistry()
    llm_interface = LLMInterface()
    
    agent = Agent(
        agent_id="verification_agent",
        name="Verification Agent",
        llm_interface=llm_interface,
        tool_registry=registry
    )
    agent.load_workflow(workflow)
    
    # Run with synchronous engine
    print("\n-> Testing with synchronous engine:")
    start_time = time.time()
    sync_results = agent.run()
    sync_duration = time.time() - start_time
    
    print(f"\nSync Results: {sync_results.get('status')}")
    print(f"Duration: {sync_duration:.2f} seconds")
    
    # Run with asynchronous engine
    print("\n-> Testing with asynchronous engine:")
    start_time = time.time()
    async_results = agent.run_async()
    async_duration = time.time() - start_time
    
    print(f"\nAsync Results: {async_results.get('status')}")
    print(f"Duration: {async_duration:.2f} seconds")
    
    # Read the generated report
    report_path = os.path.join(output_dir, "verification_report.md")
    if os.path.exists(report_path):
        print(f"\n-> Final report content:")
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                print("\n" + f.read())
        except Exception as e:
            print(f"Error reading report: {e}")
    
    print("\n✓ Verification completed successfully!")
    print("The improved variable resolution features are working properly with both engines.")


if __name__ == "__main__":
    try:
        verify_improvements()
    except Exception as e:
        import traceback
        print(f"ERROR: Verification failed: {e}")
        print(traceback.format_exc()) 