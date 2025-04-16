#!/usr/bin/env python3
"""
Simple test script for testing the plan_user_request_handler function.
"""  # noqa: D202

import sys
import os
import json
from unittest.mock import MagicMock

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock the ChatPlannerConfig
sys.modules['examples.chat_planner_config'] = MagicMock()
sys.modules['examples.chat_planner_config'].ChatPlannerConfig = MagicMock()
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_planning_system_message.return_value = "You are a planning assistant."
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_tokens.return_value = 1500
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_llm_temperature.return_value = 0.7
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_prompt.return_value = "Create a plan for: {user_request}"
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_validation_strictness.return_value = "medium"
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.is_plan_validation_enabled.return_value = True
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications.return_value = 3

# Import the handler
from examples.chat_planner_workflow import plan_user_request_handler
from core.task import DirectHandlerTask
from core.llm.interface import LLMInterface
from core.services import get_services, reset_services

def test_plan_user_request_handler():
    """Test the plan_user_request_handler function."""
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

    # Create mock task
    mock_task = MagicMock(spec=DirectHandlerTask)
    mock_task.id = "test_task"
    mock_task.name = "Test Task"

    # Sample tool and handler details
    tool_details = [
        {"name": "test_tool", "description": "Test tool"}
    ]
    handler_details = [
        {"name": "test_handler", "description": "Test handler"}
    ]

    # Call the handler
    result = plan_user_request_handler(
        mock_task,
        {
            "user_request": "Test request",
            "available_tools_context": json.dumps(tool_details),
            "available_handlers_context": json.dumps(handler_details),
            "skip_ambiguity_check": True
        }
    )

    # Check result
    if result.get("success"):
        print("Test passed!")
        print(f"Result: {result}")
    else:
        print("Test failed!")
        print(f"Error: {result.get('error')}")
        print(f"Result: {result}")

if __name__ == "__main__":
    test_plan_user_request_handler() 