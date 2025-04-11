#!/usr/bin/env python
"""
Simplified Compliance Workflow Example

This example demonstrates a compliance document analysis workflow
using wrapper functions for framework compatibility.
"""  # noqa: D202

import logging
import os
import tempfile
import json
from typing import Any, Dict, List, Optional

from core.agent import Agent
from core.task import Task, DirectHandlerTask
from core.tools.registry import ToolRegistry
from core.workflow import Workflow

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function for parsing structured task outputs
def extract_task_output(task_output, field_path=None):
    """
    Extract data from task output using a field path.
    
    Args:
        task_output: The task output data to extract from
        field_path: Optional dot-notation path to extract (e.g., "result.summary")
        
    Returns:
        The extracted data or the original output if no path is provided
    """
    if not task_output:
        return None
        
    # If no specific field path is requested, try to get the most useful representation
    if not field_path:
        # For LLM tasks (which typically have a response field)
        if isinstance(task_output, dict) and "response" in task_output:
            # Try to parse it as JSON if it looks like JSON
            response = task_output.get("response", "")
            if response and isinstance(response, str) and (response.strip().startswith("{") or response.strip().startswith("[")):
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return response
            return response
        # For tool tasks (which typically have a result field)
        elif isinstance(task_output, dict) and "result" in task_output:
            return task_output.get("result")
        # Otherwise, just return the output as is
        return task_output
    
    # If a specific field path is provided, navigate the object structure
    current = task_output
    for field in field_path.split("."):
        if isinstance(current, dict) and field in current:
            current = current[field]
        else:
            # If the field is not found, try to parse JSON if this is a string
            if isinstance(current, str) and (current.strip().startswith("{") or response.strip().startswith("[")):
                try:
                    parsed = json.loads(current)
                    if isinstance(parsed, dict) and field in parsed:
                        current = parsed[field]
                        continue
                except json.JSONDecodeError:
                    pass
            # If we couldn't find or parse the field, return None
            return None
    return current


# Compatibility wrapper functions
def create_task(
    task_id,
    name,
    is_llm_task=False,
    tool_name=None,
    input_data=None,
    max_retries=0,
    next_task_id_on_success=None,
    next_task_id_on_failure=None,
    condition=None,
    parallel=False,
    use_file_search=False,
    file_search_vector_store_ids=None,
    file_search_max_results=5,
    dependencies=None,
    **kwargs,
):
    """
    Wrapper to create a Task with support for dependencies parameter.
    In the original Task class, dependencies is not supported.
    """
    # Create the task with standard parameters
    task = Task(
        task_id=task_id,
        name=name,
        is_llm_task=is_llm_task,
        tool_name=tool_name,
        input_data=input_data,
        max_retries=max_retries,
        next_task_id_on_success=next_task_id_on_success,
        next_task_id_on_failure=next_task_id_on_failure,
        condition=condition,
        parallel=parallel,
        use_file_search=use_file_search,
        file_search_vector_store_ids=file_search_vector_store_ids,
        file_search_max_results=file_search_max_results,
    )

    # Store dependencies as an attribute (though it won't be used by the framework)
    if dependencies:
        task.dependencies = dependencies
    else:
        task.dependencies = []

    return task


def run_agent_with_input(agent, initial_input=None):
    """Wrapper function to run an agent with initial input."""
    logger.info(f"Running agent with initial input: {initial_input}")
    # Store the input on the agent for reference (though not used internally)
    agent.initial_input = initial_input if initial_input else {}
    # Run the agent normally
    return agent.run()


def get_task_history(workflow):
    """Extract task history from a workflow."""
    if not workflow or not hasattr(workflow, "tasks"):
        return []

    history = []
    for task_id, task in workflow.tasks.items():
        history.append({"task_id": task_id, "status": task.status, "output_data": task.output_data})
    return history


# Custom tool handler definitions
def log_alert_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Log an alert message at the specified level."""
    message = input_data.get("message", "No message provided")
    level = input_data.get("level", "INFO").upper()
    
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = log_levels.get(level, logging.INFO)
    logger.log(log_level, f"ALERT: {message}")
    
    return {
        "success": True,
        "result": f"Alert logged: {message}",
        "status": "success" 
    }


def extract_compliance_topics_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key compliance topics from document content."""
    document_content = input_data.get("document_content", "")
    
    if not document_content:
        return {
            "success": False,
            "error": "Missing document content",
            "result": {
                "topics": [],
                "summary": "No document content provided"
            }
        }
    
    # This would typically use an LLM or other extraction method
    # For simplicity, we're just simulating the extraction
    logger.info("Extracting compliance topics from document")

    # Simulate extraction results based on document content
    topics = []
    if "data privacy" in document_content.lower():
        topics.append("Data Privacy")
    if "security" in document_content.lower():
        topics.append("Security Requirements")
    if "regulatory" in document_content.lower():
        topics.append("Regulatory Compliance")
    if "third-party" in document_content.lower():
        topics.append("Third-party Risk")
    
    # Add default topics if none were found
    if not topics:
        topics = ["Data Privacy", "Security Requirements", "Regulatory Compliance", "Third-party Risk"]

    return {
        "success": True,
        "result": {
            "topics": topics,
            "summary": "This document covers several compliance areas including data privacy and security."
        }
    }


def parse_json_output(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse JSON output from LLM task or structured data."""
    llm_output = input_data.get("llm_output", "{}")
    
    # If the input is already a dictionary with result field, extract and return it
    if isinstance(llm_output, dict) and "result" in llm_output:
        return {
            "success": True,
            "result": llm_output.get("result", {}),
            "error": None
        }
    
    # If the input is a dictionary with response field (LLM output), extract it
    if isinstance(llm_output, dict) and "response" in llm_output:
        llm_output = llm_output.get("response", "{}")
            
    # Handle string output
    if isinstance(llm_output, str):
        try:
            # Try to parse the JSON
            result = json.loads(llm_output)
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except json.JSONDecodeError as e:
            # If parsing fails, try to extract just the JSON part
            # Look for starting { and ending }
            start_idx = llm_output.find('{')
            end_idx = llm_output.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                # Extract what looks like JSON
                json_str = llm_output[start_idx:end_idx+1]
                try:
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "result": result,
                        "error": None
                    }
                except json.JSONDecodeError:
                    pass
            
            # If we still can't parse it, return default structure with error
            return {
                "success": False,
                "result": {
                    "topics": [],
                    "summary": "Failed to parse output"
                },
                "error": f"Failed to parse JSON: {str(e)}"
            }
    
    # If the input was neither a string nor a dict with expected fields
    return {
        "success": False,
        "result": {
            "topics": [],
            "summary": "Unexpected input format"
        },
        "error": "Input was not in expected format"
    }


def evaluate_compliance_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate compliance report and determine if action is needed."""
    topics = input_data.get("topics", [])
    document_content = input_data.get("document_content", "")
    
    logger.info(f"Evaluating compliance topics: {topics}")

    # Handle case where topics is not a list
    if not isinstance(topics, list):
        logger.warning(f"Topics not in expected format. Got: {type(topics)}")
        # Try to extract topics if it's a dictionary
        if isinstance(topics, dict) and "topics" in topics:
            topics = topics.get("topics", [])
        else:
            # Use empty list as fallback
            topics = []

    # Simulate evaluation logic
    high_risk_topics = ["Data Privacy", "Security Requirements"]
    risk_score = sum(1 for topic in topics if topic in high_risk_topics)

    action_needed = risk_score >= 1

    return {
        "success": True,
        "result": {
            "Action": "ACTION_REQUIRED" if action_needed else "NO_ACTION",
            "RiskScore": risk_score,
            "Explanation": (
                "High risk compliance topics detected." if action_needed else "No high risk compliance topics detected."
            )
        }
    }


def generate_compliance_report_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a compliance report based on extracted topics and evaluation."""
    topics = input_data.get("topics", [])
    evaluation_result = input_data.get("evaluation_result", {})
    document_content = input_data.get("document_content", "")
    
    # Handle case where topics is not a list
    if not isinstance(topics, list):
        logger.warning(f"Topics not in expected format. Got: {type(topics)}")
        # Try to extract topics if it's a dictionary
        if isinstance(topics, dict) and "topics" in topics:
            topics = topics.get("topics", [])
        else:
            # Use empty list as fallback
            topics = []
    
    # Extract evaluation details with fallbacks
    if isinstance(evaluation_result, dict):
        action = evaluation_result.get("Action", "NO_ACTION")
        risk_score = evaluation_result.get("RiskScore", 0)
        explanation = evaluation_result.get("Explanation", "No explanation provided")
    else:
        # Default values if evaluation_result is not a dictionary
        action = "NO_ACTION" 
        risk_score = 0
        explanation = "No evaluation data provided"

    logger.info("Generating compliance report")

    report_content = f"""
    COMPLIANCE ANALYSIS REPORT
    
    Topics Identified: {', '.join(topics) if topics else 'None identified'}
    Risk Assessment: {explanation}
    Risk Score: {risk_score}
    Action Required: {action == 'ACTION_REQUIRED'}
    
    Recommendations:
    1. Review the document sections related to {topics[0] if topics else 'compliance'}
    2. Update compliance documentation as needed
    3. Consider additional controls for high-risk areas
    """

    # Create a temporary file to store the report
    fd, report_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)

    try:
        with open(report_path, "w") as file:
            file.write(report_content)

        return {
            "success": True, 
            "result": {
                "report_path": report_path, 
                "summary": "Compliance report generated successfully.",
                "content": report_content
            }
        }
    except Exception as e:
        logger.error(f"Failed to write report: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to generate report: {str(e)}",
            "result": {
                "report_path": None,
                "summary": f"Error: {str(e)}",
                "content": report_content
            }
        }


def main():
    """Main function to set up and run the compliance workflow."""
    # Sample document content
    document_content = """
    This is a sample contract that includes provisions for data privacy,
    security requirements, and regulatory compliance. The document outlines
    procedures for handling customer data, security protocols, and ensuring
    compliance with relevant regulations.
    """  # noqa: D202

    # Create tool registry and register tools
    registry = ToolRegistry()

    # Register tools using direct tool registry access
    if "log_alert" not in list(registry.tools.keys()):
        registry.register_tool("log_alert", log_alert_handler)

    if "extract_compliance_topics" not in list(registry.tools.keys()):
        registry.register_tool("extract_compliance_topics", extract_compliance_topics_handler)

    if "evaluate_compliance_report" not in list(registry.tools.keys()):
        registry.register_tool("evaluate_compliance_report", evaluate_compliance_report_handler)

    if "generate_compliance_report" not in list(registry.tools.keys()):
        registry.register_tool("generate_compliance_report", generate_compliance_report_handler)

    # Create and configure the workflow
    workflow = Workflow(workflow_id="compliance_workflow", name="Simplified Compliance Workflow")

    # Task 1: Extract Compliance Topics
    task1 = DirectHandlerTask(
        task_id="extract_topics_task",
        name="Extract Compliance Topics",
        handler=extract_compliance_topics_handler,
        input_data={"document_content": document_content},
        next_task_id_on_success="parse_topics_task",
    )
    workflow.add_task(task1)
    
    # Task 2: Parse Topics Output
    task2 = DirectHandlerTask(
        task_id="parse_topics_task",
        name="Parse Topics Output",
        handler=parse_json_output,
        input_data={"llm_output": "${extract_topics_task.output_data}"},
        next_task_id_on_success="evaluate_compliance_task",
    )
    workflow.add_task(task2)

    # Task 3: Evaluate Compliance Report
    task3 = DirectHandlerTask(
        task_id="evaluate_compliance_task",
        name="Evaluate Compliance Report",
        handler=evaluate_compliance_report_handler,
        input_data={
            "topics": "${parse_topics_task.output_data.result.topics | []}",
            "document_content": document_content,
        },
        next_task_id_on_success="parse_evaluation_task",
    )
    workflow.add_task(task3)
    
    # Task 4: Parse Evaluation Output
    task4 = DirectHandlerTask(
        task_id="parse_evaluation_task",
        name="Parse Evaluation Output",
        handler=parse_json_output,
        input_data={"llm_output": "${evaluate_compliance_task.output_data}"},
        next_task_id_on_success="generate_report_task",
    )
    workflow.add_task(task4)

    # Task 5: Generate Compliance Report
    task5 = DirectHandlerTask(
        task_id="generate_report_task",
        name="Generate Compliance Report",
        handler=generate_compliance_report_handler,
        input_data={
            "topics": "${parse_topics_task.output_data.result.topics | []}",
            "evaluation_result": "${parse_evaluation_task.output_data.result | {}}",
            "document_content": document_content,
        },
        next_task_id_on_success="log_alert_task",
    )
    workflow.add_task(task5)

    # Task 6: Log Alert (if needed)
    task6 = DirectHandlerTask(
        task_id="log_alert_task",
        name="Log Compliance Alert",
        handler=log_alert_handler,
        input_data={
            "message": "Compliance alert: Action required for document with risk score ${parse_evaluation_task.output_data.result.RiskScore | 0}",
            "level": "CRITICAL",
        },
        condition="output_data.get('result', {}).get('Action', 'NO_ACTION') == 'ACTION_REQUIRED'",
        next_task_id_on_success=None,  # End workflow
    )
    workflow.add_task(task6)

    # Create agent with workflow
    agent = Agent(agent_id="compliance_agent", name="Compliance Analysis Agent")
    
    # Check for DirectHandlerTask dependencies attribute issues
    for task_id, task in workflow.tasks.items():
        if hasattr(task, 'is_direct_handler') and task.is_direct_handler:
            # Verify no 'dependencies' attribute is mistakenly set
            if hasattr(task, 'dependencies'):
                logger.warning(f"Task {task_id} is a DirectHandlerTask but has a 'dependencies' attribute. This is unsupported and will be removed.")
                # Remove the dependencies attribute to prevent errors
                delattr(task, 'dependencies')
    
    agent.load_workflow(workflow)

    # Run the agent
    logger.info("Running simplified compliance workflow...")
    result = agent.run()

    # Display results
    if result:
        logger.info("Workflow completed successfully")
        
        # Get task history
        history = get_task_history(workflow)
        logger.info("Task execution summary:")
        for task_data in history:
            task_id = task_data["task_id"]
            status = task_data["status"]
            task = workflow.tasks.get(task_id)
            task_name = task.name if task else task_id
            logger.info(f"  - {task_name} ({task_id}): {status}")
            
            if status == "completed":
                # Use extract_task_output for consistent data access
                output = extract_task_output(task_data["output_data"])
                if output:
                    if isinstance(output, dict):
                        # Truncate dictionary representation
                        logger.info(f"    Output: {str(output)[:100]}...")
                    else:
                        # Truncate string representation
                        logger.info(f"    Output: {str(output)[:100]}...")
        
        # Display final report
        report_task = workflow.tasks.get("generate_report_task")
        if report_task and report_task.status == "completed":
            report_data = extract_task_output(report_task.output_data, "result")
            if report_data and "content" in report_data:
                logger.info("\nFinal Report:")
                logger.info(report_data["content"])
            elif report_data and "report_path" in report_data:
                try:
                    with open(report_data["report_path"], "r") as f:
                        logger.info("\nFinal Report:")
                        logger.info(f.read())
                except Exception as e:
                    logger.error(f"Failed to read report file: {e}")
    else:
        logger.error("Workflow failed")
        
        # Find failed tasks
        failed_tasks = []
        for task_id, task in workflow.tasks.items():
            if task.status == "failed":
                failed_tasks.append(task_id)
                # Get error information
                if hasattr(task, "output_data") and task.output_data:
                    error_msg = task.output_data.get("error", "Unknown error")
                    logger.error(f"Task {task_id} failed with error: {error_msg}")
        
        if failed_tasks:
            logger.error(f"Failed tasks: {', '.join(failed_tasks)}")
        else:
            logger.error("No specific tasks marked as failed, but workflow did not complete successfully")


if __name__ == "__main__":
    main()
