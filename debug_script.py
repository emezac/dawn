#!/usr/bin/env python3
"""
Debug script for the plan_user_request_handler function.
"""  # noqa: D202

import sys
import os
import json
import logging
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug_script")

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock the ChatPlannerConfig
mock_config = MagicMock()
mock_config.get_planning_system_message.return_value = "You are a planning assistant."
mock_config.get_max_tokens.return_value = 1500
mock_config.get_llm_temperature.return_value = 0.7
mock_config.get_prompt.return_value = "Create a plan for: {user_request}"
mock_config.get_validation_strictness.return_value = "medium"
mock_config.is_plan_validation_enabled.return_value = True
mock_config.get_max_clarifications.return_value = 3

# Create the mock module
sys.modules['examples.chat_planner_config'] = MagicMock()
sys.modules['examples.chat_planner_config'].ChatPlannerConfig = mock_config

# Now import the handler
try:
    from examples.chat_planner_workflow import plan_user_request_handler
    from core.task import DirectHandlerTask
    from core.llm.interface import LLMInterface
    from core.services import get_services, reset_services
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def debug_plan_user_request_handler():
    """Debug the plan_user_request_handler function."""
    logger.info("Starting debug test...")
    
    # Reset services
    reset_services()
    services = get_services()

    # Create mock LLM interface
    mock_llm_interface = MagicMock(spec=LLMInterface)
    mock_llm_interface.execute_llm_call.return_value = {
        "success": True,
        "response": """[
            {
                "step_id": "step_1",
                "description": "Test step",
                "type": "tool",
                "name": "test_tool",
                "inputs": {"query": "test"},
                "outputs": ["result"],
                "depends_on": []
            }
        ]"""
    }
    services.register_llm_interface(mock_llm_interface)
    logger.info("Registered mock LLM interface")

    # Create mock task
    mock_task = MagicMock(spec=DirectHandlerTask)
    mock_task.id = "test_task"
    mock_task.name = "Test Task"
    logger.info("Created mock task")

    # Sample tool and handler details
    tool_details = [{"name": "test_tool", "description": "Test tool"}]
    handler_details = [{"name": "test_handler", "description": "Test handler"}]

    # Log max_clarifications mock setup
    logger.info(f"ChatPlannerConfig.get_max_clarifications() mock setup: {mock_config.get_max_clarifications.return_value}")
    
    # Call ChatPlannerConfig.get_max_clarifications() directly to check
    try:
        from examples.chat_planner_config import ChatPlannerConfig
        max_clarifications = ChatPlannerConfig.get_max_clarifications()
        logger.info(f"Direct call to get_max_clarifications() returned: {max_clarifications}")
    except Exception as e:
        logger.error(f"Error calling get_max_clarifications() directly: {e}")

    # Log input parameters
    input_data = {
        "user_request": "Test request",
        "available_tools_context": json.dumps(tool_details),
        "available_handlers_context": json.dumps(handler_details),
        "skip_ambiguity_check": True
    }
    logger.info(f"Input data: {input_data}")

    # Call the handler with try/except for better error logging
    try:
        logger.info("Calling plan_user_request_handler...")
        result = plan_user_request_handler(mock_task, input_data)
        logger.info(f"Handler execution completed. Result: {result}")
        
        if result.get("success"):
            logger.info("Test passed!")
        else:
            logger.error(f"Test failed! Error: {result.get('error')}")
    except Exception as e:
        logger.error(f"Exception during handler execution: {e}", exc_info=True)

if __name__ == "__main__":
    debug_plan_user_request_handler() 