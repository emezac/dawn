#!/usr/bin/env python
"""
Error Handling Workflow Example.

This example demonstrates a workflow with error handling and propagation
between tasks, showing different error recovery strategies.
"""  # noqa: D202

import os
import sys
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Dawn framework components
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.engine import WorkflowEngine
from core.tools.registry import ToolRegistry
from core.services import get_services
from core.llm.interface import LLMInterface
from core.errors import ErrorCode, create_error_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("error_handling_workflow")

def print_box(title, content):
    """Print information in a nice box format."""
    width = 80
    print("\n" + "=" * width)
    print(f" {title} ".center(width, "="))
    print("=" * width)
    for line in content.split("\n"):
        print(f"| {line:<{width-4}} |")
    print("=" * width + "\n")

# ------- Custom Tool Handlers -------

def data_validator_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input data and return success or error.
    
    This handler deliberately fails with a validation error when 
    the 'simulate_error' field is set to True.
    """
    logger.info(f"Validating data: {input_data}")
    
    # Check if we should simulate an error
    if input_data.get("simulate_error", False):
        logger.info("Simulating validation error")
        return create_error_response(
            message="Validation failed: Invalid email format",
            error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
            details={
                "field_name": "email",
                "expected_format": "valid email address",
                "received_value": "invalid@example",
                "is_recoverable": True
            }
        )
    
    # Success case
    return {
        "success": True,
        "result": {
            "is_valid": True,
            "validated_data": input_data.get("data", {})
        }
    }

def data_processor_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process data and return success or error.
    
    This handler deliberately fails with an execution error when
    the 'simulate_error' field is set to True.
    """
    logger.info(f"Processing data: {input_data}")
    
    # Check if we should simulate an error
    if input_data.get("simulate_error", False):
        logger.info("Simulating processing error")
        return create_error_response(
            message="Data processing failed: Connection timeout",
            error_code=ErrorCode.EXECUTION_TIMEOUT,
            details={
                "component": "database",
                "operation": "insert",
                "is_retryable": True,
                "retry_after": 5
            }
        )
    
    # Success case
    data = input_data.get("data", {})
    return {
        "success": True,
        "result": {
            "processed_data": {
                "id": 123,
                "processed_at": "2023-05-15T10:30:00Z",
                "data": data
            }
        }
    }

def error_recovery_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempt to recover from an error based on the error details.
    
    This handler demonstrates how to access and use error information
    from a previous task.
    """
    logger.info(f"Attempting to recover from error: {input_data}")
    
    error_message = input_data.get("error_message", "Unknown error")
    error_code = input_data.get("error_code", "UNKNOWN_ERROR")
    error_details = input_data.get("error_details", {})
    
    # Log the error information we received
    logger.info(f"Error message: {error_message}")
    logger.info(f"Error code: {error_code}")
    logger.info(f"Error details: {error_details}")
    
    # Check if it's a validation error
    if error_code.startswith("VALIDATION"):
        field_name = error_details.get("field_name")
        if field_name == "email":
            # Fix the email format
            logger.info(f"Fixing email format")
            fixed_data = input_data.get("original_data", {}).copy()
            fixed_data["email"] = "corrected@example.com"
            
            return {
                "success": True,
                "result": {
                    "fixed_data": fixed_data,
                    "field_fixed": field_name,
                    "recovery_action": "field_correction"
                }
            }
    
    # Check if it's a timeout error
    elif error_code == ErrorCode.EXECUTION_TIMEOUT:
        if error_details.get("is_retryable", False):
            retry_after = error_details.get("retry_after", 0)
            logger.info(f"Error is retryable, suggesting retry after {retry_after} seconds")
            
            return {
                "success": True,
                "result": {
                    "recovery_action": "retry",
                    "retry_after": retry_after,
                    "original_data": input_data.get("original_data", {})
                }
            }
    
    # If we can't recover, return an error
    logger.info("Unable to recover from the error")
    return create_error_response(
        message=f"Unable to recover from error: {error_message}",
        error_code=ErrorCode.RECOVERY_FAILED,
        details={
            "original_error_code": error_code,
            "recovery_attempted": True,
            "recovery_strategy": "auto_recovery"
        }
    )

def notification_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send a notification about the workflow status."""
    message = input_data.get("message", "No message provided")
    logger.info(f"Sending notification: {message}")
    
    return {
        "success": True,
        "result": {
            "notification_sent": True,
            "message": message,
            "timestamp": "2023-05-15T10:35:00Z"
        }
    }

# ------- Main Functions -------

def build_error_handling_workflow(simulate_validation_error=True, simulate_processing_error=False):
    """
    Build a workflow that demonstrates error handling and propagation.
    
    Args:
        simulate_validation_error: If True, the validation task will fail
        simulate_processing_error: If True, the processing task will fail
        
    Returns:
        A Workflow instance
    """
    # Create a new workflow
    workflow = Workflow("error_handling_demo", "Error Handling Demonstration Workflow")
    
    # Initial input data
    input_data = {
        "user_id": 123,
        "email": "invalid@example",
        "name": "Test User",
        "subscription": "premium"
    }
    
    # Task 1: Validate user data
    validation_task = DirectHandlerTask(
        task_id="validate_user_data",
        name="Validate User Data",
        handler=data_validator_handler,
        input_data={
            "data": input_data,
            "validate_fields": ["email", "user_id"],
            "simulate_error": simulate_validation_error
        },
        next_task_id_on_success="process_user_data",
        next_task_id_on_failure="handle_validation_error"
    )
    
    # Task 2: Process user data (only executes if validation succeeds)
    processing_task = DirectHandlerTask(
        task_id="process_user_data",
        name="Process User Data", 
        handler=data_processor_handler,
        input_data={
            "data": "${validate_user_data.result.validated_data}",
            "operation": "create_user",
            "simulate_error": simulate_processing_error
        },
        next_task_id_on_success="send_success_notification",
        next_task_id_on_failure="handle_processing_error"
    )
    
    # Task 3A: Handle validation errors
    validation_error_handler = DirectHandlerTask(
        task_id="handle_validation_error",
        name="Handle Validation Error",
        handler=error_recovery_handler,
        input_data={
            "error_message": "${error.validate_user_data}",
            "error_code": "${error.validate_user_data.error_code}",
            "error_details": "${error.validate_user_data.error_details}",
            "original_data": input_data
        },
        next_task_id_on_success="retry_with_fixed_data",
        next_task_id_on_failure="send_failure_notification"
    )
    
    # Task 3B: Handle processing errors
    processing_error_handler = DirectHandlerTask(
        task_id="handle_processing_error",
        name="Handle Processing Error",
        handler=error_recovery_handler,
        input_data={
            "error_message": "${error.process_user_data}",
            "error_code": "${error.process_user_data.error_code}",
            "error_details": "${error.process_user_data.error_details}",
            "original_data": "${validate_user_data.result.validated_data}"
        },
        next_task_id_on_success="retry_after_error",
        next_task_id_on_failure="send_failure_notification"
    )
    
    # Task 4A: Retry with fixed data (after validation error)
    retry_task = DirectHandlerTask(
        task_id="retry_with_fixed_data",
        name="Retry With Fixed Data",
        handler=data_processor_handler,
        input_data={
            "data": "${handle_validation_error.result.fixed_data}",
            "operation": "create_user",
            "recovery_action": "${handle_validation_error.result.recovery_action}"
        },
        next_task_id_on_success="send_success_notification",
        next_task_id_on_failure="send_failure_notification"
    )
    
    # Task 4B: Retry after error (typically after timeout)
    retry_after_error = DirectHandlerTask(
        task_id="retry_after_error",
        name="Retry After Error Recovery",
        handler=data_processor_handler,
        input_data={
            "data": "${handle_processing_error.result.original_data}",
            "operation": "create_user",
            "recovery_action": "${handle_processing_error.result.recovery_action}"
        },
        next_task_id_on_success="send_success_notification",
        next_task_id_on_failure="send_failure_notification"
    )
    
    # Task 5A: Send success notification
    success_notification = DirectHandlerTask(
        task_id="send_success_notification",
        name="Send Success Notification",
        handler=notification_handler,
        input_data={
            "message": "User data processed successfully",
            "status": "success",
            "user_id": input_data["user_id"]
        }
    )
    
    # Task 5B: Send failure notification
    failure_notification = DirectHandlerTask(
        task_id="send_failure_notification",
        name="Send Failure Notification",
        handler=notification_handler,
        input_data={
            "message": "Failed to process user data",
            "status": "failure",
            "user_id": input_data["user_id"],
            "error": "${error.retry_with_fixed_data || error.retry_after_error || error.handle_validation_error || error.handle_processing_error}"
        }
    )
    
    # Add all tasks to the workflow
    workflow.add_task(validation_task)
    workflow.add_task(processing_task)
    workflow.add_task(validation_error_handler)
    workflow.add_task(processing_error_handler)
    workflow.add_task(retry_task)
    workflow.add_task(retry_after_error)
    workflow.add_task(success_notification)
    workflow.add_task(failure_notification)
    
    return workflow

def register_handlers(registry):
    """Register custom handlers with the tool registry."""
    registry.register_tool("data_validator", data_validator_handler)
    registry.register_tool("data_processor", data_processor_handler)
    registry.register_tool("error_recovery", error_recovery_handler)
    registry.register_tool("send_notification", notification_handler)

def main():
    """Run the error handling workflow examples."""
    # Get services
    services = get_services()
    tool_registry = services.tool_registry
    
    # Register our custom handlers
    register_handlers(tool_registry)
    
    # Create a simple LLM interface (not actually used in this example)
    llm_interface = LLMInterface(api_key=os.getenv("OPENAI_API_KEY", "dummy_key"))
    
    print_box("ERROR HANDLING WORKFLOW DEMO", "This example demonstrates error propagation between tasks")
    
    # Create workflows for different scenarios
    print_box("SCENARIO 1", "Validation Error → Recovery → Success")
    workflow1 = build_error_handling_workflow(
        simulate_validation_error=True,
        simulate_processing_error=False
    )
    engine1 = WorkflowEngine(workflow1, llm_interface, tool_registry, services)
    result1 = engine1.run()
    
    print_box("SCENARIO 2", "Validation Success → Processing Error → Recovery → Success")
    workflow2 = build_error_handling_workflow(
        simulate_validation_error=False,
        simulate_processing_error=True
    )
    engine2 = WorkflowEngine(workflow2, llm_interface, tool_registry, services)
    result2 = engine2.run()
    
    print_box("SCENARIO 3", "No Errors → Straight Success Path")
    workflow3 = build_error_handling_workflow(
        simulate_validation_error=False,
        simulate_processing_error=False
    )
    engine3 = WorkflowEngine(workflow3, llm_interface, tool_registry, services)
    result3 = engine3.run()
    
    # Print a summary of all scenario results
    print_box("RESULTS SUMMARY", "Summary of all workflow scenarios")
    print(f"Scenario 1 Status: {result1['status']}")
    print(f"Scenario 2 Status: {result2['status']}")
    print(f"Scenario 3 Status: {result3['status']}")
    
    # Check for error summaries
    if "error_summary" in result1 and result1["error_summary"] is not None:
        print(f"\nScenario 1 had {result1['error_summary']['error_count']} errors")
    if "error_summary" in result2 and result2["error_summary"] is not None:
        print(f"Scenario 2 had {result2['error_summary']['error_count']} errors")
    if "error_summary" in result3 and result3["error_summary"] is not None:
        print(f"Scenario 3 had {result3['error_summary']['error_count']} errors")
    else:
        print(f"Scenario 3 had 0 errors")
    
    print("\nDemo completed! This example demonstrated how errors can be propagated between tasks,")
    print("enabling sophisticated error handling and recovery strategies.")

if __name__ == "__main__":
    main() 