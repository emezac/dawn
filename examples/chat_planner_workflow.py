#!/usr/bin/env python3
"""
Chat Planner Workflow Example.

This workflow takes a user prompt via chat, uses a planning task
to generate an execution plan, dynamically generates tasks based on the plan,
executes them, and returns the result.
"""
# noqa: D202

import sys
import os
import logging
import json # Added for potential parsing
import re # Needed for JSON cleaning
import jsonschema # <-- Add import for JSON schema validation
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Core imports
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.services import get_services, reset_services
from core.llm.interface import LLMInterface
from core.tools.registry_access import execute_tool, tool_exists, register_tool
from core.handlers.registry_access import get_handler, handler_exists, register_handler
from core.tools.registry import ToolRegistry
from core.handlers.registry import HandlerRegistry
from core.tools.framework_tools import get_available_capabilities
from core.utils.visualizer import visualize_workflow
from core.utils.registration_manager import ensure_all_registrations
# from core.utils.task_utils import get_output_value # Not strictly needed if using Task.get_output_value

# Example-specific imports
from examples.chat_planner_config import ChatPlannerConfig # Ensure this import works

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("chat_planner_workflow")

# --- Define JSON Schema for the Plan ---
PLAN_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "step_id": {"type": "string", "minLength": 1},
            "description": {"type": "string"},
            "type": {"type": "string", "enum": ["tool", "handler"]},
            "name": {"type": "string", "minLength": 1},
            "inputs": {"type": "object", "additionalProperties": True},
            "outputs": {"type": "array", "items": {"type": "string"}},
            "depends_on": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["step_id", "description", "type", "name", "inputs", "depends_on"],
        "additionalProperties": False
    },
    "description": "A list of steps defining the execution plan."
}

# --- Example Plan for Mock Testing ---
EXAMPLE_PLAN = """
[
  {
    "step_id": "search_step",
    "description": "Search for information about project Dawn",
    "type": "tool",
    "name": "mock_search",
    "inputs": {
      "query": "project Dawn documentation"
    },
    "outputs": ["search_results"],
    "depends_on": []
  },
  {
    "step_id": "summarize_step",
    "description": "Summarize the information found about project Dawn",
    "type": "handler",
    "name": "mock_summarize_handler",
    "inputs": {
      "content": "${search_step.result}",
      "max_length": 200
    },
    "outputs": ["summary"],
    "depends_on": ["search_step"]
  }
]
"""

def plan_user_request_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """
    Handler for the "Think & Analyze" planning task.
    Takes user request and context, generates a structured plan using an LLM.
    Can detect ambiguity and request clarification when needed.
    """
    logger.info(f"Executing planning handler for task: {task.id}")
    user_request = input_data.get("user_request", "")
    available_tools_str = input_data.get("available_tools_context", "No tools provided.")
    available_handlers_str = input_data.get("available_handlers_context", "No handlers provided.")
    clarification_history = input_data.get("clarification_history", []) # Default handled by engine now
    clarification_count = input_data.get("clarification_count", 0) # Default handled by engine now
    skip_ambiguity_check = input_data.get("skip_ambiguity_check", False) # Default handled by engine now

    # Now defaults should be correctly resolved by the engine, check types
    if not isinstance(clarification_history, list):
        logger.warning(f"plan_user_request_handler received non-list clarification_history ({type(clarification_history)}), using empty list.")
        clarification_history = []
    if not isinstance(clarification_count, int):
        logger.warning(f"plan_user_request_handler received non-int clarification_count ({type(clarification_count)}), using 0.")
        clarification_count = 0
    if not isinstance(skip_ambiguity_check, bool):
        logger.warning(f"plan_user_request_handler received non-bool skip_ambiguity_check ({type(skip_ambiguity_check)}), using False.")
        skip_ambiguity_check = False

    try:
        max_clarifications = ChatPlannerConfig.get_max_clarifications()
    except AttributeError:
        logger.warning("ChatPlannerConfig.get_max_clarifications() not found. Defaulting to 3.")
        max_clarifications = 3


    if not user_request:
        logger.error("Missing user_request input in plan_user_request_handler.")
        # Return structure expected by engine/task standard output
        return {"success": False, "error": "Missing user_request input.", "status": "failed"}

    full_context = user_request
    if clarification_history:
        full_context += "\n\nPrevious clarifications:\n"
        for i, clr in enumerate(clarification_history):
            q = clr.get('question', '') if isinstance(clr, dict) else ''
            a = clr.get('answer', '') if isinstance(clr, dict) else ''
            full_context += f"\nQ{i+1}: {q}\nA{i+1}: {a}\n"


    if clarification_count < max_clarifications and not skip_ambiguity_check:
        try:
            ambiguity_prompt_template = ChatPlannerConfig.get_prompt("ambiguity_check")
            ambiguity_prompt = ambiguity_prompt_template.format(
                user_request=full_context,
                available_tools=available_tools_str,
                available_handlers=available_handlers_str
            )
        except KeyError as e:
             logger.warning(f"Ambiguity prompt template missing variable: {e}. Using default.")
             ambiguity_prompt = f"Analyze for ambiguity: {full_context}\nTools:{available_tools_str}\nHandlers:{available_handlers_str}"
        except AttributeError:
             logger.error("ChatPlannerConfig.get_prompt('ambiguity_check') failed.")
             # Proceed without check? Or fail? Let's proceed.
             ambiguity_prompt = None

        if ambiguity_prompt:
            try:
                services = get_services()
                llm_interface = services.get_llm_interface()
                if not llm_interface: raise ValueError("LLMInterface not found")

                logger.info("Checking request for ambiguity using LLM...")
                ambiguity_response = llm_interface.execute_llm_call(
                    prompt=ambiguity_prompt,
                    system_message=ChatPlannerConfig.get_planning_system_message(),
                    max_tokens=ChatPlannerConfig.get_max_tokens(),
                    temperature=ChatPlannerConfig.get_llm_temperature()
                )

                if ambiguity_response.get("success"):
                    raw_output = ambiguity_response.get("response", "")
                    try:
                        cleaned_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_output, flags=re.MULTILINE | re.IGNORECASE).strip()
                        if not cleaned_json: raise ValueError("Empty JSON string")
                        ambiguity_result = json.loads(cleaned_json)

                        if isinstance(ambiguity_result, dict) and ambiguity_result.get("needs_clarification") is True:
                            logger.info("Ambiguity detected - clarification needed.")
                            details = ambiguity_result.get("ambiguity_details", [])
                            if not isinstance(details, list): details = []
                            # Return the result dictionary expected by the workflow
                            return {
                                "success": True, # Handler succeeded in detecting ambiguity
                                "result": {
                                    "needs_clarification": True,
                                    "ambiguity_details": details,
                                    "original_request": user_request,
                                    "clarification_count": clarification_count,
                                    "clarification_history": clarification_history
                                },
                                # Status should be set by engine based on success
                            }
                        else:
                             logger.info("No clarification needed according to ambiguity check.")
                    except (json.JSONDecodeError, ValueError) as parse_err:
                         logger.error(f"Error processing ambiguity response: {parse_err}, raw: {raw_output[:100]}")
                else:
                    logger.error(f"Ambiguity check LLM call failed: {ambiguity_response.get('error')}")
            except Exception as check_err:
                logger.error(f"Error during ambiguity check execution: {check_err}", exc_info=True)

    # --- Generate plan ---
    logger.info("Proceeding to generate execution plan...")
    try:
        planning_prompt_template = ChatPlannerConfig.get_prompt("planning")
        planning_prompt = planning_prompt_template.format(
            user_request=full_context,
            available_tools=available_tools_str,
            available_handlers=available_handlers_str
        )
    except KeyError as e:
        logger.warning(f"Planning prompt template missing variable: {e}. Using default.")
        planning_prompt = f"Create JSON plan for: {full_context}\nTools:{available_tools_str}\nHandlers:{available_handlers_str}"
    except AttributeError:
         logger.error("ChatPlannerConfig.get_prompt('planning') failed.")
         return {"success": False, "error": "Failed to get planning prompt template.", "status": "failed"}


    try:
        services = get_services()
        llm_interface = services.get_llm_interface()
        if not llm_interface: raise ValueError("LLMInterface not found")

        plan_response = llm_interface.execute_llm_call(
            prompt=planning_prompt,
            system_message=ChatPlannerConfig.get_planning_system_message(),
            max_tokens=ChatPlannerConfig.get_max_tokens(),
            temperature=ChatPlannerConfig.get_llm_temperature()
        )

        if not plan_response.get("success"):
            error_msg = f"Plan generation failed: {plan_response.get('error', 'LLM plan generation failed')}"
            return {"success": False, "error": error_msg, "status": "failed"}

        raw_plan_output = plan_response.get("response", "")
        return {
            "success": True,
            "result": {
                "raw_llm_output": raw_plan_output,
                "needs_clarification": False, # Explicitly false if plan generated
                "clarification_count": clarification_count,
                "clarification_history": clarification_history
            }
            # Status 'completed' will be set by engine
        }
    except Exception as plan_err:
        logger.error(f"Error during plan generation: {plan_err}", exc_info=True)
        return {"success": False, "error": f"Plan generation failed: {str(plan_err)}", "status": "failed"}


def validate_plan_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """Validates the structure and content of the generated plan."""
    logger.info(f"Executing plan validation handler for task: {task.id}")
    raw_plan_output = input_data.get("raw_llm_output") # Should be resolved correctly now
    tool_details = input_data.get("tool_details", [])
    handler_details = input_data.get("handler_details", [])

    # --- Get config safely (using Option B - commented out LLM validation) ---
    try:
        strictness = ChatPlannerConfig.get_validation_strictness()
        logger.info(f"Validation strictness from config: {strictness}")
    except AttributeError:
        logger.warning("ChatPlannerConfig.get_validation_strictness() not found. Defaulting to 'strict'.")
        strictness = "strict"

    # Removed calls to should_use_llm_validation and should_fix_with_llm
    use_llm_validation = False
    fix_with_llm = False
    # ----------------------------------------------------------------------

    available_tool_names = {t['name'] for t in tool_details if isinstance(t, dict) and 'name' in t}
    available_handler_names = {h['name'] for h in handler_details if isinstance(h, dict) and 'name' in h} 

    validation_errors = []
    validation_warnings = []
    parsed_plan = None
    fixed_by_llm = False    # Not used if LLM validation is off
    validated_by_llm = False # Not used if LLM validation is off

    # --- Check if raw_plan_output was resolved and is a string ---
    if not raw_plan_output or not isinstance(raw_plan_output, str):
        error_msg = f"Invalid or missing 'raw_llm_output' input. Expected string, got {type(raw_plan_output)}. Value: '{str(raw_plan_output)[:100]}...'"
        logger.error(error_msg)
        validation_errors.append(error_msg)
        # Immediately return failure if input is wrong
        return {
            "success": False, "status": "failed", "error": "Missing or invalid raw plan input",
            "validation_errors": validation_errors, "result": {"validated_plan": None}
        }
    # ------------------------------------------------------------

    try:
        # 1. Clean and Parse JSON
        logger.debug(f"Raw plan before cleaning: {raw_plan_output[:200]}...")
        cleaned_json_string = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_plan_output, flags=re.MULTILINE | re.IGNORECASE).strip()
        if not cleaned_json_string:
             raise json.JSONDecodeError("Plan output is empty after cleaning markdown.", "", 0)
        parsed_plan = json.loads(cleaned_json_string)
        logger.debug(f"Cleaned plan string parsed successfully.")

        # 2. Basic Structure and Schema Validation
        jsonschema.validate(instance=parsed_plan, schema=PLAN_SCHEMA)
        logger.info("Plan passed JSON schema validation.")

        # 3. Content Validation
        all_step_ids = set()
        if not isinstance(parsed_plan, list): # Ensure parsed_plan is a list
             raise ValueError(f"Parsed plan is not a list, but type {type(parsed_plan)}")

        for i, step in enumerate(parsed_plan):
            if not isinstance(step, dict):
                 validation_errors.append(f"Step {i+1}: Invalid format, not a dictionary.")
                 continue # Skip further validation for this invalid step

            step_id = step.get("step_id")
            step_type = step.get("type")
            capability_name = step.get("name")
            dependencies = step.get("depends_on", [])

            if not step_id or not isinstance(step_id, str): validation_errors.append(f"Step {i+1}: Missing or invalid 'step_id'.")
            elif step_id in all_step_ids: validation_errors.append(f"Step {i+1}: Duplicate step_id '{step_id}'.")
            if step_id: all_step_ids.add(step_id) # Only add valid IDs to the set

            if not capability_name or not isinstance(capability_name, str):
                 validation_errors.append(f"Step {i+1} ('{step_id}'): Missing or invalid 'name'.")

            if step_type == "tool":
                if capability_name and capability_name not in available_tool_names:
                    msg = f"Step {i+1} ('{step_id}'): Tool '{capability_name}' is not available."
                    # Always add as warning, never as error, regardless of strictness
                    validation_warnings.append(msg)
            elif step_type == "handler":
                if capability_name and capability_name not in available_handler_names:
                    msg = f"Step {i+1} ('{step_id}'): Handler '{capability_name}' is not available."
                    # Always add as warning, never as error, regardless of strictness
                    validation_warnings.append(msg)
            elif step_type: # Error only if type is present but invalid
                validation_errors.append(f"Step {i+1} ('{step_id}'): Invalid 'type' ('{step_type}'). Must be 'tool' or 'handler'.")
            else: # Error if type is missing
                 validation_errors.append(f"Step {i+1} ('{step_id}'): Missing 'type' field.")

            if not isinstance(dependencies, list):
                validation_errors.append(f"Step {i+1} ('{step_id}'): 'depends_on' must be a list.")
            else:
                for dep_id in dependencies:
                    # Check against steps defined *earlier* in the plan for DAG validity
                    # A simple check here is if dep_id is in the set of *all* declared IDs
                    # A more robust check would ensure dep_id corresponds to a previous step index.
                    # For now, check if it's a declared ID at all.
                    if dep_id not in all_step_ids:
                        # This check might be too early if dependencies can be declared later.
                        # Let's just check if the ID exists anywhere in the plan for now.
                        if not any(s.get("step_id") == dep_id for s in parsed_plan if isinstance(s,dict)):
                             validation_errors.append(f"Step {i+1} ('{step_id}'): Dependency '{dep_id}' refers to a non-existent step ID.")

        logger.info("Plan passed internal consistency checks.")

    # Catch specific expected errors first
    except json.JSONDecodeError as e:
        logger.error(f"Plan validation failed: JSON parsing error - {e}")
        validation_errors.append(f"Invalid JSON format in raw_llm_output: {e}")
        return {
            "success": False, "status": "failed", "error": f"JSON parsing error: {e}",
            "validation_errors": validation_errors,
            "result": {"validated_plan": None, "validation_errors": validation_errors}
        }
    except jsonschema.ValidationError as e:
        logger.error(f"Plan validation failed: Schema validation error - {e.message}")
        validation_errors.append(f"Schema validation failed: {e.message} at path {'/'.join(map(str, e.path))}")
        return {
            "success": False, "status": "failed", "error": f"Schema validation error: {e.message}",
            "validation_errors": validation_errors,
            "result": {"validated_plan": None, "validation_errors": validation_errors}
        }
    except ValueError as e: # Catch ValueErrors raised during validation
        logger.error(f"Plan validation failed: {e}")
        validation_errors.append(f"Validation logic error: {str(e)}")
    # Catch any other unexpected errors
    except Exception as e:
        logger.error(f"Plan validation failed: Unexpected error - {e}", exc_info=True)
        validation_errors.append(f"Unexpected validation error: {str(e)}")
        return {
            "success": False, "status": "failed", "error": f"Unexpected validation error: {str(e)}",
            "validation_errors": validation_errors,
            "result": {"validated_plan": None, "validation_errors": validation_errors}
        }

    # --- LLM Validation Block Removed (Option B applied) ---

    # Determine final success
    if validation_errors:
         logger.error(f"Plan validation finished with errors: {validation_errors}")
         return {
             "success": False, "status": "failed", "error": "Plan validation failed",
             "validation_errors": validation_errors,
             "validation_warnings": validation_warnings,
             "result": {"validated_plan": None, "validation_errors": validation_errors}
         }
    else:
        logger.info("Plan validation successful.")
        if validation_warnings:
            logger.warning(f"Plan validation finished with warnings: {validation_warnings}")
        return {
            "success": True, "status": "completed",
            "result": {
                "validated_plan": parsed_plan,
                "validation_warnings": validation_warnings,
                "validation_errors": [],
                "strictness": strictness,
                # "fixed_by_llm": fixed_by_llm, # Removed
                # "validated_by_llm": validated_by_llm # Removed
            }
        }

# --- plan_to_tasks_handler (Keep as is) ---
def plan_to_tasks_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    logger.info(f"Executing plan-to-tasks handler for task: {task.id}")
    validated_plan = input_data.get("validated_plan")

    if not isinstance(validated_plan, list):
        logger.error("Validated plan is missing or not a list in plan_to_tasks_handler.")
        return {"success": False, "error": "Validated plan is missing or not a list.", "status": "failed"}

    if len(validated_plan) == 0:
        logger.warning("Empty plan provided to plan_to_tasks_handler.")
        return {"success": False, "error": "No tasks to execute", "status": "failed"}

    task_definitions = []
    conversion_warnings = []

    for step in validated_plan:
        if not isinstance(step, dict):
            conversion_warnings.append(f"Skipping invalid step (not a dict): {step}")
            continue

        task_id = step.get("step_id")
        step_type = step.get("type")
        capability_name = step.get("name")
        inputs = step.get("inputs", {})
        description = step.get("description", f"Execute {step_type} {capability_name}")
        depends_on = step.get("depends_on", [])

        if not all([task_id, step_type, capability_name]):
            conversion_warnings.append(f"Skipping step due to missing required fields (step_id, type, name): {step}")
            continue
        if not isinstance(inputs, dict):
            conversion_warnings.append(f"Step '{task_id}': Inputs field is not a dictionary, defaulting to empty.")
            inputs = {}

        task_def = {
            "task_id": task_id,
            "name": description,
            "input_data": inputs,
            "depends_on": depends_on if isinstance(depends_on, list) else [],
            "is_llm_task": False,
        }
        if step_type == "tool": task_def["tool_name"] = capability_name
        elif step_type == "handler":
             task_def["handler_name"] = capability_name
             task_def["task_class"] = "DirectHandlerTask"
        else:
            conversion_warnings.append(f"Step '{task_id}': Unknown step type '{step_type}'. Skipping.")
            continue
        task_definitions.append(task_def)
    # -----------------------------------------------------------------------

    logger.info(f"Converted plan into {len(task_definitions)} task definitions.")
    if conversion_warnings:
        logger.warning(f"Plan to tasks conversion finished with warnings: {conversion_warnings}")

    return {
        "success": True, # Handler execution success
        "status": "completed",
        "result": {
            "tasks": task_definitions,
            "task_definitions": task_definitions,
            "conversion_warnings": conversion_warnings
        }
    }

def execute_dynamic_tasks_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """
    Executes dynamically generated tasks defined in the input.

    Imports 'resolve_path' locally at the start of the function execution.
    Simulates a mini-execution loop for the dynamic tasks.
    """
    parent_task_id = task.id
    logger.info(f"[DynamicExec:{parent_task_id}] Starting handler execution.")

    # --- Attempt to import resolve_path utility ONCE at the start ---
    resolve_path_func: Optional[Callable] = None # Declare with type hint
    try:
        # Intenta la importación crucial aquí. Si falla, el handler no puede funcionar.
        from core.utils.variable_resolver import resolve_path as rp_func
        resolve_path_func = rp_func
        logger.info(f"[DynamicExec:{parent_task_id}] Successfully imported resolve_path utility.")
    except ImportError:
         logger.error(f"[DynamicExec:{parent_task_id}] CRITICAL: Failed to import resolve_path utility. Cannot resolve inputs for dynamic tasks.", exc_info=True)
         # Fail the handler immediately if the core utility is missing
         return {"success": False, "error": "Missing core variable resolution utility.", "status": "failed"}
    # ----------------------------------------------------------------

    # --- Input Validation ---
    tasks_to_execute = input_data.get("generated_tasks") or input_data.get("tasks")
    if not tasks_to_execute or not isinstance(tasks_to_execute, list):
        logger.warning(f"[DynamicExec:{parent_task_id}] No valid 'generated_tasks'/'tasks' list found in input.")
        return {"success": True, "status": "completed", "result": {"message": "No valid dynamic tasks provided.", "outputs": []}}

    original_workflow_vars = input_data.get("original_input", {})
    if not isinstance(original_workflow_vars, dict):
        logger.warning(f"[DynamicExec:{parent_task_id}] 'original_input' not a dict, using empty.")
        original_workflow_vars = {}

    # --- Get Services ---
    logger.debug(f"[DynamicExec:{parent_task_id}] Acquiring services...")
    services = get_services()
    tool_registry = getattr(services, 'tool_registry', None)
    handler_registry = getattr(services, 'handler_registry', None)

    if not tool_registry:
        logger.error(f"[DynamicExec:{parent_task_id}] ToolRegistry not found.")
        return {"success": False, "error": "Missing ToolRegistry service.", "status": "failed"}
    if not handler_registry:
        logger.error(f"[DynamicExec:{parent_task_id}] HandlerRegistry not found.")
        return {"success": False, "error": "Missing HandlerRegistry service.", "status": "failed"}
    logger.debug(f"[DynamicExec:{parent_task_id}] Services acquired.")

    # --- Initialization for Loop ---
    task_objects: Dict[str, Dict] = {}
    task_outputs_dict: Dict[str, Dict] = {} # Stores {task_id: output_dict}
    final_step_outputs_list: List[Dict] = []

    # 1. Prepare Task Objects
    logger.debug(f"[DynamicExec:{parent_task_id}] Preparing {len(tasks_to_execute)} dynamic task objects...")
    for i, task_def in enumerate(tasks_to_execute):
        if not isinstance(task_def, dict): logger.warning(f"[DynamicExec:{parent_task_id}] Skipping task definition at index {i}: not a dict."); continue
        task_id = task_def.get("task_id");
        if not task_id or not isinstance(task_id, str): logger.warning(f"[DynamicExec:{parent_task_id}] Skipping task definition at index {i}: missing/invalid 'task_id'."); continue
        if task_id in task_objects: logger.warning(f"[DynamicExec:{parent_task_id}] Duplicate dynamic task_id '{task_id}'. Overwriting.")
        task_objects[task_id] = {"id": task_id, "name": task_def.get("name", task_id), "definition": task_def, "status": "pending", "depends_on": task_def.get("depends_on", []), "input_data_template": task_def.get("input_data", {}), "output_data": None}
    logger.debug(f"[DynamicExec:{parent_task_id}] Prepared {len(task_objects)} valid task objects.")

    # 2. Execution Loop
    completed_tasks = set()
    remaining_tasks = set(task_objects.keys())
    max_iterations = len(remaining_tasks) * 2 + 5
    iteration = 0

    logger.info(f"[DynamicExec:{parent_task_id}] Starting execution loop for {len(remaining_tasks)} tasks.")
    while remaining_tasks and iteration < max_iterations:
        iteration += 1
        executed_in_iteration = set()
        logger.debug(f"[DynamicExec:{parent_task_id}] Iteration {iteration}. Remaining: {len(remaining_tasks)}")

        for task_id in list(remaining_tasks): # Iterate on copy
            task_info = task_objects[task_id]
            dependencies = task_info.get("depends_on", [])
            if not isinstance(dependencies, list): dependencies = []

            # Check dependencies met
            if all(dep_id in completed_tasks for dep_id in dependencies):
                logger.info(f"[DynamicExec:{parent_task_id}] Dependencies met for '{task_id}'.")
                task_def = task_info["definition"]
                input_template = task_info["input_data_template"]
                capability_name = task_def.get("tool_name") or task_def.get("handler_name")
                is_tool = "tool_name" in task_def
                output = {"task_id": task_id, "success": False, "status": "failed"} # Default

                # Check dependency failure
                dependency_failed = False
                for dep_id in dependencies:
                    dep_output = task_outputs_dict.get(dep_id)
                    if dep_output and not dep_output.get("success", False):
                        dependency_failed = True; output = {"task_id": task_id, "success": False, "status": "skipped", "error": f"Dependency '{dep_id}' failed"}; break

                # Resolve Inputs
                processed_inputs = {}
                resolution_failed = False
                if not dependency_failed:
                    logger.debug(f"[DynamicExec:{parent_task_id}] Resolving inputs for '{task_id}'...")
                    try:
                        resolution_context = {**original_workflow_vars, **task_outputs_dict}
                        if isinstance(input_template, dict):
                            for k, v in input_template.items():
                                if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                                     ref_path = v[2:-1]
                                     try:
                                         # --- USA LA FUNCIÓN IMPORTADA (ya verificada) ---
                                         resolved_value = resolve_path_func(resolution_context, ref_path)
                                         processed_inputs[k] = resolved_value
                                         logger.debug(f"[DynamicExec:{parent_task_id}] Resolved '{k}':'{v}' to type {type(resolved_value)}")
                                     except Exception as res_err:
                                         logger.warning(f"[DynamicExec:{parent_task_id}] Failed to resolve input '{k}':'{v}': {res_err}. Using None.")
                                         processed_inputs[k] = None
                                else: processed_inputs[k] = v
                        logger.debug(f"[DynamicExec:{parent_task_id}] Final inputs for '{task_id}': {processed_inputs}")
                    except Exception as e:
                        logger.error(f"[DynamicExec:{parent_task_id}] Input resolution process failed for '{task_id}': {e}", exc_info=True)
                        resolution_failed = True; output["error"] = f"Input resolution failed: {str(e)}"

                # Execute Task
                if not dependency_failed and not resolution_failed:
                    logger.info(f"[DynamicExec:{parent_task_id}] Executing capability '{capability_name}' for task '{task_id}'...")
                    try:
                        if is_tool:
                            if hasattr(tool_registry, 'tools') and capability_name in tool_registry.tools:
                                output = tool_registry.execute_tool(capability_name, processed_inputs)
                            else: output = {"task_id": task_id, "success": False, "status": "failed", "error": f"Tool '{capability_name}' not found."}
                        else: # Assume handler
                            if handler_registry.handler_exists(capability_name):
                                handler_func = handler_registry.get_handler(capability_name)
                                mock_task_obj = type('obj', (object,), {'id': task_id, 'name': task_info['name']})()
                                output = handler_func(mock_task_obj, processed_inputs)
                            else: output = {"task_id": task_id, "success": False, "status": "failed", "error": f"Handler '{capability_name}' not found."}

                        # Standardize output
                        if not isinstance(output, dict): output = {"result": output}
                        output["task_id"] = task_id
                        if "success" not in output: output["success"] = "error" not in output
                        output["status"] = "completed" if output["success"] else "failed"
                        if "result" in output and "response" not in output: output["response"] = output["result"]
                        elif "response" in output and "result" not in output: output["result"] = output["response"]
                        elif "result" not in output and "response" not in output and output.get("success"): output["result"] = None; output["response"] = None

                    except Exception as e:
                        import traceback
                        logger.error(f"[DynamicExec:{parent_task_id}] Exception during execution of '{task_id}': {e}", exc_info=True)
                        output = {"task_id": task_id, "success": False, "status": "failed", "error": f"Execution error: {str(e)}", "error_type": type(e).__name__, "error_details": {"traceback": traceback.format_exc()}}

                # Store Result & Update State
                task_info["output_data"] = output
                task_info["status"] = output.get("status", "failed")
                task_outputs_dict[task_id] = output
                final_step_outputs_list.append(output)
                completed_tasks.add(task_id)
                executed_in_iteration.add(task_id)
                logger.info(f"[DynamicExec:{parent_task_id}] Finished '{task_info['name']}' | Status: {task_info['status']}")

        # End of inner loop (for task_id in list(remaining_tasks))
        remaining_tasks -= executed_in_iteration
        if not executed_in_iteration and remaining_tasks:
            logger.error(f"[DynamicExec:{parent_task_id}] Stuck? Remaining: {remaining_tasks}. Check dependencies.")
            for tid in list(remaining_tasks):
                 if task_objects[tid]["status"] == "pending":
                     output = {"task_id": tid, "success": False, "status": "skipped", "error": "Unmet dependencies or cycle."}
                     task_objects[tid]["output_data"] = output; task_objects[tid]["status"] = "skipped"; task_outputs_dict[tid] = output; final_step_outputs_list.append(output); completed_tasks.add(tid)
            remaining_tasks.clear(); break

    # End of while loop
    if iteration >= max_iterations and remaining_tasks:
         logger.error(f"[DynamicExec:{parent_task_id}] Max iterations reached. Remaining tasks: {remaining_tasks}")
         for tid in list(remaining_tasks):
              if task_objects[tid]["status"] == "pending":
                  output = {"task_id": tid, "success": False, "status": "failed", "error": "Execution timed out (max iterations)."}
                  task_objects[tid]["output_data"] = output; task_objects[tid]["status"] = "failed"; task_outputs_dict[tid] = output; final_step_outputs_list.append(output); completed_tasks.add(tid)

    logger.info(f"[DynamicExec:{parent_task_id}] Finished executing dynamic tasks.")
    return {
        "success": True,
        "status": "completed",
        "result": {
            "message": f"Executed {len(final_step_outputs_list)} dynamic tasks.",
            "outputs": final_step_outputs_list
        }
    }
# --- summarize_results_handler (Keep as is) ---
def summarize_results_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    logger.info(f"Executing summarize results handler for task: {task.id}")
    execution_result_dict = input_data.get("execution_results", {})
    original_plan = input_data.get("original_plan", [])
    original_input = input_data.get("original_input", "")

    task_outputs_list = execution_result_dict.get("outputs", [])

    # --- Simple Text Summary ---
    final_summary = f"Summary for request: '{original_input}'\n"
    final_summary += f"Plan Steps Attempted: {len(task_outputs_list)}\n"
    success_count = sum(1 for o in task_outputs_list if isinstance(o, dict) and o.get("success"))
    fail_count = len(task_outputs_list) - success_count
    final_summary += f"- Succeeded: {success_count}\n- Failed/Skipped: {fail_count}\n"

    if task_outputs_list:
        final_output = {}
        last_planned_step_id = original_plan[-1].get("step_id") if isinstance(original_plan, list) and original_plan else None
        if last_planned_step_id:
             final_output = next((o for o in task_outputs_list if isinstance(o, dict) and o.get("task_id") == last_planned_step_id), None)
        if not final_output: # Fallback to last executed
            final_output = task_outputs_list[-1] if task_outputs_list else None

        if isinstance(final_output, dict):
            final_summary += f"\nFinal Result Preview (from task '{final_output.get('task_id', 'N/A')}'):\n"
            if final_output.get("success"):
                result_data = final_output.get("result", final_output.get("response", "No result field"))
                final_summary += f"  Status: Success\n  Output: {str(result_data)[:200]}{'...' if len(str(result_data)) > 200 else ''}"
            else:
                error_data = final_output.get("error", "No error details")
                final_summary += f"  Status: Failed/Skipped\n  Error: {str(error_data)[:200]}{'...' if len(str(error_data)) > 200 else ''}"
        else: final_summary += "\nNo final result data available."
    else: final_summary += "\nNo tasks were executed."

    # --- Optional LLM Summary ---
    # try:
    #     if ChatPlannerConfig.get_use_llm_summarization(): # Example config check
    #         # ... call LLM ...
    #         # final_summary = llm_summary
    #         # is_llm_summary = True
    # except AttributeError: pass # Config option might not exist
    is_llm_summary = False
    # --------------------------

    logger.info("Generated final summary.")
    return {
        "success": True, "status": "completed",
        "result": {
            "final_summary": final_summary,
            "task_outputs": task_outputs_list,
            "is_llm_summary": is_llm_summary
        }
    }


# --- process_clarification_handler (Keep as is) ---
def process_clarification_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    logger.info(f"Processing clarification response for task: {task.id}")
    user_clarification = input_data.get("user_clarification", "")
    original_request = input_data.get("original_request", "")
    ambiguity_details = input_data.get("ambiguity_details", [])
    clarification_count = input_data.get("clarification_count", 0)
    clarification_history = input_data.get("clarification_history", [])

    if not user_clarification:
        return {"success": False, "error": "Missing user clarification response", "status": "failed"}

    if not isinstance(original_request, str): original_request = ""
    if not isinstance(ambiguity_details, list): ambiguity_details = []
    if not isinstance(clarification_count, int): clarification_count = 0
    if not isinstance(clarification_history, list): clarification_history = []

    questions = [str(d.get("q", d.get("question", "Clarification requested."))) for d in ambiguity_details if isinstance(d, dict)]
    combined_question = "; ".join(questions) if questions else "General clarification needed."

    new_clarification_entry = {"question": combined_question, "answer": user_clarification}
    updated_history = clarification_history + [new_clarification_entry]
    next_clarification_count = clarification_count + 1

    logger.info(f"Processed clarification. Count: {next_clarification_count}")
    return {
        "success": True, "status": "completed",
        "result": {
            "user_request": original_request,
            "clarification_history": updated_history,
            "clarification_count": next_clarification_count,
        }
    }

# --- await_input_handler (Keep as is) ---
def await_input_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    logger.info(f"Task {task.id}: Entering 'awaiting_input' state (simulation).")
    return {
        "success": True,
        "status": "awaiting_input", # Special status for engine/UI
        "result": {
            "status": "awaiting_input", # Mirror status in result
            "message": "Workflow paused, awaiting user clarification.",
            **input_data # Pass through all input data for context
        }
    }

# --- check_clarification_needed_default_handler (Keep as is) ---
def check_clarification_needed_default_handler(task: DirectHandlerTask, input_data: dict) -> dict:
     plan_result = input_data.get("plan", {}) # Expecting output from plan task
     needs_clar = False
     details = []
     orig_req = ""
     count = 0
     history = []
     if isinstance(plan_result, dict):
          needs_clar = plan_result.get("needs_clarification") is True
          details = plan_result.get("ambiguity_details", [])
          orig_req = plan_result.get("original_request", input_data.get("user_prompt", ""))
          count = plan_result.get("clarification_count", 0)
          history = plan_result.get("clarification_history", [])
          # Basic type safety
          if not isinstance(details, list): details = []
          if not isinstance(history, list): history = []
          if not isinstance(count, int): count = 0
     else:
          logger.warning(f"check_clarification_needed received non-dict 'plan' input: {type(plan_result)}. Assuming no clarification needed.")

     return {
         "success": True, "status": "completed",
         "result": {
             "needs_clarification": needs_clar,
             "ambiguity_details": details,
             "original_request": orig_req,
             "clarification_count": count,
             "clarification_history": history
         }
     }


# --- Workflow Definition ---
# Apply corrections from Step 1 of previous answer: remove output_key, use standard refs
def build_chat_planner_workflow() -> Workflow:
    """
    Builds the chat-driven workflow with corrected variable references.
    """
    workflow = Workflow(
        workflow_id="chat_planner_workflow",
        name="Chat-Driven Planning Workflow"
    )

    # Phase 1: Get Capabilities
    get_capabilities_task = Task(
        task_id="get_capabilities",
        name="Get Available Tools and Handlers",
        tool_name="get_available_capabilities",
        input_data={},
        next_task_id_on_success="think_analyze_plan"
    )
    workflow.add_task(get_capabilities_task)

    # Phase 2: Planning & Clarification Loop
    plan_task = DirectHandlerTask(
        task_id="think_analyze_plan",
        name="Generate Execution Plan",
        handler_name="plan_user_request_handler",
        input_data={
            "user_request": "${user_prompt}",
            "available_tools_context": "${get_capabilities.result.tools_context}", # Use standard ref
            "available_handlers_context": "${get_capabilities.result.handlers_context}", # Use standard ref
            "clarification_history": "${clarification_history:[]}", # Use default syntax
            "clarification_count": "${clarification_count:0}", # Use default syntax
            "skip_ambiguity_check": "${skip_ambiguity_check:False}" # Use default syntax
        },
        # REMOVED output_key
        next_task_id_on_success="check_for_clarification_needed",
        description="Analyzes request and capabilities for planning or ambiguity."
    )
    workflow.add_task(plan_task)

    check_clarification_task = DirectHandlerTask(
        task_id="check_for_clarification_needed",
        name="Check if Clarification is Needed",
        handler_name="check_clarification_needed",
        input_data={
            "plan": "${think_analyze_plan.result}", # Use standard ref
            "user_prompt": "${user_prompt}" # Pass original prompt
        },
        # REMOVED output_key
        condition="'${result.needs_clarification}' == 'True'", # Condition uses THIS task's result
        next_task_id_on_success="await_clarification",
        next_task_id_on_failure="validate_plan",
        description="Checks planning outcome for clarification need."
    )
    workflow.add_task(check_clarification_task)

    # Clarification Branch
    await_clarification_task = DirectHandlerTask(
        task_id="await_clarification",
        name="Await User Clarification",
        handler_name="await_input_handler",
        input_data={
             # Get context from check_for_clarification_needed result
            "prompt_context": "Clarification needed for request: ${check_for_clarification_needed.result.original_request}",
            "ambiguity_details": "${check_for_clarification_needed.result.ambiguity_details}",
            "original_request": "${check_for_clarification_needed.result.original_request}",
            "clarification_count": "${check_for_clarification_needed.result.clarification_count}",
            # History comes from the original plan task result
            "clarification_history": "${think_analyze_plan.result.clarification_history}"
        },
        # REMOVED output_key
        next_task_id_on_success="process_clarification",
        description="Pauses workflow awaiting user clarification."
    )
    workflow.add_task(await_clarification_task)

    process_clarification_task = DirectHandlerTask(
        task_id="process_clarification",
        name="Process User Clarification",
        handler_name="process_clarification_handler",
        input_data={
            "user_clarification": "${user_clarification}", # From external input
             # Context from await_clarification's *input* (or its result if handler passes it through)
             # Assuming await_input_handler passes input through in its result:
            "original_request": "${await_clarification.result.original_request}",
            "ambiguity_details": "${await_clarification.result.ambiguity_details}",
            "clarification_count": "${await_clarification.result.clarification_count}",
            "clarification_history": "${await_clarification.result.clarification_history}"
        },
        # REMOVED output_key
        next_task_id_on_success="restart_planning",
        description="Integrates user's clarification."
    )
    workflow.add_task(process_clarification_task)

    # Register passthrough handler if not already done
    if not handler_exists("passthrough_handler"):
        register_handler("passthrough_handler", lambda task, data: {"success": True, "result": data})

    restart_planning_task = DirectHandlerTask(
        task_id="restart_planning",
        name="Restart Planning Loop",
        handler_name="passthrough_handler", # Use passthrough
        input_data={
             # Get data from process_clarification result
             "user_request": "${process_clarification.result.user_request}",
             "clarification_history": "${process_clarification.result.clarification_history}",
             "clarification_count": "${process_clarification.result.clarification_count}",
             "skip_ambiguity_check": False # Don't skip ambiguity on restart
        },
        # REMOVED output_key
        next_task_id_on_success="think_analyze_plan", # Loop back
        description="Routes back to planning with updated context."
    )
    workflow.add_task(restart_planning_task)

    # Main Execution Branch
    validate_plan_task = DirectHandlerTask(
        task_id="validate_plan",
        name="Validate Plan Structure and Content",
        handler_name="validate_plan_handler",
        input_data={
            "raw_llm_output": "${think_analyze_plan.result.raw_llm_output}", # Use standard ref
            "tool_details": "${get_capabilities.result.tool_details}",
            "handler_details": "${get_capabilities.result.handler_details}",
            "user_request": "${user_prompt}"
        },
        # REMOVED output_key
        next_task_id_on_success="plan_to_tasks",
        description="Validates the generated plan."
    )
    workflow.add_task(validate_plan_task)

    # Phase 4: Dynamic Task Generation
    plan_to_tasks_task = DirectHandlerTask(
        task_id="plan_to_tasks",
        name="Convert Plan to Executable Tasks",
        handler_name="plan_to_tasks_handler",
        input_data={
            "validated_plan": "${validate_plan.result.validated_plan}", # Use standard ref
            "original_input": "${user_prompt}"
        },
        # REMOVED output_key
        next_task_id_on_success="execute_dynamic_tasks",
        description="Transforms plan into task definitions."
    )
    workflow.add_task(plan_to_tasks_task)

    # Phase 5: Dynamic Task Execution
    execute_tasks_task = DirectHandlerTask(
        task_id="execute_dynamic_tasks",
        name="Execute Dynamic Tasks",
        handler_name="execute_dynamic_tasks_handler",
        input_data={
            "generated_tasks": "${plan_to_tasks.result.tasks}", # Use standard ref
            "original_input": workflow.variables # Pass workflow vars
        },
        # REMOVED output_key
        next_task_id_on_success="summarize_results",
        description="Executes the dynamic tasks."
    )
    workflow.add_task(execute_tasks_task)

    # Phase 6: Results and Output
    summarize_task = DirectHandlerTask(
        task_id="summarize_results",
        name="Summarize Execution Results",
        handler_name="summarize_results_handler",
        input_data={
            "execution_results": "${execute_dynamic_tasks.result}", # Use standard ref
            "original_plan": "${validate_plan.result.validated_plan}", # Use standard ref
            "original_input": "${user_prompt}"
        },
        # REMOVED output_key
        next_task_id_on_success=None, # End of workflow
        description="Generates final summary."
    )
    workflow.add_task(summarize_task)

    return workflow

# --- Mock Tools/Handlers (Keep as is) ---
def mock_search_tool(input_data):
    query = input_data.get("query", "")
    logger.info(f"[MOCK TOOL] mock_search: Searching for '{query}'")
    if "fail" in query.lower(): return {"success": False, "error": "Mock search failed."}
    return {"success": True, "result": f"Found 3 docs for '{query}'.", "response": f"Results for {query}"}

def mock_summarize_handler(task, input_data):
    text = input_data.get("content", input_data.get("text", ""))
    max_len = input_data.get("max_length", 150)
    logger.info(f"[MOCK HANDLER] mock_summarize: Summarizing '{text[:50]}...'")
    if not text: return {"success": False, "error": "No content."}
    summary = f"Summary of: {text}"
    return {"success": True, "result": summary[:max_len]}


# --- Mock LLM Interface (Keep as is) ---
class MockLLMInterface(LLMInterface):
    """Mock LLM interface for testing the workflow example."""
    def __init__(self, plan_response: str = EXAMPLE_PLAN):
        self.plan_response = plan_response
        self.ambiguity_check_response = json.dumps({"needs_clarification": False, "ambiguity_details": []})
        self.validation_response = json.dumps({"valid": True})
        self.fix_plan_response = ""

    def set_plan_response(self, plan_json_string: str): self.plan_response = plan_json_string
    def set_ambiguity_response(self, needs: bool, details: list = None): self.ambiguity_check_response = json.dumps({"needs_clarification": needs, "ambiguity_details": details or []})
    def set_validation_response(self, valid: bool, fixed_plan: str = None): self.validation_response = json.dumps({"valid": valid}); self.fix_plan_response = fixed_plan or ""

    def execute_llm_call(self, prompt: str, **kwargs) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        if "clarification" in prompt_lower or "ambiguity" in prompt_lower:
             logger.info("MOCK LLM: Returning Ambiguity Response")
             return {"success": True, "response": self.ambiguity_check_response}
        elif "validate" in prompt_lower and "plan" in prompt_lower:
             logger.info("MOCK LLM: Returning Validation Response")
             return {"success": True, "response": self.validation_response}
        # Add more specific checks if needed for fixing prompts etc.
        elif "plan" in prompt_lower: # Assume planning otherwise
             logger.info("MOCK LLM: Returning Plan Response")
             return {"success": True, "response": self.plan_response}
        else:
             logger.warning(f"MOCK LLM: Unmatched prompt, returning default plan. Prompt: {prompt[:100]}...")
             return {"success": True, "response": self.plan_response}

# --- Main execution block (Keep as is, but ensure handlers are registered) ---
def main():
    """Entry point for running the chat planner workflow example."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    logger.info("--- Initializing Chat Planner Workflow Example ---")
    reset_services()
    services = get_services()
    tool_registry = ToolRegistry(); services.register_tool_registry(tool_registry)
    handler_registry = HandlerRegistry(); services.register_handler_registry(handler_registry)

    # Register ALL handlers used by name in build_workflow
    handlers_to_register = {
        "plan_user_request_handler": plan_user_request_handler,
        "validate_plan_handler": validate_plan_handler,
        "plan_to_tasks_handler": plan_to_tasks_handler,
        "execute_dynamic_tasks_handler": execute_dynamic_tasks_handler,
        "summarize_results_handler": summarize_results_handler,
        "process_clarification_handler": process_clarification_handler,
        "await_input_handler": await_input_handler,
        "check_clarification_needed": check_clarification_needed_default_handler,
        "mock_summarize_handler": mock_summarize_handler,
        "passthrough_handler": lambda task, data: {"success": True, "result": data}
    }
    for name, func in handlers_to_register.items():
        register_handler(name, func) # Use replace=True if needed during dev
    logger.info(f"Registered {len(handlers_to_register)} handlers for standalone run.")

    # Register mock tool
    register_tool("mock_search", mock_search_tool)
    logger.info("Registered 'mock_search' tool.")

    # Ensure framework tools are registered
    ensure_all_registrations()

    # Build workflow
    workflow = build_chat_planner_workflow()
    logger.info(f"Workflow '{workflow.name}' built.")

    # Setup Mock LLM
    mock_llm = MockLLMInterface()
    services.register_llm_interface(mock_llm)
    logger.info("Registered Mock LLM Interface.")

    # Visualize (Optional)
    try:
        output_dir = os.path.join(os.path.dirname(__file__), "visualizations")
        os.makedirs(output_dir, exist_ok=True)
        viz_path = os.path.join(output_dir, f"{workflow.id}_graph")
        visualize_workflow(workflow, filename=viz_path, format="png", view=False)
        logger.info(f"Workflow visualization saved to {viz_path}.png (if graphviz installed)")
    except Exception as e: logger.warning(f"Could not generate visualization: {e}")

    # Simulate Run
    logger.info("--- Simulating Workflow Execution ---")
    from core.engine import WorkflowEngine
    engine = WorkflowEngine(workflow=workflow, llm_interface=mock_llm, tool_registry=tool_registry, services=services)
    initial_input = {"user_prompt": "Search project Dawn docs and summarize."}
    logger.info(f"Initial input: {initial_input}")
    result = engine.run(initial_input=initial_input)

    # Print results
    logger.info(f"--- Workflow Execution Finished (Status: {workflow.status}) ---")
    if result.get("success"):
        final_summary = result.get("final_output", {}).get("result", {}).get("final_summary", "N/A")
        print(f"\n----- FINAL SUMMARY -----\n{final_summary}")
    else:
        print("\n----- WORKFLOW FAILED -----")
        print(f"Workflow Error: {result.get('workflow_error', 'N/A')}")
        print(f"Failed Task ID: {result.get('failed_task_id', 'N/A')}")
        # Optionally print full result dict for debugging
        # import pprint
        # print("\nFull Result Dict:")
        # pprint.pprint(result)

if __name__ == "__main__":
    main()

# --- Helper Functions for Testing ---
def attempt_json_recovery(json_str):
    """Attempts to recover malformed JSON."""
    try:
        # Basic recovery for common syntax errors
        fixed_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas in objects
        fixed_str = re.sub(r',\s*]', ']', fixed_str)  # Remove trailing commas in arrays
        fixed_str = re.sub(r'(?<=["{[:,])\s*\'', '"', fixed_str)  # Replace single quotes at start
        fixed_str = re.sub(r'\'\s*(?=["{[:,])', '"', fixed_str)  # Replace single quotes at end
        
        # Try to parse the fixed JSON
        return json.loads(fixed_str)
    except:
        return None

def validate_plan_with_llm(plan_str, user_request, tool_details=None, handler_details=None, system_message=None):
    """
    Attempt to validate/fix a plan using LLM.
    
    Args:
        plan_str: The JSON plan string to validate
        user_request: Original user request for context
        tool_details: Tool details to include in context (optional)
        handler_details: Handler details to include in context (optional)
        system_message: Optional system message for LLM
        
    Returns:
        Fixed plan as Python object, or None if failed
    """
    # Create service container and get LLM interface
    services = get_services()
    llm_interface = services.get_llm_interface()
    
    if not llm_interface:
        logger.error("No LLM interface available for plan validation.")
        return None
    
    # Set up the system message for the LLM
    if not system_message:
        system_message = "You are an AI assistant that helps with validating and fixing JSON plans for task workflows."
    
    # Prepare a prompt for the LLM to validate and fix the plan
    tool_context = json.dumps(tool_details) if tool_details else "[]"
    handler_context = json.dumps(handler_details) if handler_details else "[]"
    
    prompt = f"""
    I need you to validate and potentially fix this JSON plan for a workflow:
    
    {plan_str}
    
    The plan is for the user request: "{user_request}"
    
    Available tools: {tool_context}
    Available handlers: {handler_context}
    
    If the plan is valid, respond with:
    {{
      "valid": true,
      "errors": []
    }}
    
    If the plan has issues, respond with:
    {{
      "valid": false,
      "errors": ["Error 1", "Error 2", ...],
      "fixed_plan": [Fixed JSON plan array]
    }}
    
    Only respond with valid JSON. No explanation.
    """
    
    try:
        # Execute the LLM call
        llm_result = llm_interface.execute_llm_call(prompt, system_message=system_message)
        
        if not llm_result.get("success", False):
            logger.error(f"LLM validation call failed: {llm_result.get('error', 'Unknown error')}")
            return None
        
        # Parse the response
        llm_response = llm_result.get("response", "{}")
        validation_result = json.loads(llm_response)
        
        # Check if the plan is valid
        if validation_result.get("valid", False):
            # Return the original plan parsed as JSON
            return json.loads(plan_str)
        
        # Get the fixed plan if available
        fixed_plan = validation_result.get("fixed_plan")
        if fixed_plan:
            return fixed_plan
        
        logger.warning("LLM validation failed but no fixed plan was provided.")
        return None
        
    except Exception as e:
        logger.error(f"Error during LLM validation attempt: {e}")
        return None

def format_validation_errors_for_user(errors, warnings=None):
    """Format validation errors in a user-friendly way."""
    if not errors:
        return "No validation errors found."
    
    formatted = "The following issues were found in your plan:\n\n"
    for i, error in enumerate(errors):
        formatted += f"{i+1}. {error}\n"
    
    if warnings:
        formatted += "\nWarnings:\n"
        for i, warning in enumerate(warnings):
            formatted += f"{i+1}. {warning}\n"
            
    return formatted