"""
Simplified example demonstrating improved variable resolution.

A minimal example showing the enhanced variable resolution capabilities
without complex dependencies.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task import DirectHandlerTask
from core.utils.variable_resolver import resolve_variables

# Simple handler functions
def data_generator_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate sample data with nested structure."""
    print("Executing data_generator_handler")
    
    # Create a sample nested data structure
    result = {
        "user": {
            "id": input_data.get("user_id", 1),
            "name": input_data.get("name", "Default User"),
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

def data_processor_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data using values from previous task."""
    print("Executing data_processor_handler")
    print(f"Input data: {json.dumps(input_data, indent=2)}")
    
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
        "processed_at": "2023-04-15T12:00:00Z"
    }
    
    return {
        "success": True,
        "result": processed_data
    }

def main():
    """Run the simplified variable resolution example."""
    print("=== Starting Simplified Variable Resolution Example ===")
    
    # Create the first task
    print("Creating first task (data generation)...")
    task1 = DirectHandlerTask(
        task_id="generate_data",
        name="Generate Data",
        handler=data_generator_handler,
        input_data={
            "user_id": 123,
            "name": "Alice Smith"
        }
    )
    
    # Execute the first task
    print("Executing first task...")
    task1_result = task1.execute()
    print(f"Task 1 execution success: {task1_result.get('success', False)}")
    if task1_result.get("success"):
        task1.set_output(task1_result)
    else:
        print(f"Task 1 failed: {task1_result.get('error', 'Unknown error')}")
        return
    
    # Create a context from the first task's output
    context = {
        "generate_data": {
            "id": task1.id,
            "status": "completed",
            "output_data": task1.output_data
        }
    }
    
    # Define input for the second task with variable references
    task2_input = {
        "user_name": "${generate_data.output_data.result.user.name}",
        "theme": "${generate_data.output_data.result.user.metadata.settings.theme}",
        "tags": "${generate_data.output_data.result.tags}",
        "views": "${generate_data.output_data.result.metrics.views}"
    }
    
    # Resolve variables
    print("\nResolving variables...")
    resolved_input = resolve_variables(task2_input, context)
    print(f"Resolved input: {json.dumps(resolved_input, indent=2)}")
    
    # Create and execute the second task
    print("\nCreating second task (data processing)...")
    task2 = DirectHandlerTask(
        task_id="process_data",
        name="Process Data",
        handler=data_processor_handler,
        input_data=resolved_input
    )
    
    print("Executing second task...")
    task2_result = task2.execute()
    print(f"Task 2 execution success: {task2_result.get('success', False)}")
    if task2_result.get("success"):
        task2.set_output(task2_result)
        
        # Print the result
        print("\n=== Results ===")
        summary = task2.output_data.get("result", {}).get("summary", "No summary available")
        print(f"Summary: {summary}")
        
        # Demonstrate accessing nested data from task outputs
        context["process_data"] = {
            "id": task2.id,
            "status": "completed",
            "output_data": task2.output_data
        }
        
        # Define some test variable paths
        test_paths = [
            "${generate_data.output_data.result.user.id}",
            "${generate_data.output_data.result.tags[0]}",
            "${generate_data.output_data.result.metrics.conversion_rate}",
            "${process_data.output_data.result.popular}",
            "${process_data.output_data.result.tag_count}"
        ]
        
        print("\n=== Variable Resolution Examples ===")
        for path in test_paths:
            value = resolve_variables(path, context)
            print(f"{path} -> {value}")
    else:
        print(f"Task 2 failed: {task2_result.get('error', 'Unknown error')}")
    
    print("\n=== Example Completed ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        print(traceback.format_exc()) 