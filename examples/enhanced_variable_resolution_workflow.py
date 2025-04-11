"""
Enhanced Variable Resolution and Data Validation Example.

This example demonstrates how to use Dawn's improved task output handling
and variable resolution capabilities with proper type validation.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Union

# Add parent directory to path to import the framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from core.agent import Agent
from core.task import Task, DirectHandlerTask, TaskOutput
from core.workflow import Workflow
from core.utils.variable_resolver import resolve_variables
from core.utils.data_validator import ValidationError, validate_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("enhanced_workflow")

# Load environment variables
load_dotenv()


# Define some typed handler functions for our DirectHandlerTasks
def process_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process input data and return structured results.
    
    Demonstrates using a dictionary-based handler with proper return type.
    """
    # Extract values from input (with proper validation)
    text = input_data.get("text", "")
    multiplier = input_data.get("multiplier", 1)
    
    if not isinstance(text, str):
        return {
            "success": False,
            "error": f"Expected text to be string, got {type(text).__name__}",
            "error_type": "TypeError"
        }
    
    if not isinstance(multiplier, int):
        return {
            "success": False,
            "error": f"Expected multiplier to be integer, got {type(multiplier).__name__}",
            "error_type": "TypeError"
        }
    
    # Process the data
    word_count = len(text.split())
    char_count = len(text)
    repeated_text = text * multiplier
    
    # Return structured result with strongly typed shape
    return {
        "success": True,
        "result": {
            "processed_text": repeated_text,
            "metrics": {
                "word_count": word_count,
                "char_count": char_count,
                "multiplier": multiplier
            },
            "summary": f"Processed {word_count} words with {char_count} characters"
        }
    }


def analyze_metrics_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze metrics data from previous task.
    
    Demonstrates accessing nested data from previous task outputs.
    """
    # Get metrics from input, which should come from previous task output
    metrics = input_data.get("metrics", {})
    threshold = input_data.get("threshold", 10)
    
    if not isinstance(metrics, dict):
        return {
            "success": False,
            "error": "Expected metrics to be a dictionary",
            "error_type": "TypeError"
        }
    
    # Extract metrics values
    word_count = metrics.get("word_count", 0)
    char_count = metrics.get("char_count", 0)
    
    # Analyze the metrics
    words_per_char_ratio = word_count / char_count if char_count > 0 else 0
    exceeds_threshold = word_count > threshold
    
    # Return analysis results
    return {
        "success": True,
        "result": {
            "analysis": {
                "words_per_char_ratio": round(words_per_char_ratio, 4),
                "exceeds_threshold": exceeds_threshold,
                "word_count": word_count,
                "threshold": threshold
            },
            "summary": f"Text has {word_count} words (threshold: {threshold})"
        }
    }


def generate_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a report based on processed data and analysis.
    
    Demonstrates combining data from multiple previous tasks.
    """
    # Get data from input
    processed_text = input_data.get("processed_text", "")
    analysis = input_data.get("analysis", {})
    format_type = input_data.get("format", "text")
    
    # Generate appropriate report format
    if format_type == "json":
        report = {
            "text": processed_text[:50] + "..." if len(processed_text) > 50 else processed_text,
            "analysis": analysis,
            "generated_at": "2023-04-15T12:00:00Z"  # Normally use actual timestamp
        }
        return {
            "success": True,
            "result": {
                "report": report,
                "format": "json"
            }
        }
    else:
        # Text format
        report_lines = [
            "=== DATA ANALYSIS REPORT ===",
            f"Text Sample: {processed_text[:50]}..." if len(processed_text) > 50 else processed_text,
            f"Word Count: {analysis.get('word_count', 0)}",
            f"Threshold Check: {'Passed' if analysis.get('exceeds_threshold', False) else 'Failed'}",
            f"Words/Char Ratio: {analysis.get('words_per_char_ratio', 0)}",
            "=========================="
        ]
        return {
            "success": True,
            "result": {
                "report": "\n".join(report_lines),
                "format": "text"
            }
        }


def main():
    """Run the enhanced variable resolution example workflow."""
    logger.info("Starting Enhanced Variable Resolution Example")
    
    # Create an Agent
    agent = Agent(
        agent_id="enhanced_var_resolution_agent",
        name="Enhanced Variable Resolution Agent"
    )
    
    # Create a workflow
    workflow = Workflow(
        workflow_id="enhanced_variable_workflow",
        name="Enhanced Variable Resolution Workflow"
    )
    
    # Task 1: Process input text
    task1 = DirectHandlerTask(
        task_id="process_text",
        name="Process Text",
        handler=process_data_handler,
        input_data={
            "text": "This is a sample text to demonstrate variable resolution",
            "multiplier": 2
        },
        next_task_id_on_success="analyze_metrics"
    )
    
    # Task 2: Analyze the metrics from Task 1 using variable resolution
    task2 = DirectHandlerTask(
        task_id="analyze_metrics",
        name="Analyze Metrics",
        handler=analyze_metrics_handler,
        input_data={
            # Demonstrates accessing nested data with dot notation
            "metrics": "${process_text.output_data.metrics}",
            "threshold": 5
        },
        next_task_id_on_success="generate_report"
    )
    
    # Task 3: Generate a report combining data from previous tasks
    task3 = DirectHandlerTask(
        task_id="generate_report",
        name="Generate Report",
        handler=generate_report_handler,
        input_data={
            # Demonstrates accessing deeply nested data
            "processed_text": "${process_text.output_data.processed_text}",
            # Demonstrates accessing nested object from another task
            "analysis": "${analyze_metrics.output_data.analysis}",
            "format": "text"
        }
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    
    # Load workflow into agent
    agent.load_workflow(workflow)
    
    # Run the workflow
    logger.info("Executing workflow")
    result = agent.run()
    
    # Print the final results
    logger.info("\n=== WORKFLOW RESULTS ===")
    logger.info(f"Workflow Status: {result['status']}")
    
    # Print task outputs with proper path resolution for demonstration
    logger.info("\n=== TASK OUTPUTS ===")
    for task_id, task in workflow.tasks.items():
        task_data = task.to_dict()
        logger.info(f"\n{task_data['name']} (ID: {task_id}):")
        logger.info(f"Status: {task_data['status']}")
        
        if task_data["status"] == "completed":
            # For the report task, show the final report
            if task_id == "generate_report":
                report = task.get_output_value("report")
                logger.info(f"\nFinal Report:\n{report}")
            else:
                # For other tasks, show a summary of their outputs
                if "result" in task_data["output_data"]:
                    result_summary = task_data["output_data"]["result"].get("summary", "No summary available")
                    logger.info(f"Result Summary: {result_summary}")
        elif task_data["status"] == "failed":
            logger.error(f"Error: {task_data['output_data'].get('error', 'Unknown error')}")
    
    logger.info("\n=== DEMONSTRATION OF PATH RESOLUTION ===")
    # Demonstrate manual variable resolution
    context = {}
    for task_id, task in workflow.tasks.items():
        task_dict = task.to_dict()
        context[task_id] = {
            "id": task_id,
            "status": task_dict["status"],
            "output_data": task_dict["output_data"]
        }
    
    # Demonstrate resolving various paths with different styles
    paths_to_resolve = [
        "process_text.output_data.metrics.word_count",
        "analyze_metrics.output_data.analysis.exceeds_threshold",
        "generate_report.output_data.format"
    ]
    
    logger.info("Resolving individual paths:")
    for path in paths_to_resolve:
        template = f"${{{path}}}"
        resolved = resolve_variables(template, context)
        logger.info(f"Path: {path} -> Value: {resolved}")
    
    # Demonstrate resolving a complex object with nested variables
    template_object = {
        "summary": {
            "text_info": {
                "word_count": "${process_text.output_data.metrics.word_count}",
                "char_count": "${process_text.output_data.metrics.char_count}"
            },
            "analysis_result": "${analyze_metrics.output_data.analysis.exceeds_threshold}",
            "report_format": "${generate_report.output_data.format}"
        }
    }
    
    logger.info("\nResolving nested object with variables:")
    resolved_object = resolve_variables(template_object, context)
    import json
    logger.info(json.dumps(resolved_object, indent=2))
    
    logger.info("\nExample completed!")


if __name__ == "__main__":
    main() 