"""
Task Output Improvements Example.

This example demonstrates the improved task output handling capabilities
with proper typing and structured data.
"""

# Standard imports
import sys
import os
import json
from typing import Dict, Any, List, Optional, TypedDict, Union

# Set up path to import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task import Task, DirectHandlerTask, TaskOutput


# Define some typed structures for demonstration
class MetricsData(TypedDict):
    """TypedDict for metrics data."""
    count: int
    average: float
    max_value: Optional[float]


class ResultData(TypedDict):
    """TypedDict for task result data."""
    success: bool
    message: str
    metrics: Optional[MetricsData]
    items: List[str]


# Define handler functions
def generate_metrics(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate metrics from input data.
    
    Args:
        input_data: Dictionary with values to process
        
    Returns:
        Dictionary with metrics result
    """
    # Extract values
    values = input_data.get("values", [])
    if not values:
        return {
            "success": False,
            "error": "No values provided",
            "error_type": "ValueError"
        }
    
    # Calculate metrics
    count = len(values)
    total = sum(values)
    average = total / count if count > 0 else 0
    max_value = max(values) if values else None
    
    # Return typed metrics
    metrics: MetricsData = {
        "count": count,
        "average": average,
        "max_value": max_value
    }
    
    # Create structured result
    result: ResultData = {
        "success": True,
        "message": f"Processed {count} values",
        "metrics": metrics,
        "items": [str(v) for v in values]
    }
    
    return {
        "success": True,
        "result": result
    }


def format_output(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the metrics into a readable output.
    
    Args:
        input_data: Dictionary with metrics to format
        
    Returns:
        Dictionary with formatted output
    """
    # Extract metrics from input
    metrics = input_data.get("metrics", {})
    if not metrics:
        return {
            "success": False,
            "error": "No metrics provided",
            "error_type": "ValueError"
        }
    
    # Get metrics values
    count = metrics.get("count", 0)
    average = metrics.get("average", 0.0)
    max_value = metrics.get("max_value")
    
    # Format the output
    lines = [
        "=== Metrics Summary ===",
        f"Count: {count}",
        f"Average: {average:.2f}",
    ]
    
    if max_value is not None:
        lines.append(f"Maximum: {max_value:.2f}")
    
    lines.append("=====================")
    formatted_output = "\n".join(lines)
    
    return {
        "success": True,
        "result": {
            "formatted_text": formatted_output,
            "raw_metrics": metrics
        }
    }


def main():
    """Run the task output improvement example."""
    print("=== Task Output Improvements Example ===\n")
    
    # Sample data
    sample_values = [10, 25, 15, 30, 20]
    
    # Create tasks
    task1 = DirectHandlerTask(
        task_id="metrics_task",
        name="Generate Metrics",
        handler=generate_metrics,
        input_data={"values": sample_values}
    )
    
    # Execute first task
    print("Executing metrics calculation task...")
    result1 = task1.execute()
    
    if not result1.get("success", False):
        print(f"Error in task1: {result1.get('error', 'Unknown error')}")
        return
    
    # Store output in task
    task1.set_output(result1)
    print("Task 1 completed successfully")
    
    # Extract the metrics from the first task
    metrics = task1.output_data.get("result", {}).get("metrics", {})
    print(f"Metrics from task 1: {json.dumps(metrics, indent=2)}")
    
    # Create second task with output from first task
    task2 = DirectHandlerTask(
        task_id="format_task",
        name="Format Output",
        handler=format_output,
        input_data={"metrics": metrics}
    )
    
    # Execute second task
    print("\nExecuting formatting task...")
    result2 = task2.execute()
    
    if not result2.get("success", False):
        print(f"Error in task2: {result2.get('error', 'Unknown error')}")
        return
        
    # Store output in task
    task2.set_output(result2)
    print("Task 2 completed successfully")
    
    # Display the formatted output
    formatted_text = task2.output_data.get("result", {}).get("formatted_text", "No output available")
    print("\nFormatted Output:")
    print(formatted_text)
    
    # Demonstrate using get_output_value
    print("\nDemonstrating get_output_value:")
    metrics_count = task1.get_output_value("result.metrics.count")
    metrics_average = task1.get_output_value("result.metrics.average")
    print(f"Count from get_output_value: {metrics_count}")
    print(f"Average from get_output_value: {metrics_average}")
    
    print("\n=== Example Completed ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        print(traceback.format_exc()) 