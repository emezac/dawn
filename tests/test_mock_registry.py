"""
Tests for the MockToolRegistry.

This module demonstrates how to use the MockToolRegistry to test
workflows and tools without requiring real services.
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from core
from core.tools.mock_registry import (
    MockToolRegistry, 
    create_mock_registry,
    setup_mock_registry_for_test,
    register_mock_registry_with_services,
    with_mock_registry
)
from core.tools.registry_access import execute_tool, get_registry, tool_exists
from core.services import get_services
from core.errors import ErrorCode, create_error_response
from core.workflow import Workflow
from core.task import Task


class TestMockRegistry(unittest.TestCase):
    """Test case for MockToolRegistry functionality."""  # noqa: D202
    
    def setUp(self):
        """Set up before each test."""
        # Register a fresh mock registry
        self.mock_registry = register_mock_registry_with_services()
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean up after tests
        self.mock_registry = None
    
    def test_basic_mock_response(self):
        """Test basic mocking of a tool response."""
        # Set up a mock response
        self.mock_registry.mock_tool_as_success("test_tool", {"mock_result": "success"})
        
        # Execute the tool through registry_access functions
        result = execute_tool("test_tool", {"param": "value"})
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["mock_result"], "success")
    
    def test_mock_failure_response(self):
        """Test mocking a tool failure."""
        # Set up a mock failure
        self.mock_registry.mock_tool_as_failure("test_tool", "Simulated failure")
        
        # Execute the tool
        result = execute_tool("test_tool", {"param": "value"})
        
        # Verify the result
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Simulated failure")
    
    def test_input_specific_response(self):
        """Test that different inputs can get different responses."""
        # Set up different responses for different inputs
        input1 = {"id": "1", "action": "get"}
        input2 = {"id": "2", "action": "get"}
        
        self.mock_registry.add_mock_response(
            "parameterized_tool", 
            input1, 
            {"success": True, "result": {"data": "result1"}}
        )
        
        self.mock_registry.add_mock_response(
            "parameterized_tool", 
            input2, 
            {"success": True, "result": {"data": "result2"}}
        )
        
        # Execute with different inputs
        result1 = execute_tool("parameterized_tool", input1)
        result2 = execute_tool("parameterized_tool", input2)
        
        # Verify different results
        self.assertEqual(result1["result"]["data"], "result1")
        self.assertEqual(result2["result"]["data"], "result2")
    
    def test_recording_and_replay(self):
        """Test recording tool executions and replaying them."""
        # Start recording
        self.mock_registry.start_recording()
        
        # Execute some tools
        execute_tool("list_vector_stores", {})
        execute_tool("create_vector_store", {"name": "Test Store"})
        
        # Stop recording
        self.mock_registry.stop_recording()
        
        # Verify recordings
        recordings = self.mock_registry.get_recorded_executions()
        self.assertEqual(len(recordings), 2)
        self.assertEqual(recordings[0]["tool_name"], "list_vector_stores")
        self.assertEqual(recordings[1]["tool_name"], "create_vector_store")
        
        # Save recordings to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
            temp_path = temp.name
            self.mock_registry.save_recordings(temp_path)
        
        try:
            # Create a new mock registry
            new_registry = create_mock_registry()
            
            # Load recordings
            new_registry.load_recordings(temp_path)
            
            # Create mocks from recordings
            new_registry.create_mock_from_recordings()
            
            # Execute the same tools with the new registry
            result1 = new_registry.execute_tool("list_vector_stores", {})
            result2 = new_registry.execute_tool("create_vector_store", {"name": "Test Store"})
            
            # Verify same responses
            self.assertEqual(result1, recordings[0]["response"])
            self.assertEqual(result2, recordings[1]["response"])
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestMockRegistryWithDecorator(unittest.TestCase):
    """Test case demonstrating the decorator pattern for MockToolRegistry."""  # noqa: D202
    
    @with_mock_registry
    def test_with_decorator(self, mock_registry):
        """Test using the with_mock_registry decorator."""
        # The decorator sets up a mock registry and passes it to the test
        self.assertIsInstance(mock_registry, MockToolRegistry)
        
        # Configure the mock registry
        mock_registry.mock_tool_as_success("special_tool", {"special": True})
        
        # Use the tool
        result = execute_tool("special_tool", {})
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertTrue(result["result"]["special"])


class TestWorkflowWithMockRegistry(unittest.TestCase):
    """Test case demonstrating workflow testing with MockToolRegistry."""  # noqa: D202
    
    def setUp(self):
        """Set up a workflow and mock registry."""
        # Register a mock registry
        self.mock_registry = register_mock_registry_with_services()
        
        # Configure mock responses for tools used by the workflow
        self.mock_registry.mock_tool_as_success("data_fetch", {"items": [1, 2, 3]})
        self.mock_registry.mock_tool_as_success("data_process", {"processed": True})
        
        # Create a simple workflow
        self.workflow = Workflow(workflow_id="test_workflow", name="Test Workflow")
        
        # Add tasks
        task1 = Task(
            task_id="task1",
            name="Fetch Data",
            tool_name="data_fetch",
            input_data={"source": "test"},
            next_task_id_on_success="task2"
        )
        
        task2 = Task(
            task_id="task2",
            name="Process Data",
            tool_name="data_process",
            input_data={"data": "${task1.output_data.result.items}"},
            next_task_id_on_success=None
        )
        
        self.workflow.add_task(task1)
        self.workflow.add_task(task2)
    
    def test_workflow_execution(self):
        """Test executing a workflow with mock tools."""
        from core.engine import WorkflowEngine
        
        # Create an engine and execute the workflow
        engine = WorkflowEngine(self.workflow)
        success = engine.execute()
        
        # Verify workflow executed successfully
        self.assertTrue(success)
        
        # Verify task states
        self.assertEqual(self.workflow.tasks["task1"].status, "completed")
        self.assertEqual(self.workflow.tasks["task2"].status, "completed")
        
        # Verify task outputs
        task1_output = self.workflow.tasks["task1"].output_data
        self.assertIn("items", task1_output.get("response", {}))
        
        task2_output = self.workflow.tasks["task2"].output_data
        self.assertTrue(task2_output.get("response", {}).get("processed", False))


if __name__ == "__main__":
    unittest.main() 