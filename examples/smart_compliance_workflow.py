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

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.agent import Agent
from core.engine import WorkflowEngine
from core.task import Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow

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


def create_compliance_vector_store_if_needed(registry: ToolRegistry) -> Optional[str]:
    """
    Creates a Vector Store for compliance documents if it doesn't exist
    and uploads sample compliance data.

    Args:
        registry: The ToolRegistry instance to use for tool operations

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
        list_result = registry.execute_tool("list_vector_stores", {})

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
            create_result = registry.execute_tool("create_vector_store", {"name": vs_name})

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
        """

        try:
            # Create a temporary file with the compliance content
            with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt", encoding="utf-8") as temp_file:
                temp_file.write(compliance_content)
                temp_file_path = temp_file.name

            # Verify the file exists
            if not os.path.exists(temp_file_path):
                raise FileNotFoundError(f"Temporary file not found at {temp_file_path}")

            logger.info(f"Attempting upload from path: {temp_file_path}")
            upload_result = registry.execute_tool(
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


# --- Patch Implementation ---
def patch_workflow_engine():
    """Apply patches to the workflow engine to support direct handler tasks."""
    # Store the original execute_task method
    original_execute_task = WorkflowEngine.execute_task

    # Define our patched method
    def patched_execute_task(self, task):
        # Check if this is a DirectHandlerTask
        if isinstance(task, DirectHandlerTask):
            logger.info(f"Using direct handler execution for task {task.id}")
            # Call the DirectHandlerTask's execute method directly
            result = task.execute(agent=None)  # We don't have the agent here, but that's okay for simple tasks
            return result
        else:
            # Call the original method for non-DirectHandlerTask tasks
            return original_execute_task(self, task)

    # Apply the patch
    WorkflowEngine.execute_task = patched_execute_task
    logger.info("Applied workflow engine patch for DirectHandlerTask support")


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
    registry.register_tool("log_alert", log_alert_handler)
    registry.register_tool("log_info", log_info_handler)

    # Apply our patch to the workflow engine
    patch_workflow_engine()

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
            """
        },
        use_file_search=True,
        file_search_vector_store_ids=[compliance_vs_id],  # Use the compliance VS
        max_retries=1,
        next_task_id_on_success="task_2_evaluate_report",
        next_task_id_on_failure=None,  # End workflow on failure
    )
    workflow.add_task(task1)

    # Task 2: Evaluate Compliance Report (LLM) - Parses JSON output from Task 1
    task2_input_data = {
        # Pass the raw output of task 1, which should be the JSON string
        "prompt": """Parse the following JSON compliance analysis report:
        --- ANALYSIS REPORT (JSON) ---
        ${task_1_analyze_risk_llm.output_data}
        --- END REPORT ---

        Based *only* on the 'risk_level' field and the content of the 'findings' array in the JSON report:
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
    task2_use_file_search = False
    task2_file_search_vector_store_ids = []

    if ltm_vs_id:
        task2_use_file_search = True
        task2_file_search_vector_store_ids.append(ltm_vs_id)

    task2 = create_task(
        task_id="task_2_evaluate_report",
        name="Evaluate Compliance Findings",
        is_llm_task=True,
        input_data=task2_input_data,
        dependencies=["task_1_analyze_risk_llm"],
        use_file_search=task2_use_file_search,
        file_search_vector_store_ids=task2_file_search_vector_store_ids,
        next_task_id_on_success="task_3_log_alert",  # Always check condition 3 next
    )
    workflow.add_task(task2)

    # Task 3 (Conditional): Log Critical Alert
    # Convert condition dict to string
    condition_str = "output_data.get('Action') == 'ACTION_REQUIRED'"

    task3 = create_task(
        task_id="task_3_log_alert",
        name="Log Critical Compliance Alert",
        tool_name="log_alert",
        input_data={
            "message": f"Compliance check requires immediate action for item described starting with: "
            f"'{item_description[:100]}...'. Assessment Summary: ${{task_2_evaluate_report.output_data[Summary]}}",
        },
        dependencies=["task_2_evaluate_report"],
        condition=condition_str,  # Use string condition directly
        next_task_id_on_success=None,  # End path if alert is logged
        next_task_id_on_failure="task_4_log_info",  # Go to info log if condition fails
    )
    workflow.add_task(task3)

    # Task 4 (Conditional): Log Info/Recommendation
    task4 = create_task(
        task_id="task_4_log_info",
        name="Log Compliance Review Recommendation",
        tool_name="log_info",
        input_data={
            "message": f"Compliance check completed for item starting with: '{item_description[:100]}...'. "
            f"Status: ${{task_2_evaluate_report.output_data[Action]}}. "
            f"Summary: ${{task_2_evaluate_report.output_data[Summary]}}",
        },
        dependencies=["task_2_evaluate_report"],
        # No explicit condition needed if it's the fallback path from Task 3's failure
        next_task_id_on_success=None,  # End path
    )
    workflow.add_task(task4)

    return workflow


# Instead of using a completely custom DirectHandlerTask, let's create a subclass of Task
class DirectHandlerTask(Task):
    """
    A Task subclass that directly executes a handler function instead of using the tool registry.
    """

    def __init__(
        self,
        task_id,
        name,
        handler,
        input_data=None,
        condition=None,
        next_task_id_on_success=None,
        next_task_id_on_failure=None,
        max_retries=0,
    ):
        # Call the parent constructor with standard parameters
        # Use a dummy tool name to satisfy the validation
        super().__init__(
            task_id=task_id,
            name=name,
            tool_name="_direct_handler_",  # Use a special prefix that won't conflict with real tools
            is_llm_task=False,
            input_data=input_data,
            condition=condition,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            max_retries=max_retries,
        )
        # Store the handler function
        self.handler = handler
        # Flag to indicate this is a direct handler task
        self._is_direct_handler = True

    def execute(self, agent=None):
        """Override the execute method to directly call the handler function."""
        logger.info(f"Executing direct handler task: {self.name} (ID: {self.id})")

        try:
            # Execute handler directly instead of using the registry
            logger.info(f"Calling direct handler for task {self.id}")
            result = self.handler(self.input_data)
            logger.info(f"Direct handler execution result: {result}")

            # Set output directly
            self.output_data = result

            # Check success
            if result.get("success", False) or result.get("status") == "success":
                self.status = "completed"
                return True
            else:
                self.status = "failed"
                return False

        except Exception as e:
            logger.error(f"Error executing direct handler: {e}")
            self.status = "failed"
            self.output_data = {"success": False, "status": "error", "error": str(e)}
            return False


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
    registry = None
    try:
        registry = ToolRegistry()  # Assumes singleton or gets the instance

        # Debug: Print all registered tools to check what's available
        logger.info(f"Tools in registry before adding: {list(registry.tools.keys())}")

        # Always register the tools (don't check if they exist first)
        registry.register_tool("log_alert", log_alert_handler)
        logger.info("Registered log_alert tool.")

        registry.register_tool("log_info", log_info_handler)
        logger.info("Registered log_info tool.")

        # Debug: Print all registered tools after adding ours
        logger.info(f"Tools in registry after adding: {list(registry.tools.keys())}")

        # Verify necessary VS tools are registered
        required_vs_tools = ["list_vector_stores", "create_vector_store", "upload_file_to_vector_store"]
        missing_tools = [tool for tool in required_vs_tools if tool not in list(registry.tools.keys())]

        if missing_tools:
            logger.error(f"Missing required Vector Store tools in registry: {missing_tools}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error initializing/registering tools: {e}")
        traceback.print_exc()  # Print full traceback for better debugging
        sys.exit(1)  # Exit with error code

    # --- Setup Compliance Vector Store ---
    compliance_vs_id = create_compliance_vector_store_if_needed(registry)
    if not compliance_vs_id:
        logger.error("Failed to ensure compliance vector store is ready. Exiting.")
        sys.exit(1)  # Exit with error code
    logger.info(f"Using compliance vector store ID: {compliance_vs_id}")

    # --- Setup LTM Vector Store (Optional) ---
    ltm_vs_id = WORKFLOW_INPUT.get("agent_config", {}).get("ltm_vector_store_id")

    # Build the workflow
    workflow = build_compliance_check_workflow(compliance_vs_id, ltm_vs_id, WORKFLOW_INPUT)

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
    # Display analysis task output
    analysis_result = next((t for t in executed_order if t.get("task_id") == "task_1_analyze_risk_llm"), None)
    if analysis_result and analysis_result.get("status") == "completed":
        analysis_output_str = analysis_result.get("output_data", {}).get("response", "{}")
        logger.info(f"  - Analysis Output (Raw): {analysis_output_str[:300]}...")
        try:
            analysis_output_dict = json.loads(analysis_output_str)
            logger.info(f"  - Analysis Parsed Risk Level: {analysis_output_dict.get('risk_level', 'PARSE_ERROR')}")
        except json.JSONDecodeError:
            logger.error("  - Analysis: Failed to parse JSON output.")
    elif analysis_result:
        logger.info(f"  - Analysis Task Status: {analysis_result.get('status')}")
    else:
        logger.info("  - Analysis Task: Did not execute.")

    # Display evaluation task output
    eval_result = next((t for t in executed_order if t.get("task_id") == "task_2_evaluate_report"), None)
    if eval_result and eval_result.get("status") == "completed":
        eval_output_str = eval_result.get("output_data", {}).get("response", "{}")
        logger.info(f"  - Evaluation Output (Raw): {eval_output_str}")
        try:
            eval_output_dict = json.loads(eval_output_str)
            logger.info(f"  - Evaluation Parsed Action: {eval_output_dict.get('Action', 'PARSE_ERROR')}")
        except json.JSONDecodeError:
            logger.error("  - Evaluation: Failed to parse JSON output.")
    elif eval_result:
        logger.info(f"  - Evaluation Task Status: {eval_result.get('status')}")
    else:
        logger.info("  - Evaluation Task: Did not execute.")

    # Check final state based on execution history
    alert_result = next((t for t in executed_order if t.get("task_id") == "task_3_log_alert"), None)
    info_result = next((t for t in executed_order if t.get("task_id") == "task_4_log_info"), None)

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


if __name__ == "__main__":
    main()
