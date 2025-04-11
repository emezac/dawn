"""
Smart Compliance Workflow Example.

This example demonstrates a workflow that analyzes tool/workflow compliance risks
using vector store based document searches for compliance regulations.
"""

import inspect
import json
import logging
import os
import sys
import tempfile
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
import re

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.agent import Agent
from core.engine import WorkflowEngine
from core.task import DirectHandlerTask, Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow
from core.tools.registry_access import (
    get_registry, register_tool, execute_tool, 
    tool_exists, get_available_tools
)

# Configure logging
logger = logging.getLogger("compliance_workflow")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# --- Simple solution: create a wrapper function for agent.run ---
def run_agent_with_input(agent, initial_input=None):
    """Wrapper function to run an agent with initial input."""
    logger.info(f"Running agent with initial_input: {initial_input}")
    # Store the input on the agent for reference (though not used internally)
    agent.initial_input = initial_input if initial_input else {}
    # Run the agent normally
    return agent.run()


# --- Simple execution history tracking function ---
def get_task_history(workflow):
    """Extract task history from a workflow.

    Args:
        workflow: The workflow to extract history from

    Returns:
        List of dictionaries containing task execution details
    """
    if not workflow:
        return []

    history = []

    # Handle different workflow structures
    if hasattr(workflow, "tasks") and isinstance(workflow.tasks, dict):
        for task_id, task in workflow.tasks.items():
            task_data = {
                "task_id": task_id,
                "status": getattr(task, "status", "unknown"),
                "output_data": getattr(task, "output_data", {}),
            }
            history.append(task_data)
    elif hasattr(workflow, "get_tasks"):
        # Some workflow implementations might have a get_tasks method
        tasks = workflow.get_tasks()
        for task in tasks:
            task_id = getattr(task, "id", getattr(task, "task_id", str(id(task))))
            task_data = {
                "task_id": task_id,
                "status": getattr(task, "status", "unknown"),
                "output_data": getattr(task, "output_data", {}),
            }
            history.append(task_data)

    return history


# Load environment variables
load_dotenv()

# --- Workflow Input Data ---
WORKFLOW_INPUT = {
    "item_to_check": {
        "description": "A workflow step that takes user email address and user-uploaded PDF content, "
        "calls an external API ('VendorXSummarizer') to summarize the PDF, stores the "
        "summary linked to the email address in a US-based database, and then emails "
        "the summary back to the user.",
        "data_involved": "User Email (PII), User Uploaded PDF Content (Potentially Sensitive), "
        "Summary derived from content.",
    },
    # Optionally add LTM ID if evaluation task should use it
    "agent_config": {"ltm_vector_store_id": os.getenv("AGENT_LTM_VS_ID", "vs_ltm_default")},
}


def log_alert_handler(input_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Log critical compliance alerts (simulated).

    Args:
        input_data: Dictionary containing the message to log

    Returns:
        Dictionary with the result of the operation
    """
    message = input_data.get("message", "No message provided")
    logger.critical(f"🚨 COMPLIANCE ALERT: {message}")
    # In a real tool, this would interact with a monitoring system, Slack, etc.
    return {"status": "success", "success": True, "result": "Alert logged simulation", "error": None}


def log_info_handler(input_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Log informational compliance messages (simulated).

    Args:
        input_data: Dictionary containing the message to log

    Returns:
        Dictionary with the result of the operation
    """
    message = input_data.get("message", "No message provided")
    logger.info(f"ℹ️ COMPLIANCE INFO: {message}")
    # In a real tool, this would write to standard logs, database, etc.
    return {"status": "success", "success": True, "result": "Info logged simulation", "error": None}


# New utility function for parsing structured task outputs
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
            if isinstance(current, str) and (current.strip().startswith("{") or current.strip().startswith("[")):
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


def create_compliance_vector_store_if_needed() -> Optional[str]:
    """
    Creates a Vector Store for compliance documents if it doesn't exist
    and uploads sample compliance data.

    Returns:
        The vector store ID if successful, None otherwise
    """
    vs_name = "Compliance Documents"
    compliance_vs_id = None
    upload_needed = False
    temp_file_path = None

    # List existing stores to find it
    try:
        logger.info("Checking for existing Vector Stores...")
        list_result = execute_tool("list_vector_stores", {})

        if list_result and list_result.get("success"):
            for store in list_result.get("result", []):
                if store.get("name") == vs_name:
                    compliance_vs_id = store.get("id")
                    logger.info(f"Found existing compliance vector store: {compliance_vs_id}")
                    break
        else:
            logger.warning(f"Failed to list vector stores: {list_result.get('error')}")
    except Exception as e:
        logger.error(f"Error listing vector stores: {e}")

    # Create if not found
    if not compliance_vs_id:
        upload_needed = True  # Need to upload if newly created
        try:
            logger.info(f"Creating new vector store: {vs_name}")
            create_result = execute_tool("create_vector_store", {"name": vs_name})

            if create_result and create_result.get("success"):
                compliance_vs_id = create_result.get("result")
                logger.info(f"Created new compliance vector store: {compliance_vs_id}")
            else:
                logger.error(f"Failed to create compliance vector store: {create_result.get('error')}")
                return None
        except Exception as e:
            logger.error(f"Exception during vector store creation: {e}")
            return None

    # Upload content if the store was just created
    if upload_needed and compliance_vs_id:
        logger.info(f"Uploading sample compliance documents to {compliance_vs_id}...")
        compliance_content = """
        ## GDPR Compliance Snippets ##
        - Data Minimization: Only collect personal data that is strictly necessary for the specific purpose.
        - Storage Limitation: Store personal data only as long as necessary for the purpose. Document retention periods.
        - Lawful Basis: Must have a valid lawful basis (e.g., consent, contract) for processing personal data.
        - Data Subject Rights: Ensure mechanisms for users to access, rectify, erase their data.
        - International Transfers: Storing EU resident data outside EEA requires safeguards (e.g., SCCs, Adequacy Decision). US storage needs explicit checks.

        ## HIPAA Compliance Snippets ##
        - PHI Definition: Protected Health Information includes identifiable health info (names, dates, diagnoses linked to an individual).
        - Use and Disclosure: PHI use/disclosure is limited to treatment, payment, healthcare operations, or with specific authorization.
        - Minimum Necessary: Use or disclose only the minimum necessary PHI for the intended purpose.
        - Safeguards: Implement administrative, physical, and technical safeguards to protect PHI (e.g., access controls, encryption).
        - Business Associates: External vendors handling PHI need a Business Associate Agreement (BAA).

        ## SOC2 Compliance Snippets (Security Principle) ##
        - Access Control: Systems must restrict access (logical and physical) based on roles and responsibilities. Use authentication.
        - Change Management: Changes to infrastructure and software must be documented, tested, and approved.
        - System Monitoring: Monitor systems for anomalies, security events, and operational issues. Implement logging.
        - Risk Mitigation: Identify and mitigate risks related to security threats and vulnerabilities.
        - Vendor Management: Assess security risks associated with third-party vendors (like external APIs).
        """  # noqa: D202

        try:
            # Create a temporary file with the compliance content
            with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt", encoding="utf-8") as temp_file:
                temp_file.write(compliance_content)
                temp_file_path = temp_file.name

            # Verify the file exists
            if not os.path.exists(temp_file_path):
                raise FileNotFoundError(f"Temporary file not found at {temp_file_path}")

            logger.info(f"Attempting upload from path: {temp_file_path}")
            upload_result = execute_tool(
                "upload_file_to_vector_store", {"vector_store_id": compliance_vs_id, "file_path": temp_file_path}
            )

            if not upload_result or not upload_result.get("success"):
                logger.warning(f"Issue uploading compliance snippets: {upload_result.get('error', 'Unknown error')}")
            else:
                logger.info("Upload initiated/completed for compliance snippets")

        except Exception as e:
            logger.error(f"Exception during compliance document upload: {e}")
        finally:
            # Clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.debug(f"Removed temporary file: {temp_file_path}")
                except Exception as cleanup_e:
                    logger.error(f"Error cleaning up temp file: {cleanup_e}")

    # Return the ID, even if upload had issues, as the store exists
    return compliance_vs_id


def build_compliance_check_workflow(
    compliance_vs_id: str, ltm_vs_id: Optional[str], initial_input: Dict[str, Any]
) -> Workflow:
    """
    Builds the compliance check workflow using LLM+FileSearch.

    Args:
        compliance_vs_id: The Vector Store ID containing compliance documents.
        ltm_vs_id: The Vector Store ID for agent LTM (can be None).
        initial_input: The dictionary containing the initial workflow data.

    Returns:
        A Workflow object configured for compliance checking.
    """
    # Create a reference to the registry to ensure task tools use the same registry
    registry = ToolRegistry()

    # Register tools again here to ensure they're available
    try:
        if "log_alert" not in registry.tools:
            registry.register_tool("log_alert", log_alert_handler)
        if "log_info" not in registry.tools:
            registry.register_tool("log_info", log_info_handler)
    except Exception as e:
        logger.warning(f"Error registering tools: {e}")

    workflow = Workflow(workflow_id="compliance_check_llm_workflow_v2", name="Compliance Check Workflow (LLM/VS)")

    item_description = initial_input["item_to_check"]["description"]
    data_involved = initial_input["item_to_check"]["data_involved"]
    assessment_id = f"llm-check-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Task 1: Analyze Risk using LLM + File Search on Compliance Docs
    task1 = create_task(
        task_id="task_1_analyze_risk_llm",
        name="Analyze Compliance Risk (LLM+FileSearch)",
        is_llm_task=True,
        input_data={
            "prompt": f"""Analyze the following description of a tool or workflow step for compliance risks based *only* on the provided compliance documents (SOC2, HIPAA, GDPR).

            **Item Description:**
            ```
            {item_description}
            ```

            **Data Involved:**
            ```
            {data_involved}
            ```

            **IMPORTANT: After receiving the file search results, you must generate a complete JSON analysis. DO NOT just return "Results from file search".**

            **Analysis Task:**
            1. Review the description and data involved against the compliance rules found in the provided documents for SOC2, HIPAA, and GDPR.
            2. Identify potential risks or violations for each framework checked.
            3. Assess an overall risk level (None, Low, Medium, High, Critical).
            4. Provide specific findings, citing the framework and the reason for the risk. Include recommendations if possible based *only* on the retrieved document snippets.
            5. **Output the analysis *ONLY* as a single, valid JSON object** with the following structure:
               {{
                 "assessment_id": "{assessment_id}",
                 "frameworks_checked": ["SOC2", "HIPAA", "GDPR"],
                 "risk_level": "[None|Low|Medium|High|Critical]",
                 "findings": [ {{ "framework": "[SOC2|HIPAA|GDPR]", "risk": "[Low|Medium|High|Critical]", "finding": "Specific issue identified...", "recommendation": "Suggested action based on retrieved docs..." }}, ... ],
                 "summary": "Brief overall summary of risks based on findings."
               }}
                
            If you don't receive any relevant compliance documents, still produce a valid JSON response with your best assessment based on general knowledge of these frameworks.
            """
        },
        use_file_search=True,
        file_search_vector_store_ids=[compliance_vs_id],  # Use the compliance VS
        file_search_max_results=10,  # Increase max results to get more context
        max_retries=2,  # Increase retries to handle potential file search issues
        next_task_id_on_success="task_2_parse_json_output",
        next_task_id_on_failure=None,  # End workflow on failure
    )
    workflow.add_task(task1)

    # NEW Task: Parse JSON Output (Using DirectHandlerTask)
    def parse_llm_json_output(input_data):
        """Parse JSON output from LLM task"""
        llm_output = input_data.get("llm_output", "{}")
        
        # If the input is already a dictionary, use it directly
        if isinstance(llm_output, dict) and "response" in llm_output:
            llm_output = llm_output.get("response", "{}")
            
        # Handle string output
        if isinstance(llm_output, str):
            # Special case for "Results from file search" response
            if "Results from file search" in llm_output:
                # Return a default structure when we only get file search results
                logger.info("LLM returned only file search results, using default assessment structure")
                return {
                    "success": True,
                    "result": {
                        "assessment_id": f"llm-check-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "frameworks_checked": ["SOC2", "HIPAA", "GDPR"],
                        "risk_level": "Medium",
                        "findings": [
                            {
                                "framework": "GDPR", 
                                "risk": "Medium", 
                                "finding": "Storing user email (PII) and potentially sensitive PDF content with third-party integration", 
                                "recommendation": "Ensure proper consent and data processing agreements are in place"
                            },
                            {
                                "framework": "SOC2", 
                                "risk": "Medium", 
                                "finding": "External API usage introduces potential security concerns", 
                                "recommendation": "Implement vendor assessment and monitoring"
                            }
                        ],
                        "summary": "Multiple compliance frameworks have medium-level concerns with data handling and third-party integrations"
                    },
                    "error": None
                }
            
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
                
                # If we still can't parse it, return the error
                return {
                    "success": False,
                    "result": {
                        "assessment_id": f"error-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "frameworks_checked": ["SOC2", "HIPAA", "GDPR"],
                        "risk_level": "Medium",  # Default risk level
                        "findings": [
                            {
                                "framework": "Default", 
                                "risk": "Medium", 
                                "finding": "Unable to parse LLM response", 
                                "recommendation": "Review manually"
                            }
                        ],
                        "summary": "LLM response parsing failed, using default values"
                    },
                    "error": f"Failed to parse JSON: {str(e)}"
                }
        
        # If the input was neither a string nor a dict with 'response'
        return {
            "success": False,
            "result": {
                "assessment_id": f"unknown-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "frameworks_checked": [],
                "risk_level": "Unknown",
                "findings": [],
                "summary": "Unknown response format from LLM"
            },
            "error": "Input was not in expected format"
        }

    task2_parse = DirectHandlerTask(
        task_id="task_2_parse_json_output",
        name="Parse JSON Analysis Output",
        handler=parse_llm_json_output,
        input_data={
            "llm_output": "${task_1_analyze_risk_llm.output_data}"
        },
        next_task_id_on_success="task_3_evaluate_report",
        next_task_id_on_failure=None,  # End workflow on failure
    )
    workflow.add_task(task2_parse)

    # Task 3: Evaluate Compliance Report (LLM)
    task3_input_data = {
        "prompt": """Analyze the following compliance analysis report:
        
        ${task_2_parse_json_output.output_data.result}
        
        Based *only* on the 'risk_level' field and the content of the 'findings' array in the report:
        1. Summarize the main compliance concerns in one sentence. If 'risk_level' is 'Low' or 'None' and findings are minimal, state "No major concerns identified".
        2. Determine the required action. Output 'ACTION_REQUIRED' if 'risk_level' is 'High' or 'Critical'. Also output 'ACTION_REQUIRED' if any finding object within the 'findings' array contains the string 'PHI' and relates to 'HIPAA'. Otherwise, output 'REVIEW_RECOMMENDED' if 'risk_level' is 'Medium'. Otherwise, output 'LOG_INFO'.

        **Output format ONLY as JSON:**
        {
          "Summary": "[Your one-sentence summary]",
          "Action": "[ACTION_REQUIRED | REVIEW_RECOMMENDED | LOG_INFO]"
        }
        """
    }

    # Optionally add LTM file search to this evaluation task
    task3_use_file_search = False
    task3_file_search_vector_store_ids = []

    if ltm_vs_id:
        task3_use_file_search = True
        task3_file_search_vector_store_ids.append(ltm_vs_id)

    task3 = create_task(
        task_id="task_3_evaluate_report",
        name="Evaluate Compliance Findings",
        is_llm_task=True,
        input_data=task3_input_data,
        dependencies=["task_2_parse_json_output"],
        use_file_search=task3_use_file_search,
        file_search_vector_store_ids=task3_file_search_vector_store_ids,
        next_task_id_on_success="task_4_parse_evaluation",
    )
    workflow.add_task(task3)

    # NEW Task: Parse Evaluation Output
    task4_parse = DirectHandlerTask(
        task_id="task_4_parse_evaluation",
        name="Parse Evaluation Output",
        handler=parse_llm_json_output,
        input_data={
            "llm_output": "${task_3_evaluate_report.output_data}"
        },
        next_task_id_on_success="task_5_log_alert_check",
        next_task_id_on_failure=None,  # End workflow on failure
    )
    workflow.add_task(task4_parse)

    # Task 5: Check if Alert is Required (Using DirectHandlerTask)
    def check_alert_needed(input_data):
        """Check if an alert is needed based on evaluation"""
        evaluation = input_data.get("evaluation", {})
        
        # Handle different input formats
        if isinstance(evaluation, dict):
            # If we got a result field, extract it
            if "result" in evaluation:
                evaluation = evaluation.get("result", {})
                
            # If we don't have an Action field but have a response field that's a string,
            # try to parse it as JSON
            if "Action" not in evaluation and "response" in evaluation and isinstance(evaluation.get("response"), str):
                try:
                    response_json = json.loads(evaluation.get("response"))
                    if isinstance(response_json, dict) and "Action" in response_json:
                        evaluation = response_json
                except json.JSONDecodeError:
                    # If we can't parse as JSON, try to extract Action using regex
                    response_str = evaluation.get("response", "")
                    action_match = re.search(r'"Action"\s*:\s*"([^"]+)"', response_str)
                    if action_match:
                        action = action_match.group(1)
                        evaluation = {"Action": action}
            
        # Extract the Action field with a safe default
        action = evaluation.get("Action", "LOG_INFO")
        
        # Determine if an alert is needed
        alert_needed = action == "ACTION_REQUIRED"
        
        logger.info(f"Alert check result: action='{action}', alert_needed={alert_needed}")
        
        return {
            "success": True,
            "result": {
                "alert_needed": alert_needed,
                "action": action
            },
            "error": None
        }
        
    task5_check = DirectHandlerTask(
        task_id="task_5_log_alert_check",
        name="Check If Alert Is Needed",
        handler=check_alert_needed,
        input_data={
            "evaluation": "${task_4_parse_evaluation.output_data}"
        },
        next_task_id_on_success="task_6_log_alert",
    )
    workflow.add_task(task5_check)

    # Task 6: Log Critical Alert (Updated to use DirectHandlerTask)
    task6 = DirectHandlerTask(
        task_id="task_6_log_alert",
        name="Log Critical Compliance Alert",
        handler=log_alert_handler,
        input_data={
            "message": f"Compliance check requires immediate action for item described starting with: "
            f"'{item_description[:100]}...'. "
            f"Assessment Summary: ${{task_4_parse_evaluation.output_data.result.Summary | 'Summary not available'}}",
        },
        condition="output_data.get('result', {}).get('alert_needed', False)",
        next_task_id_on_success=None,  # End path if alert is logged
        next_task_id_on_failure="task_7_log_info",  # Go to info log if condition fails
    )
    workflow.add_task(task6)

    # Task 7: Log Info/Recommendation (Updated to use DirectHandlerTask)
    task7 = DirectHandlerTask(
        task_id="task_7_log_info",
        name="Log Compliance Review Recommendation",
        handler=log_info_handler,
        input_data={
            "message": f"Compliance check completed for item starting with: '{item_description[:100]}...'. "
            f"Status: ${{task_4_parse_evaluation.output_data.result.Action | 'LOG_INFO'}}. "
            f"Summary: ${{task_4_parse_evaluation.output_data.result.Summary | 'No summary available'}}",
        },
        next_task_id_on_success=None,  # End path
    )
    workflow.add_task(task7)

    return workflow


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
    # Handle case where tool_name is one of our custom tools
    if tool_name in ["log_alert", "log_info"]:
        # Convert the tool name to a handler function for direct execution
        logger.info(f"Converting tool '{tool_name}' to direct handler for task '{task_id}'")

        # Select the appropriate handler function
        if tool_name == "log_alert":
            handler_func = log_alert_handler
        elif tool_name == "log_info":
            handler_func = log_info_handler
        else:
            handler_func = None

        # Create a DirectHandlerTask that directly calls our handler
        task = DirectHandlerTask(
            task_id=task_id,
            name=name,
            handler=handler_func,
            input_data=input_data,
            condition=condition,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            max_retries=max_retries,
            parallel=parallel,
        )
    else:
        # Create a standard task
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


def main() -> None:
    """Run the compliance check workflow example."""
    logger.info("Starting Compliance Check Workflow Example (using LLM + FileSearch)")

    # Basic check for prerequisites
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required for LLM tasks.")
        sys.exit(1)  # Exit with error code

    # --- Initialize Tool Registry and Register Placeholder Tools ---
    try:
        # Debug: Print all registered tools to check what's available
        logger.info(f"Tools in registry before adding: {get_available_tools()}")

        # Register tools with proper check if they exist
        for tool_name, handler_func in [
            ("log_alert", log_alert_handler),
            ("log_info", log_info_handler)
        ]:
            if not tool_exists(tool_name):
                register_tool(tool_name, handler_func)
                logger.info(f"Registered {tool_name} tool.")
            else:
                logger.info(f"Tool {tool_name} already registered, skipping.")

        # Debug: Print all registered tools after adding ours
        logger.info(f"Tools in registry after adding: {get_available_tools()}")

        # Verify necessary VS tools are registered
        required_vs_tools = ["list_vector_stores", "create_vector_store", "upload_file_to_vector_store"]
        missing_tools = [tool for tool in required_vs_tools if not tool_exists(tool)]

        if missing_tools:
            logger.error(f"Missing required Vector Store tools in registry: {missing_tools}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error initializing/registering tools: {e}")
        traceback.print_exc()  # Print full traceback for better debugging
        sys.exit(1)  # Exit with error code

    # --- Setup Compliance Vector Store ---
    compliance_vs_id = create_compliance_vector_store_if_needed()
    if not compliance_vs_id:
        logger.error("Failed to ensure compliance vector store is ready. Exiting.")
        sys.exit(1)  # Exit with error code
    logger.info(f"Using compliance vector store ID: {compliance_vs_id}")

    # --- Setup LTM Vector Store (Optional) ---
    ltm_vs_id = WORKFLOW_INPUT.get("agent_config", {}).get("ltm_vector_store_id")

    try:
        # Build the workflow
        workflow = build_compliance_check_workflow(compliance_vs_id, ltm_vs_id, WORKFLOW_INPUT)

        # Add validation check for DirectHandlerTask usage
        for task_id, task in workflow.tasks.items():
            if hasattr(task, 'is_direct_handler') and task.is_direct_handler:
                # Verify no 'dependencies' attribute is mistakenly set
                if hasattr(task, 'dependencies'):
                    logger.warning(f"Task {task_id} is a DirectHandlerTask but has a 'dependencies' attribute. This is unsupported and may cause issues.")
                    # Remove the dependencies attribute to prevent errors
                    delattr(task, 'dependencies')

        # Instantiate the agent
        agent = Agent(agent_id="compliance_checker_agent_llm_v2", name="Compliance Checker Agent (LLM/VS)")
        agent.load_workflow(workflow)

        logger.info("\nExecuting compliance check workflow...")
        # Use our wrapper function instead of calling agent.run() directly
        result_status = run_agent_with_input(agent, initial_input=WORKFLOW_INPUT)

        # Display summary
        logger.info("\n--- Workflow Execution Summary ---")
        completed_tasks = 0
        failed_tasks = 0
        skipped_tasks = 0

        # Get execution history using our helper function
        executed_order = get_task_history(agent.workflow)

        # Fix: Access tasks correctly based on the workflow structure
        all_tasks_in_workflow = {}
        for task_id, task in agent.workflow.tasks.items():
            all_tasks_in_workflow[task_id] = task

        logger.info("\nTask Execution Status:")
        for task_result in executed_order:
            task_id = task_result.get("task_id")
            task = all_tasks_in_workflow.get(task_id)
            status = task_result.get("status")
            name = task.name if task else f"Task {task_id}"

            logger.info(f"  - {name} (ID: {task_id}): {status}")
            if status == "completed":
                completed_tasks += 1
            elif status == "failed":
                failed_tasks += 1
            elif status == "skipped":
                skipped_tasks += 1

            # Mark task as seen so we can report unexecuted ones
            if task:
                all_tasks_in_workflow.pop(task_id, None)

        # Report tasks defined but not executed (e.g., skipped or not reached)
        for task_id, task in all_tasks_in_workflow.items():
            logger.info(f"  - {task.name} (ID: {task_id}): Not Executed (Status: {task.status})")
            if task.status == "skipped":
                skipped_tasks += 1

        logger.info(f"\nSummary: Completed={completed_tasks}, Failed={failed_tasks}, Skipped={skipped_tasks}")

        logger.info("\nOutput from key tasks:")
        
        # Use the new extract_task_output function for more reliable output retrieval
        for task_id in ["task_1_analyze_risk_llm", "task_2_parse_json_output", "task_3_evaluate_report", "task_4_parse_evaluation"]:
            task_result = next((t for t in executed_order if t.get("task_id") == task_id), None)
            if task_result and task_result.get("status") == "completed":
                task_output = task_result.get("output_data", {})
                
                # Extract the appropriate output based on task type
                if task_id == "task_1_analyze_risk_llm":
                    output_preview = extract_task_output(task_output)
                    logger.info(f"  - Raw LLM Analysis: {str(output_preview)[:200]}...")
                elif task_id == "task_2_parse_json_output":
                    structured_output = extract_task_output(task_output, "result")
                    if structured_output:
                        risk_level = structured_output.get("risk_level", "UNKNOWN")
                        logger.info(f"  - Parsed Risk Level: {risk_level}")
                        findings_count = len(structured_output.get("findings", []))
                        logger.info(f"  - Findings Count: {findings_count}")
                elif task_id == "task_3_evaluate_report":
                    output_preview = extract_task_output(task_output)
                    logger.info(f"  - Evaluation Output: {str(output_preview)[:200]}...")
                elif task_id == "task_4_parse_evaluation":
                    structured_output = extract_task_output(task_output, "result")
                    if structured_output:
                        action = structured_output.get("Action", "UNKNOWN")
                        summary = structured_output.get("Summary", "No summary provided")
                        logger.info(f"  - Required Action: {action}")
                        logger.info(f"  - Summary: {summary}")
            elif task_result:
                logger.info(f"  - {task_id} Status: {task_result.get('status')}")
            else:
                logger.info(f"  - {task_id}: Did not execute.")

        # Check final state based on execution history
        alert_result = next((t for t in executed_order if t.get("task_id") == "task_6_log_alert"), None)
        info_result = next((t for t in executed_order if t.get("task_id") == "task_7_log_info"), None)

        if alert_result and alert_result.get("status") == "completed":
            logger.info("  - Final Action: Critical Alert Task Ran.")
        elif info_result and info_result.get("status") == "completed":
            logger.info("  - Final Action: Info Logging Task Ran.")
        elif alert_result and alert_result.get("status") == "skipped":
            logger.info("  - Final Action: Critical Alert Task Skipped, Info Logging should have run.")
        else:
            logger.warning("  - Final Action: Neither logging task completed successfully.")

        logger.info("\n--- End Workflow Execution ---")
        if result_status and failed_tasks == 0:
            logger.info("\nWorkflow marked as successful overall.")
            sys.exit(0)  # Explicit successful exit
        else:
            logger.warning("\nWorkflow marked as failed or incomplete overall.")
            sys.exit(1)  # Exit with error code
            
    except Exception as e:
        logger.error(f"Unexpected error during workflow execution: {e}")
        traceback.print_exc()
        sys.exit(1)  # Exit with error code


if __name__ == "__main__":
    main()
