#!/usr/bin/env python3
"""
Tests for workflow and task utilities.

This module demonstrates how to use the WorkflowTestHarness and TaskTestHarness
for testing workflows and tasks.
"""  # noqa: D202

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import testing utilities
from core.utils.testing import (
    WorkflowTestHarness,
    TaskTestHarness,
    create_test_workflow,
    add_simple_task,
    add_llm_task,
    add_direct_handler_task,
    create_mock_task_output,
    create_simple_test_handler,
    workflow_test_context,
    create_mock_tool_execution
)

# Import core components
from core.task import Task, DirectHandlerTask
from core.workflow import Workflow
from core.engine import WorkflowEngine
from core.tools.registry_access import execute_tool
from core.registry import Tool


class TestWorkflowUtilities(unittest.TestCase):
    """Test case for workflow testing utilities."""  # noqa: D202

    def test_basic_workflow_execution(self):
        """Test executing a basic workflow with the test harness."""
        # Define a simple workflow with two tasks
        workflow = Workflow(
            name="test_workflow",
            description="A test workflow",
            tasks=[
                Task(
                    name="first_task",
                    description="First task",
                    tool_name="test_tool",
                    inputs={
                        "input1": "input_value",
                        "input2": "${workflow_input}"
                    },
                    outputs={
                        "output1": "output1",
                        "output2": "output2"
                    }
                ),
                Task(
                    name="second_task",
                    description="Second task",
                    tool_name="test_tool",
                    inputs={
                        "input1": "${first_task.output1}",
                        "input2": "static_value"
                    },
                    outputs={
                        "final_output": "output1"
                    }
                )
            ]
        )

        # Set up mock tool responses
        mock_executions = {
            "test_tool": [
                create_mock_tool_execution(
                    inputs={"input1": "input_value", "input2": "workflow_value"},
                    outputs={"output1": "first_task_output", "output2": "another_output"}
                ),
                create_mock_tool_execution(
                    inputs={"input1": "first_task_output", "input2": "static_value"},
                    outputs={"output1": "final_result"}
                )
            ]
        }

        # Create the test harness
        harness = WorkflowTestHarness(
            workflow=workflow,
            mock_executions=mock_executions,
            initial_variables={"workflow_input": "workflow_value"}
        )

        # Execute the workflow
        result = harness.execute()

        # Check the workflow execution
        harness.assert_workflow_completed()
        harness.assert_task_executed("first_task")
        harness.assert_task_executed("second_task")
        harness.assert_task_executed_before("first_task", "second_task")
        harness.assert_task_complete("first_task")
        harness.assert_task_complete("second_task")

        # Check task outputs
        self.assertEqual(
            harness.get_task_output("first_task", "output1"),
            "first_task_output"
        )
        self.assertEqual(
            harness.get_task_output("second_task", "final_output"),
            "final_result"
        )

        # Check workflow result
        self.assertEqual(result["second_task.final_output"], "final_result")

    def test_workflow_with_llm_task(self):
        """Test executing a workflow that includes an LLM task."""
        # Define a workflow with an LLM task
        workflow = Workflow(
            name="llm_workflow",
            description="A workflow with an LLM task",
            tasks=[
                Task(
                    name="llm_task",
                    description="Task that calls an LLM",
                    tool_name="llm",
                    inputs={
                        "prompt": "Generate a JSON with the following format: ${format}",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    outputs={
                        "response": "response",
                        "usage": "usage"
                    }
                ),
                Task(
                    name="parse_json",
                    description="Parse the LLM response",
                    tool_name="parse_json",
                    inputs={
                        "json_string": "${llm_task.response}"
                    },
                    outputs={
                        "parsed_data": "result"
                    }
                )
            ]
        )

        # Set up mock tool responses
        mock_executions = {
            "llm": [
                create_mock_tool_execution(
                    inputs={
                        "prompt": "Generate a JSON with the following format: {\"name\": \"string\", \"age\": \"number\"}",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    outputs={
                        "response": "{\"name\": \"John Doe\", \"age\": 30}",
                        "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30}
                    }
                )
            ],
            "parse_json": [
                create_mock_tool_execution(
                    inputs={"json_string": "{\"name\": \"John Doe\", \"age\": 30}"},
                    outputs={"result": {"name": "John Doe", "age": 30}}
                )
            ]
        }

        # Create the test harness
        harness = WorkflowTestHarness(
            workflow=workflow,
            mock_executions=mock_executions,
            initial_variables={"format": "{\"name\": \"string\", \"age\": \"number\"}"}
        )

        # Execute the workflow
        result = harness.execute()

        # Check tool calls
        llm_calls = harness.get_tool_calls("llm")
        self.assertEqual(len(llm_calls), 1)
        self.assertEqual(llm_calls[0].inputs["temperature"], 0.7)
        self.assertTrue("format" in llm_calls[0].inputs["prompt"])

        # Check the parsed data
        parsed_data = harness.get_task_output("parse_json", "parsed_data")
        self.assertEqual(parsed_data["name"], "John Doe")
        self.assertEqual(parsed_data["age"], 30)

    def test_workflow_with_direct_handler(self):
        """Test executing a workflow with a direct handler task."""
        # Define a handler that performs a simple operation
        def math_operation_handler(operation: str, a: int, b: int) -> Dict[str, Any]:
            if operation == "add":
                result = a + b
            elif operation == "multiply":
                result = a * b
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            return {"result": result}

        # Define a workflow with a direct handler task
        workflow = Workflow(
            name="direct_handler_workflow",
            description="A workflow with a direct handler task",
            tasks=[
                DirectHandlerTask(
                    name="math_operation",
                    description="Perform a math operation",
                    handler=math_operation_handler,
                    inputs={
                        "operation": "${operation}",
                        "a": "${a}",
                        "b": "${b}"
                    },
                    outputs={
                        "operation_result": "result"
                    }
                ),
                Task(
                    name="format_result",
                    description="Format the result",
                    tool_name="format_string",
                    inputs={
                        "template": "The result is: ${math_operation.operation_result}",
                    },
                    outputs={
                        "formatted": "result"
                    }
                )
            ]
        )

        # Set up mock tool responses
        mock_executions = {
            "format_string": [
                create_mock_tool_execution(
                    inputs={"template": "The result is: 15"},
                    outputs={"result": "The result is: 15"}
                )
            ]
        }

        # Create the test harness
        harness = WorkflowTestHarness(
            workflow=workflow,
            mock_executions=mock_executions,
            initial_variables={"operation": "add", "a": 10, "b": 5}
        )

        # Execute the workflow
        result = harness.execute()

        # Check the direct handler task output
        self.assertEqual(
            harness.get_task_output("math_operation", "operation_result"),
            15
        )

        # Check the final result
        self.assertEqual(
            result["format_result.formatted"],
            "The result is: 15"
        )

    def test_workflow_failure(self):
        """Test handling of workflow failures."""
        # Define a workflow with a task that will fail
        workflow = Workflow(
            name="failing_workflow",
            description="A workflow with a failing task",
            tasks=[
                Task(
                    name="failing_task",
                    description="This task will fail",
                    tool_name="test_tool",
                    inputs={"input": "value"},
                    outputs={"output": "result"}
                ),
                Task(
                    name="next_task",
                    description="This task should not execute",
                    tool_name="test_tool",
                    inputs={"input": "${failing_task.output}"},
                    outputs={"output": "result"}
                )
            ]
        )

        # Set up mock tool responses with a failure
        mock_executions = {
            "test_tool": [
                create_mock_tool_execution(
                    inputs={"input": "value"},
                    fail=True,
                    error_message="Simulated failure"
                )
            ]
        }

        # Create the test harness
        harness = WorkflowTestHarness(
            workflow=workflow,
            mock_executions=mock_executions
        )

        # Execute the workflow
        result = harness.execute()

        # Check task status
        harness.assert_task_executed("failing_task")
        harness.assert_task_failed("failing_task")
        harness.assert_task_not_executed("next_task")

        # Check error message
        self.assertEqual(
            harness.get_task_error("failing_task"),
            "Simulated failure"
        )


class TestTaskTestHarness(unittest.TestCase):
    """Test case for task testing utilities."""  # noqa: D202

    def test_execute_task(self):
        """Test executing a single task with the test harness."""
        # Define a task
        task = Task(
            name="test_task",
            description="A test task",
            tool_name="test_tool",
            inputs={
                "input1": "${variable1}",
                "input2": "static_value"
            },
            outputs={
                "output1": "result1",
                "output2": "result2"
            }
        )

        # Create a mock execution
        mock_execution = create_mock_tool_execution(
            inputs={"input1": "variable_value", "input2": "static_value"},
            outputs={"result1": "output_value_1", "result2": "output_value_2"}
        )

        # Create the test harness
        harness = TaskTestHarness(
            task=task,
            mock_execution=mock_execution,
            variables={"variable1": "variable_value"}
        )

        # Execute the task
        outputs = harness.execute()

        # Check the results
        harness.assert_complete()
        self.assertEqual(harness.get_output("output1"), "output_value_1")
        self.assertEqual(harness.get_output("output2"), "output_value_2")
        self.assertEqual(outputs["output1"], "output_value_1")
        self.assertEqual(outputs["output2"], "output_value_2")

    def test_direct_handler_task(self):
        """Test executing a direct handler task."""
        # Define a direct handler task
        task = DirectHandlerTask(
            name="direct_handler_task",
            description="A direct handler task",
            handler=lambda x, y: {"sum": x + y, "product": x * y},
            inputs={"x": "${x_value}", "y": "${y_value}"},
            outputs={"sum_result": "sum", "product_result": "product"}
        )

        # Create the test harness
        harness = TaskTestHarness(
            task=task,
            variables={"x_value": 5, "y_value": 3}
        )

        # Execute the task
        outputs = harness.execute()

        # Check the results
        harness.assert_complete()
        self.assertEqual(harness.get_output("sum_result"), 8)
        self.assertEqual(harness.get_output("product_result"), 15)
        self.assertEqual(outputs["sum_result"], 8)
        self.assertEqual(outputs["product_result"], 15)

    def test_task_failure(self):
        """Test handling of task failures."""
        # Define a task
        task = Task(
            name="failing_task",
            description="A task that will fail",
            tool_name="test_tool",
            inputs={"input": "value"},
            outputs={"output": "result"}
        )

        # Create a mock execution with failure
        mock_execution = create_mock_tool_execution(
            inputs={"input": "value"},
            fail=True,
            error_message="Simulated task failure"
        )

        # Create the test harness
        harness = TaskTestHarness(
            task=task,
            mock_execution=mock_execution
        )

        # Execute the task and check the failure
        outputs = harness.execute()
        
        harness.assert_failed()
        self.assertEqual(harness.get_error(), "Simulated task failure")
        self.assertEqual(harness.get_status(), "failed")
        self.assertEqual(outputs, {})


if __name__ == "__main__":
    unittest.main() 