#!/usr/bin/env python
"""
Simplified Compliance Workflow Example

This example demonstrates a compliance document analysis workflow
using wrapper functions for framework compatibility.
"""

import logging
import os
import tempfile
from typing import Any, Dict, List, Optional

from core.agent import Agent
from core.task import Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
def log_alert_handler(message: str, level: str = "INFO") -> Dict[str, Any]:
    """Log an alert message at the specified level."""
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = log_levels.get(level.upper(), logging.INFO)
    logger.log(log_level, f"ALERT: {message}")
    return {"status": "success", "message": f"Alert logged: {message}"}


def extract_compliance_topics_handler(document_content: str) -> Dict[str, Any]:
    """Extract key compliance topics from document content."""
    # This would typically use an LLM or other extraction method
    # For simplicity, we're just simulating the extraction
    logger.info("Extracting compliance topics from document")

    # Simulate extraction results
    topics = ["Data Privacy", "Security Requirements", "Regulatory Compliance", "Third-party Risk"]

    return {
        "status": "success",
        "topics": topics,
        "summary": "This document covers several compliance areas including data privacy and security.",
    }


def evaluate_compliance_report_handler(topics: List[str], document_content: str) -> Dict[str, Any]:
    """Evaluate compliance report and determine if action is needed."""
    logger.info(f"Evaluating compliance topics: {topics}")

    # Simulate evaluation logic
    high_risk_topics = ["Data Privacy", "Security Requirements"]
    risk_score = sum(1 for topic in topics if topic in high_risk_topics)

    action_needed = risk_score >= 1

    return {
        "status": "success",
        "Action": "ACTION_REQUIRED" if action_needed else "NO_ACTION",
        "RiskScore": risk_score,
        "Explanation": (
            "High risk compliance topics detected." if action_needed else "No high risk compliance topics detected."
        ),
    }


def generate_compliance_report_handler(
    topics: List[str], evaluation_result: Dict[str, Any], document_content: str
) -> Dict[str, Any]:
    """Generate a compliance report based on extracted topics and evaluation."""
    logger.info("Generating compliance report")

    report_content = f"""
    COMPLIANCE ANALYSIS REPORT
    
    Topics Identified: {', '.join(topics)}
    Risk Assessment: {evaluation_result['Explanation']}
    Risk Score: {evaluation_result['RiskScore']}
    Action Required: {evaluation_result['Action'] == 'ACTION_REQUIRED'}
    
    Recommendations:
    1. Review the document sections related to {topics[0]}
    2. Update compliance documentation as needed
    3. Consider additional controls for high-risk areas
    """

    # Create a temporary file to store the report
    fd, report_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)

    try:
        with open(report_path, "w") as file:
            file.write(report_content)

        return {"status": "success", "report_path": report_path, "summary": "Compliance report generated successfully."}
    except Exception as e:
        logger.error(f"Failed to write report: {str(e)}")
        return {"status": "error", "error": f"Failed to generate report: {str(e)}"}


def main():
    """Main function to set up and run the compliance workflow."""
    # Sample document content
    document_content = """
    This is a sample contract that includes provisions for data privacy,
    security requirements, and regulatory compliance. The document outlines
    procedures for handling customer data, security protocols, and ensuring
    compliance with relevant regulations.
    """

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

    # Create workflow
    workflow = Workflow(registry=registry)

    # Task 1: Extract compliance topics
    task_1 = create_task(
        task_id="task_1_extract_topics",
        name="Extract Contract Topics",
        is_llm_task=False,
        tool_name="extract_compliance_topics",
        input_data={"document_content": document_content},
        next_task_id_on_success="task_2_evaluate_report",
    )
    workflow.add_task(task_1)

    # Task 2: Evaluate compliance report
    task_2 = create_task(
        task_id="task_2_evaluate_report",
        name="Evaluate Compliance",
        is_llm_task=False,
        tool_name="evaluate_compliance_report",
        input_data={"topics": "${task_1_extract_topics.output_data[topics]}", "document_content": document_content},
        next_task_id_on_success="task_3_generate_report",
        dependencies=["task_1_extract_topics"],
    )
    workflow.add_task(task_2)

    # Create string condition instead of dictionary
    condition_str = "output_data.get('Action') == 'ACTION_REQUIRED'"

    # Task 3: Generate compliance report
    task_3 = create_task(
        task_id="task_3_generate_report",
        name="Generate Compliance Report",
        is_llm_task=False,
        tool_name="generate_compliance_report",
        input_data={
            "topics": "${task_1_extract_topics.output_data[topics]}",
            "evaluation_result": "${task_2_evaluate_report.output_data}",
            "document_content": document_content,
        },
        next_task_id_on_success="task_4_log_result",
        condition=condition_str,
        dependencies=["task_1_extract_topics", "task_2_evaluate_report"],
    )
    workflow.add_task(task_3)

    # Task 4: Log result
    task_4 = create_task(
        task_id="task_4_log_result",
        name="Log Compliance Result",
        is_llm_task=False,
        tool_name="log_alert",
        input_data={
            "message": "Compliance report generated: ${task_3_generate_report.output_data[report_path]}",
            "level": "INFO",
        },
        dependencies=["task_3_generate_report"],
    )
    workflow.add_task(task_4)

    # Create agent
    agent = Agent(workflow=workflow)

    # Run agent with initial input
    result = run_agent_with_input(agent, {"document_id": "DOC123"})

    # Get execution history
    history = get_task_history(workflow)
    logger.info(f"Workflow execution history: {history}")

    # Clean up any temporary files
    for task_id, task in workflow.tasks.items():
        if task.output_data and isinstance(task.output_data, dict) and "report_path" in task.output_data:
            report_path = task.output_data["report_path"]
            try:
                if os.path.exists(report_path):
                    os.unlink(report_path)
                    logger.info(f"Deleted temporary file: {report_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {report_path}: {e}")

    return result


if __name__ == "__main__":
    main()
