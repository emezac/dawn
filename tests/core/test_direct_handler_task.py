"""
Tests for the DirectHandlerTask class and its integration with WorkflowEngine.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Now import modules using absolute imports
from core.engine import WorkflowEngine
from core.llm.interface import LLMInterface
from core.task import DirectHandlerTask, Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow
# Import the singleton access function
from core.tools.registry_access import get_registry, reset_registry


class TestDirectHandlerTask(unittest.TestCase):
    """Test the DirectHandlerTask class functionality."""  # noqa: D202

    def setUp(self):
        """Set up for testing."""
        # Reset the registry before each test
        reset_registry()
        # Get the singleton instance
        self.registry = get_registry()
        self.llm_interface = MagicMock(spec=LLMInterface)
        self.workflow = Workflow(workflow_id="test_workflow", name="Test Workflow")

    def test_init(self):
        """Test DirectHandlerTask initialization with basic parameters."""  # noqa: D202

        # Define a simple handler function
        def test_handler(data):
            return {"success": True, "result": f"Processed: {data.get('value', 'none')}"}

        # Create a task with the handler
        task = DirectHandlerTask(
            task_id="test_task", name="Test Task", handler=test_handler, input_data={"value": "test_value"}
        )

        # Validate the task attributes
        self.assertEqual(task.id, "test_task")
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.tool_name, "__direct_handler__")
        self.assertFalse(task.is_llm_task)
        self.assertTrue(task.is_direct_handler)
        self.assertEqual(task.input_data, {"value": "test_value"})
        self.assertEqual(task.handler, test_handler)

    def test_execute_success(self):
        """Test successful execution of a DirectHandlerTask."""  # noqa: D202

        # Handler that returns a success response
        def success_handler(data):
            return {"success": True, "result": f"Success with {data.get('value')}"}

        task = DirectHandlerTask(
            task_id="success_task", name="Success Task", handler=success_handler, input_data={"value": "test_data"}
        )

        # Execute the task
        result = task.execute()

        # Validate the result
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("result"), "Success with test_data")

    def test_execute_failure(self):
        """Test failed execution of a DirectHandlerTask."""  # noqa: D202

        # Handler that returns a failure response
        def failure_handler(data):
            return {"success": False, "error": "Simulated failure"}

        task = DirectHandlerTask(task_id="failure_task", name="Failure Task", handler=failure_handler)

        # Execute the task
        result = task.execute()

        # Validate the result
        self.assertFalse(result.get("success"))
        self.assertEqual(result.get("error"), "Simulated failure")

    def test_execute_exception(self):
        """Test execution when handler raises an exception."""  # noqa: D202

        # Handler that raises an exception
        def exception_handler(data):
            raise ValueError("Test exception")

        task = DirectHandlerTask(task_id="exception_task", name="Exception Task", handler=exception_handler)

        # Execute the task
        result = task.execute()

        # Validate the result
        self.assertFalse(result.get("success"))
        self.assertIn("Test exception", result.get("error", ""))
        self.assertEqual(result.get("error_type"), "ValueError")
        self.assertIn("traceback", result)

    def test_execute_non_dict_result(self):
        """Test handling of non-dictionary return values from handler."""  # noqa: D202

        # Handler that returns a non-dict value
        def invalid_handler(data):
            return "This is not a dictionary"

        task = DirectHandlerTask(task_id="invalid_result_task", name="Invalid Result Task", handler=invalid_handler)

        # Execute the task
        result = task.execute()

        # Validate the result
        self.assertFalse(result.get("success"))
        self.assertIn("non-dict value", result.get("error", ""))
        self.assertIn("str", result.get("error", ""))

    def test_to_dict(self):
        """Test the to_dict method of DirectHandlerTask."""  # noqa: D202

        def named_handler(data):
            return {"success": True}

        task = DirectHandlerTask(task_id="dict_task", name="Dict Task", handler=named_handler)

        # Get the dictionary representation
        task_dict = task.to_dict()

        # Validate dictionary fields
        self.assertEqual(task_dict["id"], "dict_task")
        self.assertEqual(task_dict["name"], "Dict Task")
        self.assertTrue(task_dict["is_direct_handler"])
        self.assertEqual(task_dict["handler_name"], "named_handler")

    def test_execute_with_processed_input(self):
        """Test execution with pre-processed input."""  # noqa: D202

        # Create a handler that uses input data
        def input_handler(data):
            return {"success": True, "result": f"Input: {data.get('value', 'none')}"}

        task = DirectHandlerTask(
            task_id="input_task", name="Input Task", handler=input_handler, input_data={"value": "original"}
        )

        # Execute with processed input that overrides original
        processed_input = {"value": "processed"}
        result = task.execute(processed_input)

        # Validate the result uses processed input
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("result"), "Input: processed")

    def test_workflow_engine_integration(self):
        """Test integration with WorkflowEngine."""
        # Create a handler that will be called by the engine
        handler_called = False

        def test_handler(data):
            nonlocal handler_called
            handler_called = True
            return {"success": True, "result": "Handler executed"}

        # Create a DirectHandlerTask
        task = DirectHandlerTask(task_id="engine_test_task", name="Engine Test Task", handler=test_handler)

        # Add the task to the workflow
        self.workflow.add_task(task)

        # Create the workflow engine
        engine = WorkflowEngine(workflow=self.workflow, llm_interface=self.llm_interface, tool_registry=self.registry)

        # Execute the task
        success = engine.execute_task(task)

        # Verify the handler was called and execution succeeded
        self.assertTrue(handler_called, "DirectHandlerTask handler was not called")
        self.assertTrue(success, "Task execution was not successful")
        self.assertEqual(task.status, "completed")


class TestWorkflowEngineWithDirectHandler(unittest.TestCase):
    """Test the WorkflowEngine with DirectHandlerTask integration."""  # noqa: D202

    def setUp(self):
        """Set up for workflow tests."""
        # Reset the registry before each test
        reset_registry()
        # Get the singleton instance
        self.registry = get_registry()
        self.llm_interface = MagicMock(spec=LLMInterface)

        # Create a workflow with multiple task types
        self.workflow = Workflow(workflow_id="mixed_workflow", name="Mixed Task Workflow")

        # 1. Create a DirectHandlerTask
        def direct_handler(data):
            return {"success": True, "result": "Direct handler result", "response": "Direct handler result"}

        self.direct_task = DirectHandlerTask(
            task_id="direct_task", name="Direct Task", handler=direct_handler, next_task_id_on_success="llm_task"
        )
        self.workflow.add_task(self.direct_task)

        # 2. Create an LLM task
        self.llm_task = Task(
            task_id="llm_task",
            name="LLM Task",
            is_llm_task=True,
            input_data={"prompt": "Test prompt"},
            next_task_id_on_success="tool_task",
        )
        self.workflow.add_task(self.llm_task)

        # 3. Create a tool task
        self.tool_task = Task(
            task_id="tool_task", name="Tool Task", tool_name="test_tool", input_data={"param": "value"}
        )
        self.workflow.add_task(self.tool_task)

        # Mock the LLM interface and tool registry
        self.llm_interface.execute_llm_call.return_value = {"success": True, "response": "LLM response"}

        # Register a test tool
        def test_tool(**kwargs):
            return {"success": True, "result": "Tool result", "response": "Tool result"}

        self.registry.register_tool("test_tool", test_tool)

        # Create the engine
        self.engine = WorkflowEngine(
            workflow=self.workflow, llm_interface=self.llm_interface, tool_registry=self.registry
        )

    def test_run_workflow_with_mixed_tasks(self):
        """Test running a workflow with DirectHandlerTask and regular tasks."""  # noqa: D202

        # Set up the expected task order - using the workflow's task_order attribute directly
        # The Workflow class doesn't have a set_task_order method
        self.workflow.task_order = ["direct_task", "llm_task", "tool_task"]

        # Run the workflow
        result = self.engine.run()

        # Verify the workflow completed successfully - using .value to get the raw string
        if hasattr(result["status"], "value"):
            # For enum values
            self.assertEqual(result["status"].value, "completed")
        else:
            # For string values
            self.assertEqual(result["status"], "completed")

        # Verify each task was executed and completed
        self.assertEqual(self.direct_task.status, "completed")
        self.assertEqual(self.llm_task.status, "completed")
        self.assertEqual(self.tool_task.status, "completed")

        # Verify the direct handler task output
        self.assertTrue("result" in self.direct_task.output_data)
        self.assertTrue(self.direct_task.output_data.get("success", False))
        self.assertEqual(self.direct_task.output_data.get("result"), "Direct handler result")


if __name__ == "__main__":
    unittest.main()
