"""
Complex Workflow with Enhanced Variable Resolution and Data Validation.

This example demonstrates a production-ready workflow that uses
Dawn's improved task output handling, variable resolution, and
data validation capabilities in a complex analytics scenario.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, TypedDict, Literal

# Add parent directory to path to import the framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from core.agent import Agent
from core.task import Task, DirectHandlerTask, TaskOutput
from core.workflow import Workflow
from core.utils.variable_resolver import resolve_variables, get_variable_value
from core.utils.data_validator import (
    ValidationError, 
    validate_type, 
    validate_data, 
    format_validation_errors
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("complex_workflow")

# Load environment variables
load_dotenv()


# Define typed data structures for analytics workflow
class DataSource(TypedDict):
    """TypedDict for data source configuration."""
    name: str
    type: Literal["file", "database", "api"]
    path: Optional[str]
    connection_string: Optional[str]
    api_key: Optional[str]
    format: Optional[str]


class AnalyticsResult(TypedDict):
    """TypedDict for analytics result data."""
    metric_name: str
    value: Union[int, float, str]
    timestamp: str
    dimension: Optional[str]


class Report(TypedDict):
    """TypedDict for analytics report data."""
    title: str
    generated_at: str
    data_sources: List[str]
    metrics: List[AnalyticsResult]
    summary: str
    charts: Optional[List[Dict[str, Any]]]


# Sample data sources for demonstration
SAMPLE_SALES_DATA = [
    {"product": "Widget A", "region": "North", "sales": 342, "date": "2023-04-01"},
    {"product": "Widget B", "region": "South", "sales": 234, "date": "2023-04-01"},
    {"product": "Widget A", "region": "East", "sales": 156, "date": "2023-04-01"},
    {"product": "Widget C", "region": "West", "sales": 187, "date": "2023-04-01"},
    {"product": "Widget B", "region": "North", "sales": 432, "date": "2023-04-02"},
    {"product": "Widget C", "region": "East", "sales": 321, "date": "2023-04-02"},
    {"product": "Widget A", "region": "West", "sales": 176, "date": "2023-04-02"},
    {"product": "Widget B", "region": "South", "sales": 368, "date": "2023-04-02"}
]

SAMPLE_USER_DATA = [
    {"user_id": "U001", "region": "North", "activity": 56, "signup_date": "2023-03-15"},
    {"user_id": "U002", "region": "South", "activity": 32, "signup_date": "2023-03-20"},
    {"user_id": "U003", "region": "East", "activity": 89, "signup_date": "2023-03-10"},
    {"user_id": "U004", "region": "West", "activity": 42, "signup_date": "2023-03-22"},
    {"user_id": "U005", "region": "North", "activity": 63, "signup_date": "2023-03-18"}
]


# Task handler functions
def load_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load data from specified sources.
    
    Simulates loading data from various sources based on configuration.
    """
    # Get data source configurations
    data_sources = input_data.get("data_sources", [])
    
    # Validate data sources
    for source in data_sources:
        if not isinstance(source, dict):
            return {
                "success": False,
                "error": f"Invalid data source format: {source}",
                "error_type": "ValueError"
            }
        
        if "name" not in source or "type" not in source:
            return {
                "success": False,
                "error": f"Data source missing required fields: {source}",
                "error_type": "ValueError"
            }
    
    # Simulated data loading (in a real scenario this would access actual data sources)
    loaded_data = {}
    loaded_sources = []
    
    for source in data_sources:
        source_name = source["name"]
        source_type = source["type"]
        
        # Load appropriate sample data based on source configuration
        if source_name == "sales":
            loaded_data[source_name] = SAMPLE_SALES_DATA
            loaded_sources.append(source_name)
        elif source_name == "users":
            loaded_data[source_name] = SAMPLE_USER_DATA
            loaded_sources.append(source_name)
        else:
            # Mock empty data for unknown sources
            loaded_data[source_name] = []
            loaded_sources.append(source_name)
    
    # Return loaded data
    return {
        "success": True,
        "result": {
            "data": loaded_data,
            "loaded_sources": loaded_sources,
            "record_counts": {src: len(loaded_data[src]) for src in loaded_sources},
            "timestamp": datetime.now().isoformat()
        }
    }


def transform_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform data for analysis.
    
    Demonstrates data transformation with validation.
    """
    # Get input data
    raw_data = input_data.get("data", {})
    transformations = input_data.get("transformations", [])
    
    # Validate inputs
    if not isinstance(raw_data, dict):
        return {
            "success": False,
            "error": "Data must be a dictionary of named datasets",
            "error_type": "TypeError"
        }
    
    # Apply transformations
    transformed_data = {}
    transformation_log = []
    
    for dataset_name, dataset in raw_data.items():
        # Skip empty datasets
        if not dataset:
            continue
            
        # Apply dataset-specific transformations
        transformed_dataset = []
        
        for record in dataset:
            transformed_record = record.copy()  # Start with original record
            
            # Apply each transformation
            for transform in transformations:
                if transform.get("target") == dataset_name:
                    transform_type = transform.get("type")
                    
                    if transform_type == "rename_field":
                        old_field = transform.get("old_field")
                        new_field = transform.get("new_field")
                        if old_field in transformed_record:
                            transformed_record[new_field] = transformed_record.pop(old_field)
                            
                    elif transform_type == "calculate_field":
                        field = transform.get("field")
                        source_fields = transform.get("source_fields", [])
                        operation = transform.get("operation")
                        
                        if operation == "sum" and all(f in transformed_record for f in source_fields):
                            transformed_record[field] = sum(transformed_record[f] for f in source_fields)
                            
                    elif transform_type == "filter_field":
                        field = transform.get("field")
                        if field in transformed_record:
                            value = transformed_record[field]
                            min_value = transform.get("min_value")
                            max_value = transform.get("max_value")
                            
                            if (min_value is not None and value < min_value) or \
                               (max_value is not None and value > max_value):
                                # Skip this record
                                continue
            
            transformed_dataset.append(transformed_record)
            
        transformed_data[dataset_name] = transformed_dataset
        transformation_log.append({
            "dataset": dataset_name,
            "original_count": len(dataset),
            "transformed_count": len(transformed_dataset)
        })
    
    # Return transformed data
    return {
        "success": True,
        "result": {
            "data": transformed_data,
            "transformation_log": transformation_log
        }
    }


def analyze_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze transformed data to generate metrics.
    
    Demonstrates complex data analysis with structured output.
    """
    # Get transformed data
    data = input_data.get("data", {})
    metrics_config = input_data.get("metrics", [])
    
    # Validate inputs
    if not isinstance(data, dict):
        return {
            "success": False,
            "error": "Data must be a dictionary of datasets",
            "error_type": "TypeError"
        }
    
    if not metrics_config:
        return {
            "success": False,
            "error": "No metrics defined for analysis",
            "error_type": "ValueError"
        }
    
    # Calculate metrics
    results: List[AnalyticsResult] = []
    
    for metric in metrics_config:
        metric_name = metric.get("name")
        dataset_name = metric.get("dataset")
        calculation = metric.get("calculation")
        field = metric.get("field")
        dimension = metric.get("dimension")
        
        # Skip if missing required config
        if not all([metric_name, dataset_name, calculation, field]):
            continue
            
        # Get dataset
        dataset = data.get(dataset_name, [])
        if not dataset:
            continue
        
        # Calculate by dimension if specified
        if dimension:
            # Group data by dimension
            dimension_groups = {}
            for record in dataset:
                dimension_value = record.get(dimension)
                if dimension_value not in dimension_groups:
                    dimension_groups[dimension_value] = []
                dimension_groups[dimension_value].append(record)
            
            # Calculate metric for each dimension
            for dim_value, dim_data in dimension_groups.items():
                metric_value = None
                
                # Calculate metric value
                if calculation == "sum":
                    metric_value = sum(record.get(field, 0) for record in dim_data)
                elif calculation == "average":
                    values = [record.get(field, 0) for record in dim_data]
                    metric_value = sum(values) / len(values) if values else 0
                elif calculation == "count":
                    metric_value = len(dim_data)
                elif calculation == "max":
                    metric_value = max(record.get(field, 0) for record in dim_data)
                
                if metric_value is not None:
                    results.append({
                        "metric_name": f"{metric_name} by {dimension}",
                        "value": metric_value,
                        "timestamp": datetime.now().isoformat(),
                        "dimension": str(dim_value)
                    })
        else:
            # Calculate overall metric
            metric_value = None
            
            # Calculate metric value
            if calculation == "sum":
                metric_value = sum(record.get(field, 0) for record in dataset)
            elif calculation == "average":
                values = [record.get(field, 0) for record in dataset]
                metric_value = sum(values) / len(values) if values else 0
            elif calculation == "count":
                metric_value = len(dataset)
            elif calculation == "max":
                metric_value = max(record.get(field, 0) for record in dataset)
            
            if metric_value is not None:
                results.append({
                    "metric_name": metric_name,
                    "value": metric_value,
                    "timestamp": datetime.now().isoformat(),
                    "dimension": None
                })
    
    # Return analysis results
    return {
        "success": True,
        "result": {
            "metrics": results,
            "count": len(results)
        }
    }


def generate_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate analytics report from analysis results.
    
    Demonstrates combining data from multiple task outputs with validation.
    """
    # Get inputs
    metrics = input_data.get("metrics", [])
    data_sources = input_data.get("data_sources", [])
    title = input_data.get("title", "Analytics Report")
    include_charts = input_data.get("include_charts", True)
    
    # Validate inputs
    if not isinstance(metrics, list):
        return {
            "success": False,
            "error": "Metrics must be a list",
            "error_type": "TypeError"
        }
    
    # Create summary
    total_metrics = len(metrics)
    metrics_by_dimension = {}
    
    for metric in metrics:
        dimension = metric.get("dimension")
        if dimension:
            if dimension not in metrics_by_dimension:
                metrics_by_dimension[dimension] = []
            metrics_by_dimension[dimension].append(metric)
    
    # Generate simple summary
    summary = (
        f"Report contains {total_metrics} metrics from {len(data_sources)} data sources. "
        f"There are {len(metrics_by_dimension)} dimensions analyzed."
    )
    
    # Generate charts (simplified simulation)
    charts = None
    if include_charts:
        charts = []
        
        # Create summary chart
        if metrics_by_dimension:
            for dimension, dim_metrics in metrics_by_dimension.items():
                chart = {
                    "title": f"Metrics by {dimension}",
                    "type": "bar",
                    "data": {
                        "labels": [m.get("dimension") for m in dim_metrics],
                        "values": [m.get("value") for m in dim_metrics]
                    }
                }
                charts.append(chart)
    
    # Create the report
    report: Report = {
        "title": title,
        "generated_at": datetime.now().isoformat(),
        "data_sources": [src.get("name") for src in data_sources],
        "metrics": metrics,
        "summary": summary,
        "charts": charts
    }
    
    # Return the report
    return {
        "success": True,
        "result": {
            "report": report,
            "status": "completed"
        }
    }


def deliver_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deliver the generated report to specified destinations.
    
    Simulates report delivery with validation.
    """
    # Get inputs
    report = input_data.get("report", {})
    delivery_options = input_data.get("delivery_options", {})
    
    # Validate inputs
    if not isinstance(report, dict):
        return {
            "success": False,
            "error": "Report must be a dictionary",
            "error_type": "TypeError"
        }
    
    # Extract delivery configuration
    email = delivery_options.get("email")
    save_to_file = delivery_options.get("save_to_file", False)
    file_format = delivery_options.get("file_format", "json")
    
    delivery_results = []
    
    # Simulate email delivery
    if email:
        # In a real implementation, this would send an email
        delivery_results.append({
            "method": "email",
            "recipient": email,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
    
    # Simulate file save
    if save_to_file:
        # Generate a sample filename
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_format}"
        
        # In a real implementation, this would save to a file
        # For demonstration, we'll just pretend to save and print a sample
        if file_format == "json":
            # Sample JSON output (just converting to string for demonstration)
            report_content = json.dumps(report, indent=2)
            logger.info(f"Simulated report save to {filename}, content preview: {report_content[:100]}...")
        else:
            # Sample text format
            report_content = f"Report: {report.get('title')}\nGenerated: {report.get('generated_at')}\n"
            logger.info(f"Simulated report save to {filename}, content preview: {report_content[:100]}...")
        
        delivery_results.append({
            "method": "file",
            "filename": filename,
            "format": file_format,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
    
    # Return delivery results
    return {
        "success": True,
        "result": {
            "delivery_results": delivery_results,
            "delivered_at": datetime.now().isoformat()
        }
    }


def main():
    """Run the complex workflow with enhanced variable resolution example."""
    logger.info("Starting Complex Workflow with Enhanced Variable Resolution")
    
    # Create an Agent
    agent = Agent(
        agent_id="complex_analytics_agent",
        name="Complex Analytics Agent"
    )
    
    # Create a workflow
    workflow = Workflow(
        workflow_id="complex_analytics_workflow",
        name="Complex Analytics Workflow with Enhanced Resolution"
    )
    
    # Configure data sources
    data_sources = [
        {
            "name": "sales",
            "type": "file",
            "path": "/data/sales.csv",  # Simulated path
            "format": "csv"
        },
        {
            "name": "users",
            "type": "database",
            "connection_string": "postgresql://user:pass@localhost:5432/analytics",  # Simulated
            "query": "SELECT * FROM users"  # Simulated
        }
    ]
    
    # Configure data transformations
    transformations = [
        {
            "target": "sales",
            "type": "rename_field",
            "old_field": "product",
            "new_field": "product_name"
        },
        {
            "target": "users",
            "type": "filter_field",
            "field": "activity",
            "min_value": 30  # Filter out low activity users
        }
    ]
    
    # Configure metrics to calculate
    metrics_config = [
        {
            "name": "Total Sales",
            "dataset": "sales",
            "calculation": "sum",
            "field": "sales"
        },
        {
            "name": "Average Sales",
            "dataset": "sales",
            "calculation": "average",
            "field": "sales",
            "dimension": "region"
        },
        {
            "name": "User Count",
            "dataset": "users",
            "calculation": "count",
            "field": "user_id"
        },
        {
            "name": "Average User Activity",
            "dataset": "users",
            "calculation": "average",
            "field": "activity",
            "dimension": "region"
        }
    ]
    
    # Task 1: Load Data
    task1 = DirectHandlerTask(
        task_id="load_data",
        name="Load Data",
        handler=load_data_handler,
        input_data={
            "data_sources": data_sources
        },
        next_task_id_on_success="transform_data",
        validate_output=True
    )
    
    # Task 2: Transform Data
    task2 = DirectHandlerTask(
        task_id="transform_data",
        name="Transform Data",
        handler=transform_data_handler,
        input_data={
            "data": "${load_data.output_data.data}",
            "transformations": transformations
        },
        next_task_id_on_success="analyze_data",
        validate_input=True,
        validate_output=True
    )
    
    # Task 3: Analyze Data
    task3 = DirectHandlerTask(
        task_id="analyze_data",
        name="Analyze Data",
        handler=analyze_data_handler,
        input_data={
            "data": "${transform_data.output_data.data}",
            "metrics": metrics_config
        },
        next_task_id_on_success="generate_report",
        validate_input=True
    )
    
    # Task 4: Generate Report
    task4 = DirectHandlerTask(
        task_id="generate_report",
        name="Generate Report",
        handler=generate_report_handler,
        input_data={
            "metrics": "${analyze_data.output_data.metrics}",
            "data_sources": data_sources,
            "title": "Analytics Dashboard Report",
            "include_charts": True
        },
        next_task_id_on_success="deliver_report"
    )
    
    # Task 5: Deliver Report
    task5 = DirectHandlerTask(
        task_id="deliver_report",
        name="Deliver Report",
        handler=deliver_report_handler,
        input_data={
            "report": "${generate_report.output_data.report}",
            "delivery_options": {
                "email": "admin@example.com",
                "save_to_file": True,
                "file_format": "json"
            }
        }
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)
    workflow.add_task(task4)
    workflow.add_task(task5)
    
    # Load workflow into agent
    agent.load_workflow(workflow)
    
    # Run the workflow
    logger.info("Executing workflow")
    result = agent.run()
    
    # Print the final results
    logger.info("\n=== WORKFLOW RESULTS ===")
    logger.info(f"Workflow Status: {result['status']}")
    
    # Print key task outputs
    logger.info("\n=== KEY METRICS ===")
    
    # Get metrics from analysis task
    if "analyze_data" in workflow.tasks:
        analyze_task = workflow.tasks["analyze_data"]
        if analyze_task.status == "completed":
            metrics = analyze_task.get_output_value("metrics")
            if metrics:
                for metric in metrics:
                    name = metric.get("metric_name", "Unnamed Metric")
                    value = metric.get("value", "N/A")
                    dimension = metric.get("dimension", "Overall")
                    
                    if dimension:
                        logger.info(f"{name}: {value} ({dimension})")
                    else:
                        logger.info(f"{name}: {value}")
    
    # Print delivery results
    logger.info("\n=== REPORT DELIVERY ===")
    if "deliver_report" in workflow.tasks:
        deliver_task = workflow.tasks["deliver_report"]
        if deliver_task.status == "completed":
            delivery_results = deliver_task.get_output_value("delivery_results")
            if delivery_results:
                for delivery in delivery_results:
                    method = delivery.get("method", "Unknown")
                    status = delivery.get("status", "Unknown")
                    
                    if method == "email":
                        recipient = delivery.get("recipient", "Unknown")
                        logger.info(f"Email delivery to {recipient}: {status}")
                    elif method == "file":
                        filename = delivery.get("filename", "Unknown")
                        logger.info(f"File delivery to {filename}: {status}")
    
    logger.info("\nExample completed!")


if __name__ == "__main__":
    main() 