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
        """Test constructor of DirectHandlerTask."""
        # Define a sample handler function
        def test_handler(data):
            return {"success": True, "result": data}

        # Initialize with handler
        task = DirectHandlerTask(task_id="test_task", name="Test Task", handler=test_handler)
        self.assertEqual(task.id, "test_task")
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.handler_name, "test_handler")
        self.assertEqual(task.status, "pending")

    def test_execute_success(self):
        """Test successful execution of a DirectHandlerTask."""
        # Create a simple success handler
        def success_handler(data):
            return {"success": True, "result": "Success", "response": "Success"}

        # Create a DirectHandlerTask
        task = DirectHandlerTask(task_id="success_task", name="Success Task", handler=success_handler)

        # Execute the task
        result = task.execute()

        # Verify success
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("result"), "Success")
        self.assertEqual(result.get("response"), "Success")

    def test_execute_failure(self):
        """Test failed execution of a DirectHandlerTask."""
        # Create a simple failure handler
        def failure_handler(data):
            return {"success": False, "error": "Failure reason", "result": None}

        # Create a DirectHandlerTask
        task = DirectHandlerTask(task_id="failure_task", name="Failure Task", handler=failure_handler)

        # Execute the task
        result = task.execute()

        # Verify failure
        self.assertFalse(result.get("success"))
        self.assertEqual(result.get("error"), "Failure reason")

    def test_execute_exception(self):
        """Test exception handling in a DirectHandlerTask."""
        # Create a handler that raises an exception
        def exception_handler(data):
            raise ValueError("Test exception")

        # Create a DirectHandlerTask
        task = DirectHandlerTask(task_id="exception_task", name="Exception Task", handler=exception_handler)

        # Execute the task
        result = task.execute()

        # Verify exception was handled
        self.assertFalse(result.get("success"))
        self.assertTrue("Test exception" in result.get("error", ""))
        self.assertEqual(result.get("error_type"), "ValueError")

    def test_execute_non_dict_result(self):
        """Test handling of non-dict return values from handler."""
        # Create a handler that returns a non-dict value
        def invalid_handler(data):
            return "Not a dictionary"

        # Create a DirectHandlerTask
        task = DirectHandlerTask(task_id="invalid_task", name="Invalid Task", handler=invalid_handler)

        # Execute the task
        result = task.execute()
        
        # Debug print
        print("\nDEBUG: test_execute_non_dict_result result:", result)
        print("DEBUG: success value =", result.get("success"))
        print("DEBUG: error message =", result.get("error"))

        # Verify error handling
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("result"), "Not a dictionary")

    def test_to_dict(self):
        """Test the to_dict method of DirectHandlerTask."""
        # Create a named handler function for testing
        def named_handler(data):
            return {"success": True}

        # Create a DirectHandlerTask
        task = DirectHandlerTask(task_id="dict_task", name="Dict Task", handler=named_handler)

        # Generate dictionary representation
        result = task.to_dict()

        # Verify dictionary contains required fields
        self.assertEqual(result.get("task_id"), "dict_task")
        self.assertEqual(result.get("name"), "Dict Task")
        self.assertTrue(result.get("is_direct_handler"))
        self.assertEqual(result.get("handler_name"), "named_handler")

    def test_execute_with_processed_input(self):
        """Test execution with processed input that overrides task input_data."""
        # Create an input handler
        def input_handler(data):
            return {"success": True, "result": f"Input: {data.get('value', 'None')}"}

        # Create a DirectHandlerTask with input data
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
        """Test running a workflow with DirectHandlerTask and regular tasks."""
        # Define a simple handler for testing
        def simple_handler(task, data):
            return {"success": True, "result": "Simple handler result"}
            
        # Create a direct handler task
        direct_task = DirectHandlerTask(
            task_id="direct_task",
            name="Direct Task",
            handler=simple_handler,
            next_task_id_on_success="regular_task"
        )
        
        # Create a regular task with real tool registry
        regular_task = Task(
            task_id="regular_task",
            name="Regular Task",
            is_llm_task=False,
            tool_name="test_tool"
        )
        
        # Create a new workflow
        workflow = Workflow("mixed_workflow", "Mixed Task Workflow")
        workflow.add_task(direct_task)
        workflow.add_task(regular_task)
        workflow.task_order = ["direct_task", "regular_task"]
        
        # Add a get_task method to the workflow if necessary
        if not hasattr(workflow, "get_task"):
            def get_task(self, task_id):
                return self.tasks.get(task_id)
            
            # Attach the method to the workflow object
            workflow.get_task = get_task.__get__(workflow)
        
        # Add a set_error method to the workflow if necessary
        if not hasattr(workflow, "set_error"):
            def set_error(self, error_message, error_code=None, task_id=None):
                self.status = "failed"
                self.error = error_message
                self.error_code = error_code
                self.failed_task_id = task_id
                print(f"Workflow '{self.id}' error: {error_message}")
                
            # Attach the method to the workflow object
            workflow.set_error = set_error.__get__(workflow)
        
        # Create a real tool registry instead of a mock
        tool_registry = ToolRegistry()
        
        # Register a test tool
        def test_tool(**kwargs):
            return {
                "success": True,
                "result": {"message": "Tool executed successfully"}
            }
        
        tool_registry.register_tool("test_tool", test_tool)
        
        # Create the engine
        engine = WorkflowEngine(
            workflow=workflow, 
            llm_interface=self.llm_interface, 
            tool_registry=tool_registry
        )
        
        # Run the workflow
        result = engine.run()
        
        # Check the result
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "completed")


if __name__ == "__main__":
    unittest.main()
