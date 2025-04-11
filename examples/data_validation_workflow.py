"""
Data Validation Workflow Example.

This example demonstrates how to use Dawn's data validation capabilities
to create workflows with strong type checking and validation-based routing.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Union, TypedDict

# Add parent directory to path to import the framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from core.agent import Agent
from core.task import Task, DirectHandlerTask, TaskOutput
from core.workflow import Workflow
from core.utils.data_validator import (
    validate_type, 
    validate_data, 
    ValidationError, 
    format_validation_errors
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("data_validation_workflow")

# Load environment variables
load_dotenv()


# Define typed data structures for our example
class UserProfile(TypedDict):
    """TypedDict for user profile data."""
    name: str
    age: int
    email: str
    is_active: bool
    preferences: Dict[str, Any]


class ValidationResult(TypedDict):
    """TypedDict for validation result data."""
    valid: bool
    errors: List[str]
    data: Optional[Dict[str, Any]]


# Handlers for our workflow tasks
def validate_user_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user data against expected schema.
    
    Demonstrates typed data validation with detailed error reporting.
    """
    # Extract the user data to validate
    user_data = input_data.get("user_data", {})
    
    # Define validation schema
    schema = {
        "name": {"type": str, "required": True},
        "age": {"type": int, "required": True},
        "email": {"type": str, "required": True},
        "is_active": {"type": bool, "required": True},
        "preferences": {"type": dict, "required": False}
    }
    
    # Validate against schema
    validation_errors = validate_data(user_data, schema)
    
    # Custom business logic validation
    if "age" in user_data and isinstance(user_data["age"], int):
        if user_data["age"] < 18:
            validation_errors.append(
                ValidationError("User must be at least 18 years old", "age")
            )
            
    if "email" in user_data and isinstance(user_data["email"], str):
        if not "@" in user_data["email"]:
            validation_errors.append(
                ValidationError("Invalid email format", "email")
            )
    
    # Build result based on validation
    validation_result: ValidationResult = {
        "valid": len(validation_errors) == 0,
        "errors": [str(err) for err in validation_errors],
        "data": user_data if len(validation_errors) == 0 else None
    }
    
    return {
        "success": True,
        "result": validation_result
    }


def process_valid_user_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a valid user profile.
    
    This task runs only when validation succeeds.
    """
    # Get the validated user data
    user_data = input_data.get("user_data", {})
    
    # Process the valid user (e.g., create account, update database)
    result = {
        "user_id": "USR_" + user_data.get("name", "")[:3].upper() + str(user_data.get("age", 0)),
        "account_status": "active" if user_data.get("is_active", False) else "inactive",
        "email_verified": False,
        "message": f"User {user_data.get('name')} successfully processed"
    }
    
    return {
        "success": True,
        "result": result
    }


def handle_validation_errors_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle validation errors.
    
    This task runs only when validation fails.
    """
    # Get the validation errors
    errors = input_data.get("errors", [])
    user_data = input_data.get("user_data", {})
    
    # Format errors for user feedback
    error_messages = errors if isinstance(errors, list) else [str(errors)]
    
    # Prepare feedback response
    result = {
        "success": False,
        "field_errors": error_messages,
        "summary": f"Found {len(error_messages)} validation errors in user data",
        "user_data_received": user_data
    }
    
    return {
        "success": True,  # Task succeeded (even though validation failed)
        "result": result
    }


def generate_response_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final response combining data from previous tasks.
    
    Demonstrates combining data from multiple execution paths.
    """
    # Get inputs from different possible task chains
    valid_result = input_data.get("valid_result", None)
    error_result = input_data.get("error_result", None)
    is_valid = input_data.get("is_valid", False)
    
    # Generate appropriate response
    if is_valid:
        response = {
            "status": "success",
            "message": valid_result.get("message", "User processing completed"),
            "user_id": valid_result.get("user_id", ""),
            "next_steps": [
                "Verify email address",
                "Complete profile" if not valid_result.get("account_status") == "active" else "No action needed"
            ]
        }
    else:
        response = {
            "status": "error",
            "message": "User data validation failed",
            "errors": error_result.get("field_errors", []),
            "next_steps": [
                "Correct the invalid fields",
                "Resubmit the form"
            ]
        }
    
    return {
        "success": True,
        "result": {
            "response": response,
            "status_code": 200,
            "content_type": "application/json"
        }
    }


def main():
    """Run the data validation workflow example."""
    logger.info("Starting Data Validation Workflow Example")
    
    # Create an Agent
    agent = Agent(
        agent_id="data_validation_agent",
        name="Data Validation Agent"
    )
    
    # Create a workflow
    workflow = Workflow(
        workflow_id="data_validation_workflow",
        name="Data Validation Workflow"
    )
    
    # Valid user data for the example
    valid_user_data = {
        "name": "Alice Smith",
        "age": 32,
        "email": "alice@example.com",
        "is_active": True,
        "preferences": {
            "theme": "dark",
            "notifications": True
        }
    }
    
    # Invalid user data for the example
    invalid_user_data = {
        "name": "Bob",
        "age": "twenty five",  # Invalid type
        "email": "invalid-email",  # Invalid format
        "is_active": "yes"  # Invalid type
    }
    
    # Change this to demonstrate different validation outcomes
    USE_VALID_DATA = True  # Set to False to demonstrate validation errors
    
    # Task 1: Validate User Data
    task1 = DirectHandlerTask(
        task_id="validate_user_data",
        name="Validate User Data",
        handler=validate_user_data_handler,
        input_data={
            "user_data": valid_user_data if USE_VALID_DATA else invalid_user_data
        },
        validate_output=True  # Enable output validation
    )
    
    # Task 2A: Process Valid User (conditional execution)
    task2a = DirectHandlerTask(
        task_id="process_valid_user",
        name="Process Valid User",
        handler=process_valid_user_handler,
        input_data={
            "user_data": "${validate_user_data.output_data.data}"
        },
        validate_input=True  # Enable input validation
    )
    
    # Task 2B: Handle Validation Errors (conditional execution)
    task2b = DirectHandlerTask(
        task_id="handle_validation_errors",
        name="Handle Validation Errors",
        handler=handle_validation_errors_handler,
        input_data={
            "errors": "${validate_user_data.output_data.errors}",
            "user_data": valid_user_data if USE_VALID_DATA else invalid_user_data
        }
    )
    
    # Task 3: Generate Response (final task)
    task3 = DirectHandlerTask(
        task_id="generate_response",
        name="Generate Response",
        handler=generate_response_handler,
        input_data={
            "is_valid": "${validate_user_data.output_data.valid}",
            "valid_result": "${process_valid_user.output_data.result}",
            "error_result": "${handle_validation_errors.output_data.result}"
        }
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2a)
    workflow.add_task(task2b)
    workflow.add_task(task3)
    
    # Set up conditional task routing based on validation results
    task1.condition = None  # Always execute
    
    # Task 2A only executes if validation passes
    task2a.condition = "${validate_user_data.output_data.valid} == True"
    task2a.next_task_id_on_success = "generate_response"
    
    # Task 2B only executes if validation fails
    task2b.condition = "${validate_user_data.output_data.valid} == False"  
    task2b.next_task_id_on_success = "generate_response"
    
    # Set first task's next tasks based on validation outcome
    task1.next_task_id_on_success = None  # Will be determined by conditional tasks
    
    # Load workflow into agent
    agent.load_workflow(workflow)
    
    # Run the workflow
    logger.info("Executing workflow")
    result = agent.run()
    
    # Print the final results
    logger.info("\n=== WORKFLOW RESULTS ===")
    logger.info(f"Workflow Status: {result['status']}")
    
    # Print task outputs
    logger.info("\n=== TASK OUTPUTS ===")
    for task_id, task in workflow.tasks.items():
        task_data = task.to_dict()
        logger.info(f"\n{task_data['name']} (ID: {task_id}):")
        logger.info(f"Status: {task_data['status']}")
        
        if task_data["status"] == "completed":
            if task_id == "generate_response":
                response = task.get_output_value("response")
                logger.info("\nFinal Response:")
                logger.info(f"Status: {response.get('status')}")
                logger.info(f"Message: {response.get('message')}")
                if response.get('status') == "error":
                    logger.info(f"Errors: {response.get('errors')}")
                else:
                    logger.info(f"User ID: {response.get('user_id')}")
                logger.info(f"Next Steps: {', '.join(response.get('next_steps', []))}")
        elif task_data["status"] == "skipped":
            logger.info("Task was skipped due to condition evaluation")
        elif task_data["status"] == "failed":
            logger.error(f"Error: {task_data['output_data'].get('error', 'Unknown error')}")
    
    logger.info("\nExample completed!")


if __name__ == "__main__":
    main() 