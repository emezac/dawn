#!/usr/bin/env python3
"""
Unit tests for the Chat Planner workflow handlers and tasks.

These tests validate the core functionality of the handlers used in the
Chat Planner workflow, including plan generation, validation, and
conversion to executable tasks.
"""  # noqa: D202

import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch, ANY

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

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

# Import the handlers to test
from examples.chat_planner_workflow import (
    plan_user_request_handler,
    validate_plan_handler,
    plan_to_tasks_handler
)
# Import other needed modules
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

# JSON with schema errors
INVALID_SCHEMA_PLAN_JSON = """
[
  {
    "step_id": "step_1_search",
    "description": "Search for information",
    "type": "invalid_type", 
    "name": "web_search",
    "inputs": {
      "query": "test query"
    },
    "depends_on": []
  }
]
"""

# Malformed JSON for testing error recovery
MALFORMED_JSON = """
[
  {
    "step_id": "step_1_search",
    "description": "Search for information",
    "type": "tool" 
    "name": "web_search",
    "inputs": {
      "query": "test query"
    },
    "depends_on": []
  }
]
"""


class TestChatPlannerHandlers(unittest.TestCase):
    """Test the Chat Planner workflow handlers."""  # noqa: D202

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
        configure(config_paths=["config/testing.json"])
        # Ensure the chat planner config has test values
        config_set("chat_planner.llm_model", "mock-llm")
        config_set("chat_planner.enable_plan_validation", True)
        
        # Sample tool and handler details for validation
        self.tool_details = [
            {"name": "web_search", "description": "Search the web for information"},
            {"name": "file_read", "description": "Read the contents of a file"}
        ]
        self.handler_details = [
            {"name": "text_summarizer", "description": "Summarize text content"},
            {"name": "extract_entities", "description": "Extract entities from text"}
        ]

    def test_plan_user_request_handler_success(self):
        """Test successful execution of plan_user_request_handler."""
        # Directly mock the get_max_clarifications function using monkeypatch
        original_func = sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications
        sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = mock_get_max_clarifications

        try:
            # Setup mock LLM response
            self.mock_llm_interface.execute_llm_call.return_value = {
                "success": True,
                "response": VALID_PLAN_JSON
            }

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

    def test_plan_user_request_handler_missing_request(self):
        """Test plan_user_request_handler with missing user_request."""
        # Execute handler with empty input
        result = plan_user_request_handler(self.mock_task, {})

        # Verify result
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Missing user_request input.")
        
        # Verify LLM was not called
        self.mock_llm_interface.execute_llm_call.assert_not_called()

    def test_plan_user_request_handler_ambiguity_detection(self):
        """Test plan_user_request_handler when ambiguity is detected."""
        # Directly mock the get_max_clarifications function using monkeypatch
        original_func = sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications
        sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = mock_get_max_clarifications

        try:
            # Setup mock LLM responses - first for ambiguity check, then for plan
            ambiguity_response = {
                "success": True,
                "response": '{"needs_clarification": true, "ambiguity_details": [{"aspect": "scope", "description": "Scope is unclear", "clarification_question": "What timeframe?"}]}'
            }
            self.mock_llm_interface.execute_llm_call.return_value = ambiguity_response

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
        # Directly mock the get_max_clarifications function using monkeypatch
        original_func = sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications
        sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = mock_get_max_clarifications

        try:
            # Setup mock LLM to simulate failure
            self.mock_llm_interface.execute_llm_call.return_value = {
                "success": False,
                "error": "LLM API error"
            }

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

    def test_validate_plan_handler_success(self):
        """Test successful validation of a valid plan."""
        # Execute handler with valid plan
        result = validate_plan_handler(
            self.mock_task,
            {
                "raw_llm_output": VALID_PLAN_JSON,
                "tool_details": self.tool_details,
                "handler_details": self.handler_details,
                "user_request": "Find the latest AI research and summarize it"
            }
        )

        # Verify result
        self.assertTrue(result["success"])
        self.assertIn("validated_plan", result["result"])
        self.assertEqual(len(result["result"]["validated_plan"]), 2)
        
        # Check that specific steps were preserved
        self.assertEqual(result["result"]["validated_plan"][0]["step_id"], "step_1_search")
        self.assertEqual(result["result"]["validated_plan"][1]["step_id"], "step_2_summarize")

    def test_validate_plan_handler_schema_error(self):
        """Test validate_plan_handler with a plan that has schema errors."""
        # Execute handler with invalid schema plan
        result = validate_plan_handler(
            self.mock_task,
            {
                "raw_llm_output": INVALID_SCHEMA_PLAN_JSON,
                "tool_details": self.tool_details,
                "handler_details": self.handler_details,
                "user_request": "Find information"
            }
        )

        # Verify validation failed with appropriate errors
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
    def test_validate_plan_handler_nested_json(self):
        """Test validate_plan_handler with a plan nested in a JSON object."""
        # Create a nested JSON structure where the plan is inside an object
        nested_json = {
            "needs_clarification": False,
            "ambiguity_details": [],
            "raw_llm_output": json.loads(VALID_PLAN_JSON)
        }
        
        # Execute handler with nested structure
        result = validate_plan_handler(
            self.mock_task,
            {
                "raw_llm_output": nested_json,
                "tool_details": self.tool_details,
                "handler_details": self.handler_details,
                "user_request": "Find the latest AI research and summarize it"
            }
        )
        
        # Verify result - should successfully extract and validate the plan
        self.assertTrue(result["success"], "Failed to validate nested plan structure")
        self.assertIn("validated_plan", result["result"])
        self.assertEqual(len(result["result"]["validated_plan"]), 2, "Plan should have 2 steps")
        self.assertEqual(result["result"]["validated_plan"][0]["step_id"], "step_1_search")
        self.assertEqual(result["result"]["validated_plan"][1]["step_id"], "step_2_summarize")
        
    def test_validate_plan_handler_nested_string(self):
        """Test validate_plan_handler with a plan nested in a JSON string."""
        # Create a nested JSON string where the plan is inside an object
        nested_json_str = json.dumps({
            "needs_clarification": False,
            "plan": json.loads(VALID_PLAN_JSON)
        })
        
        # Execute handler with nested string structure
        result = validate_plan_handler(
            self.mock_task,
            {
                "raw_llm_output": nested_json_str,
                "tool_details": self.tool_details,
                "handler_details": self.handler_details,
                "user_request": "Find the latest AI research and summarize it"
            }
        )
        
        # Verify result - should successfully extract and validate the plan
        self.assertTrue(result["success"], "Failed to validate nested plan in string")
        self.assertIn("validated_plan", result["result"])
        self.assertEqual(len(result["result"]["validated_plan"]), 2, "Plan should have 2 steps")
        self.assertEqual(result["result"]["validated_plan"][0]["step_id"], "step_1_search")
        self.assertEqual(result["result"]["validated_plan"][1]["step_id"], "step_2_summarize")

    def test_validate_plan_handler_json_error(self):
        """Test validate_plan_handler with malformed JSON."""
        # Execute handler with malformed JSON
        result = validate_plan_handler(
            self.mock_task,
            {
                "raw_llm_output": MALFORMED_JSON,
                "tool_details": self.tool_details,
                "handler_details": self.handler_details,
                "user_request": "Find information"
            }
        )

        # Verify result
        # This could either fail with JSON error or succeed with recovery depending on implementation
        if result["success"]:
            # If JSON recovery is successful
            self.assertIn("validated_plan", result["result"])
            self.assertIn("validation_warnings", result["result"])
            self.assertTrue(any("recovery" in str(warning).lower() for warning in result["result"]["validation_warnings"]))
        else:
            # If JSON recovery fails
            self.assertIn("error", result)
            self.assertIn("JSON", result["error"])

    def test_validate_plan_handler_missing_input(self):
        """Test validate_plan_handler with missing input."""
        # Execute with missing raw_llm_output
        result = validate_plan_handler(
            self.mock_task,
            {"tool_details": self.tool_details, "handler_details": self.handler_details}
        )
        
        # Verify error
        self.assertFalse(result["success"])
        self.assertIn("Missing or invalid raw plan input", result["error"])

    def test_validate_plan_handler_capability_check(self):
        """Test validate_plan_handler's check for unavailable tools/handlers."""
        # Set medium strictness for this test
        original_strictness = config_get("chat_planner.validation_strictness", "high")
        self.addCleanup(config_set, "chat_planner.validation_strictness", original_strictness)
        config_set("chat_planner.validation_strictness", "medium")
        
        # Create a plan that references a tool that isn't available
        plan_with_unavailable_tool = [
            {
                "step_id": "step_1",
                "description": "Use unavailable tool",
                "type": "tool",
                "name": "nonexistent_tool",
                "inputs": {},
                "depends_on": []  # Added the required depends_on field
            }
        ]
        plan_str = json.dumps(plan_with_unavailable_tool)
        
        # Execute handler
        result = validate_plan_handler(
            self.mock_task,
            {
                "raw_llm_output": plan_str,
                "tool_details": [{"name": "web_search"}],  # Not including nonexistent_tool
                "handler_details": []
            }
        )
        
        # Verify success but with warnings
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["result"]["validated_plan"])
        
        # Check there are warnings
        warnings = result["result"].get("validation_warnings", [])
        self.assertTrue(any("nonexistent_tool" in str(w) for w in warnings))

    def test_plan_to_tasks_handler_success(self):
        """Test successful conversion of a plan to task definitions."""
        # Parse the valid plan JSON for input
        validated_plan = json.loads(VALID_PLAN_JSON)
        
        # Execute handler
        result = plan_to_tasks_handler(
            self.mock_task,
            {"validated_plan": validated_plan}
        )

        # Verify result
        self.assertTrue(result["success"])
        self.assertIn("tasks", result["result"])
        self.assertEqual(len(result["result"]["tasks"]), 2)
        
        # Check task definitions
        tasks = result["result"]["tasks"]
        self.assertEqual(tasks[0]["task_id"], "step_1_search")
        self.assertEqual(tasks[0]["tool_name"], "web_search")
        self.assertEqual(tasks[1]["task_id"], "step_2_summarize")
        self.assertEqual(tasks[1]["handler_name"], "text_summarizer")
        self.assertEqual(tasks[1]["task_class"], "DirectHandlerTask")
        
        # Check dependencies
        self.assertEqual(tasks[0]["depends_on"], [])
        self.assertEqual(tasks[1]["depends_on"], ["step_1_search"])

    def test_plan_to_tasks_handler_invalid_input(self):
        """Test plan_to_tasks_handler with invalid input."""
        # Test with non-list input
        result = plan_to_tasks_handler(
            self.mock_task,
            {"validated_plan": "not a list"}
        )
        
        # Verify error
        self.assertFalse(result["success"])
        self.assertIn("not a list", result["error"])

    def test_plan_to_tasks_handler_empty_plan(self):
        """Test plan_to_tasks_handler with empty plan."""
        # Execute handler with empty list
        result = plan_to_tasks_handler(
            self.mock_task,
            {"validated_plan": []}
        )
        
        # Verify error
        self.assertFalse(result["success"])
        self.assertIn("No tasks to execute", result["error"])

    def test_plan_to_tasks_handler_missing_fields(self):
        """Test plan_to_tasks_handler with steps missing required fields."""
        # Create a plan with incomplete steps
        incomplete_plan = [
            {
                "step_id": "step_1",
                "description": "Missing type and name"
                # Missing type and name
            },
            {
                "step_id": "step_2",
                "type": "tool",
                # Missing name
                "description": "Missing name"
            }
        ]
        
        # Execute handler
        result = plan_to_tasks_handler(
            self.mock_task,
            {"validated_plan": incomplete_plan}
        )
        
        # Verify that the handler succeeds but with warnings
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["result"]["tasks"]), 0)
        self.assertTrue(len(result["result"]["conversion_warnings"]) > 0)
        # Verify warnings contain expected messages
        warnings = result["result"]["conversion_warnings"]
        self.assertTrue(any("missing required fields" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main() 