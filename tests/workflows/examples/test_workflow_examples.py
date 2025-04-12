"""
Test cases for the workflow examples.

This module contains test cases for the example workflows,
demonstrating how to use the testing utilities.
"""

import unittest
from unittest.mock import MagicMock
import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import the testing utilities
from core.utils.testing import (
    WorkflowTestHarness,
    TaskTestHarness,
    create_mock_tool_execution,
    workflow_test_context,
)

# Create a simple workflow for testing
def simple_workflow(input_data):
    """
    A simple workflow for testing.
    
    Args:
        input_data: Input data for the workflow
        
    Returns:
        Dict containing the workflow result
    """
    # This is a placeholder that would normally use tools
    result = {
        "success": True,
        "result": {
            "processed": input_data.get("value", ""),
            "status": "completed"
        }
    }
    return result

# Create a simple task function for testing
def simple_task(input_data):
    """
    A simple task for testing.
    
    Args:
        input_data: Input data for the task
        
    Returns:
        Dict containing the task result
    """
    # This is a placeholder that would normally use tools
    result = {
        "success": True,
        "result": f"Processed: {input_data.get('value', 'none')}"
    }
    return result


class TestWorkflowExamplesClass(unittest.TestCase):
    """Test cases for example workflows."""  # noqa: D202
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock workflow with recorded tool executions
        self.workflow_mock = MagicMock()
        self.workflow_mock.execute.return_value = {
            "success": True,
            "result": {"status": "completed"}
        }
        
        # Create a test harness
        self.harness = WorkflowTestHarness(
            workflow=self.workflow_mock,
            mock_registry=MagicMock(),
            initial_variables={"test_var": "test_value"}
        )
    
    def test_workflow_execution(self):
        """Test basic workflow execution."""
        # Execute the workflow
        result = self.harness.execute()
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["status"], "completed")
        
        # Verify the workflow was called with the correct context
        self.workflow_mock.execute.assert_called_once()
    
    def test_workflow_with_context_manager(self):
        """Test workflow execution with the context manager."""
        # Define mock executions for tools
        mock_executions = {
            "test_tool": [
                create_mock_tool_execution(
                    {"param": "value"},
                    {"success": True, "result": "Test result"}
                )
            ]
        }
        
        # Create a mock workflow
        workflow = MagicMock()
        
        # Use the context manager to execute the workflow
        with workflow_test_context(workflow, mock_executions, {"input": "test"}) as (wf, harness):
            # This would execute the workflow, but we're using a mock
            pass
        
        # Verify the workflow was set up correctly
        self.assertIsNotNone(workflow.tool_registry)
    
    def test_assertion_helpers(self):
        """Test the assertion helper methods."""
        # Mock executed tasks and outputs
        self.harness.executed_tasks = ["task1", "task2", "task3"]
        self.harness.task_outputs = {
            "task1": {"result": "result1"},
            "task2": {"result": "result2"},
            "task3": {"result": "result3"}
        }
        self.harness.execution_context = MagicMock()
        self.harness.execution_context.variables = {
            "var1": "value1",
            "var2": "value2"
        }
        
        # Test assertions
        self.harness.assert_task_executed("task1")
        self.harness.assert_task_not_executed("task4")
        self.harness.assert_tasks_executed_in_order(["task1", "task2"])
        
        # Test getting task output
        output = self.harness.get_task_output("task2")
        self.assertEqual(output["result"], "result2")
        
        # Test variable assertions
        self.harness.assert_variable_equals("var1", "value1")
        self.harness.assert_variable_contains("var2", "value")


class TestTaskExamplesClass(unittest.TestCase):
    """Test cases for example tasks."""  # noqa: D202
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock task
        self.task_mock = MagicMock()
        self.task_mock.execute.return_value = {
            "success": True,
            "result": "Task result"
        }
        
        # Create a test harness
        self.harness = TaskTestHarness(
            task=self.task_mock,
            mock_executions={},
            input_variables={"input_key": "input_value"}
        )
    
    def test_task_execution(self):
        """Test basic task execution."""
        # Execute the task
        result = self.harness.execute()
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "Task result")
        
        # Verify the task was called with the correct context
        self.task_mock.execute.assert_called_once()
    
    def test_task_assertion_helpers(self):
        """Test the assertion helper methods for tasks."""
        # Mock execution context
        self.harness.execution_context = MagicMock()
        self.harness.execution_context.variables = {
            "var1": "value1",
            "var2": "value with substring"
        }
        
        # Test variable assertions
        self.harness.assert_variable_equals("var1", "value1")
        self.harness.assert_variable_contains("var2", "substring")
        self.harness.assert_variable_matches("var2", r"value\s+with\s+\w+")


if __name__ == "__main__":
    unittest.main() 