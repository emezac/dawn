#!/usr/bin/env python3
"""
Script to fix and run the failing tests from test_chat_planner_handlers.py.

This script uses a different patching approach that works around the
'module has no attribute' issue by directly patching the function
rather than the module path.
"""  # noqa: D202

import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create mock ChatPlannerConfig functions instead of patching the imports
def mock_get_max_clarifications():
    return 3

# Mock the config module before importing the handler
sys.modules['examples.chat_planner_config'] = MagicMock()
sys.modules['examples.chat_planner_config'].ChatPlannerConfig = MagicMock()
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_planning_system_message.return_value = "You are a planning assistant."
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_tokens.return_value = 1500
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_llm_temperature.return_value = 0.7
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_prompt.return_value = "Create a plan for: {user_request}"
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_validation_strictness.return_value = "medium"
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.is_plan_validation_enabled.return_value = True
sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications.return_value = 3

# Import the handlers to test after mocking
from examples.chat_planner_workflow import (
    plan_user_request_handler,
    validate_plan_handler,
    plan_to_tasks_handler
)
from core.task import DirectHandlerTask
from core.llm.interface import LLMInterface
from core.services import get_services, reset_services
from core.config import configure, set as config_set, get as config_get

# Example valid plan for testing
VALID_PLAN_JSON = """
[
  {
    "step_id": "step_1_search",
    "description": "Search for information about AI",
    "type": "tool",
    "name": "web_search",
    "inputs": {
      "query": "latest AI research"
    },
    "outputs": ["search_results"],
    "depends_on": []
  },
  {
    "step_id": "step_2_summarize",
    "description": "Summarize the search results",
    "type": "handler",
    "name": "text_summarizer",
    "inputs": {
      "text": "${step_1_search.output.result}"
    },
    "outputs": ["summary"],
    "depends_on": ["step_1_search"]
  }
]
"""

class TestChatPlannerHandlers(unittest.TestCase):
    """Test the Chat Planner workflow handlers using direct patching."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Reset services before each test
        reset_services()
        services = get_services()

        # Create mock LLM interface
        self.mock_llm_interface = MagicMock(spec=LLMInterface)
        services.register_llm_interface(self.mock_llm_interface)

        # Create mock task for passing to handlers
        self.mock_task = MagicMock(spec=DirectHandlerTask)
        self.mock_task.id = "test_task_id"
        self.mock_task.name = "Test Task"

        # Configure for testing environment
        try:
            configure(config_paths=["config/testing.json"])
        except:
            pass  # Ignore if config file doesn't exist
            
        # Sample tool and handler details for validation
        self.tool_details = [
            {"name": "web_search", "description": "Search the web for information"},
            {"name": "file_read", "description": "Read the contents of a file"}
        ]
        self.handler_details = [
            {"name": "text_summarizer", "description": "Summarize text content"},
            {"name": "extract_entities", "description": "Extract entities from text"}
        ]

    # Instead of using @patch decorator, we'll manually patch in each test function
    def test_plan_user_request_handler_success(self):
        """Test successful execution of plan_user_request_handler."""
        # Setup mock LLM response
        self.mock_llm_interface.execute_llm_call.return_value = {
            "success": True,
            "response": VALID_PLAN_JSON
        }

        # Directly mock the get_max_clarifications function using monkeypatch
        original_func = sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications
        sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = mock_get_max_clarifications

        try:
            # Execute handler
            result = plan_user_request_handler(
                self.mock_task,
                {
                    "user_request": "Find the latest AI research and summarize it",
                    "available_tools_context": json.dumps(self.tool_details),
                    "available_handlers_context": json.dumps(self.handler_details),
                    "skip_ambiguity_check": True  # Skip ambiguity check to ensure only one LLM call
                }
            )

            # Verify result
            self.assertTrue(result["success"])
            self.assertEqual(result["result"]["needs_clarification"], False)
            self.assertEqual(result["result"]["raw_llm_output"], VALID_PLAN_JSON)
            
            # Verify LLM was called correctly
            self.mock_llm_interface.execute_llm_call.assert_called_once()
        finally:
            # Restore original function
            sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = original_func

    def test_plan_user_request_handler_ambiguity_detection(self):
        """Test plan_user_request_handler when ambiguity is detected."""
        # Setup mock LLM responses for ambiguity check
        ambiguity_response = {
            "success": True,
            "response": '{"needs_clarification": true, "ambiguity_details": [{"aspect": "scope", "description": "Scope is unclear", "clarification_question": "What timeframe?"}]}'
        }
        self.mock_llm_interface.execute_llm_call.return_value = ambiguity_response

        # Directly mock the get_max_clarifications function using monkeypatch
        original_func = sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications
        sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = mock_get_max_clarifications

        try:
            # Execute handler
            result = plan_user_request_handler(
                self.mock_task,
                {
                    "user_request": "Find some AI research",
                    "available_tools_context": json.dumps(self.tool_details),
                    "available_handlers_context": json.dumps(self.handler_details),
                    "clarification_count": 0
                }
            )

            # Verify result indicates need for clarification
            self.assertTrue(result["success"])
            self.assertTrue(result["result"]["needs_clarification"])
            self.assertEqual(len(result["result"]["ambiguity_details"]), 1)
            self.assertEqual(result["result"]["ambiguity_details"][0]["aspect"], "scope")
        finally:
            # Restore original function
            sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = original_func

    def test_plan_user_request_handler_llm_failure(self):
        """Test plan_user_request_handler when LLM call fails."""
        # Setup mock LLM to simulate failure
        self.mock_llm_interface.execute_llm_call.return_value = {
            "success": False,
            "error": "LLM API error"
        }

        # Directly mock the get_max_clarifications function using monkeypatch
        original_func = sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications
        sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = mock_get_max_clarifications

        try:
            # Execute handler
            result = plan_user_request_handler(
                self.mock_task,
                {
                    "user_request": "Find the latest AI research and summarize it",
                    "available_tools_context": json.dumps(self.tool_details),
                    "available_handlers_context": json.dumps(self.handler_details)
                }
            )

            # Verify handler reports error
            self.assertFalse(result["success"])
            self.assertIn("Plan generation failed", result["error"])
        finally:
            # Restore original function
            sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = original_func


if __name__ == "__main__":
    unittest.main() 