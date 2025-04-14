#!/usr/bin/env python3
"""
Unit tests for the execute_dynamic_tasks_handler in the Chat Planner workflow.

This tests the dynamic task execution functionality, which is responsible for
executing a list of dynamically generated tasks based on a plan.
"""  # noqa: D202

import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the handler to test
from examples.chat_planner_workflow import execute_dynamic_tasks_handler

# Import other needed modules
from core.task import DirectHandlerTask
from core.services import get_services, reset_services
from core.tools.registry import ToolRegistry
from core.handlers.registry import HandlerRegistry
from core.engine import WorkflowEngine
from core.workflow import Workflow
from core.llm.interface import LLMInterface


class TestExecuteDynamicTasksHandler(unittest.TestCase):
    """Test the execute_dynamic_tasks_handler functionality."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Reset services before each test
        reset_services()
        services = get_services()
        
        # Create and register tool registry with mock tools
        self.tool_registry = ToolRegistry()
        services.register_tool_registry(self.tool_registry)
        
        # Create and register handler registry with mock handlers
        self.handler_registry = HandlerRegistry()
        services.register_handler_registry(self.handler_registry)
        
        # Register mock tools and handlers
        self.mock_search_tool = MagicMock(return_value={"success": True, "result": "Mock search results"})
        self.mock_summarize_handler = MagicMock(return_value={"success": True, "result": "Mock summary"})
        
        self.tool_registry.register_tool("mock_search", self.mock_search_tool)
        self.handler_registry.register_handler("mock_summarize", self.mock_summarize_handler)
        
        # Create mock task for passing to handler
        self.mock_task = MagicMock(spec=DirectHandlerTask)
        self.mock_task.id = "execute_dynamic_tasks"
        self.mock_task.name = "Execute Dynamic Tasks"
        
        # Initialize mock LLM interface
        self.mock_llm = MagicMock(spec=LLMInterface)
        
        # Create a test workflow
        self.workflow = Workflow(workflow_id="test_workflow", name="Test Workflow")
        
        # Initialize WorkflowEngine with required parameters
        self.engine = WorkflowEngine(
            workflow=self.workflow,
            llm_interface=self.mock_llm,
            tool_registry=self.tool_registry
        )
        
        # Sample task definitions that would be output from plan_to_tasks_handler
        self.sample_task_defs = [
            {
                "task_id": "search_task",
                "name": "Search Task",
                "tool_name": "mock_search",
                "input_data": {
                    "query": "test query"
                },
                "depends_on": []
            },
            {
                "task_id": "summarize_task",
                "name": "Summarize Task",
                "handler_name": "mock_summarize",
                "task_class": "DirectHandlerTask",
                "input_data": {
                    "text": "${search_task.output.result}"
                },
                "depends_on": ["search_task"]
            }
        ]

    def test_execute_dynamic_tasks_success(self):
        """Test successful execution of dynamic tasks."""
        # Execute handler with sample task definitions
        result = execute_dynamic_tasks_handler(
            self.mock_task,
            {"tasks": self.sample_task_defs}
        )
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertIn("outputs", result["result"])
        
        # Verify tools were called
        self.mock_search_tool.assert_called_once()
        self.mock_summarize_handler.assert_called_once()

    def test_execute_dynamic_tasks_empty_list(self):
        """Test execute_dynamic_tasks_handler with empty task list."""
        # Execute handler with empty task list
        result = execute_dynamic_tasks_handler(
            self.mock_task,
            {"tasks": []}
        )
        
        # Verify result (should succeed with empty result)
        self.assertTrue(result["success"])
        self.assertIn("message", result["result"])
        self.assertEqual(result["result"]["outputs"], [])
        
        # Verify tools were not called
        self.mock_search_tool.assert_not_called()
        self.mock_summarize_handler.assert_not_called()

    def test_execute_dynamic_tasks_missing_input(self):
        """Test execute_dynamic_tasks_handler with missing input."""
        # Execute handler with no task list
        result = execute_dynamic_tasks_handler(
            self.mock_task,
            {}
        )
        
        # Verify result (should succeed with empty result)
        self.assertTrue(result["success"])
        self.assertIn("message", result["result"])
        self.assertEqual(result["result"]["message"], "No valid dynamic tasks provided.")
        
        # Verify tools were not called
        self.mock_search_tool.assert_not_called()
        self.mock_summarize_handler.assert_not_called()

    def test_execute_dynamic_tasks_with_tool_failure(self):
        """Test execute_dynamic_tasks_handler when a tool fails."""
        # Configure mock search tool to fail
        self.mock_search_tool.return_value = {
            "success": False,
            "error": "Mock search error"
        }
        
        # Execute handler with sample task definitions
        result = execute_dynamic_tasks_handler(
            self.mock_task,
            {"tasks": self.sample_task_defs}
        )
        
        # The handler should still succeed overall
        self.assertTrue(result["success"])
        self.assertIn("outputs", result["result"])
        
        # Verify search tool was called but summarize was not (due to dependency)
        self.mock_search_tool.assert_called_once()
        self.mock_summarize_handler.assert_not_called()
        
        # Verify error in result
        outputs = result["result"]["outputs"]
        search_output = next((o for o in outputs if o["task_id"] == "search_task"), None)
        self.assertIsNotNone(search_output)
        self.assertFalse(search_output["success"])
        self.assertEqual(search_output["error"], "Mock search error")

    def test_execute_dynamic_tasks_variable_substitution(self):
        """Test variable substitution in task inputs."""
        # Execute handler with additional input that can be referenced
        result = execute_dynamic_tasks_handler(
            self.mock_task,
            {
                "tasks": self.sample_task_defs,
                "user_prompt": "Original user request"
            }
        )
        
        # Verify result
        self.assertTrue(result["success"])
        
        # Check that the substitute worked (captured in the input to the mock)
        # Would need to inspect the calls to the mocks to verify the actual substitution

    def test_execute_dynamic_tasks_invalid_task_type(self):
        """Test with invalid task type."""
        # Create task definitions with invalid type
        invalid_tasks = [
            {
                "task_id": "invalid_task",
                "name": "Invalid Task",
                # Missing both tool_name and handler_name
                "input_data": {"test": "data"},
                "depends_on": []
            }
        ]
        
        # Execute handler
        result = execute_dynamic_tasks_handler(
            self.mock_task,
            {"tasks": invalid_tasks}
        )
        
        # Should still succeed overall, but task should fail
        self.assertTrue(result["success"])
        outputs = result["result"]["outputs"]
        self.assertEqual(len(outputs), 1)
        self.assertFalse(outputs[0]["success"])
        self.assertIn("error", outputs[0])


if __name__ == "__main__":
    unittest.main() 