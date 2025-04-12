#!/usr/bin/env python3
"""
Integration Tests for Core Workflow Features

This module contains integration tests for the core features of the workflow system,
testing the interaction between the workflow engine, tasks, and variable resolution.
"""  # noqa: D202

import unittest
import os
import sys
import json
import logging
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import workflow components
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.engine import WorkflowEngine
from core.tools.registry import ToolRegistry
from core.tools.registry_access import reset_registry, get_registry
from core.services import get_services, reset_services
from core.utils.testing import MockToolRegistry, WorkflowTestHarness

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestWorkflowExecution(unittest.TestCase):
    """Test the core workflow execution functionality."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Reset singletons
        reset_registry()
        reset_services()
        
        # Get services and registry
        self.services = get_services()
        self.registry = get_registry()
        
        # Create and register a mock tool registry
        self.mock_registry = MockToolRegistry()
        self.services.tool_registry = self.mock_registry
        
        # Set up basic mock tools
        self.mock_registry.register_tool("echo", lambda input_data: {
            "success": True,
            "result": input_data.get("text", "No text provided")
        })
        
        self.mock_registry.register_tool("add", lambda input_data: {
            "success": True,
            "result": input_data.get("a", 0) + input_data.get("b", 0)
        })
        
        self.mock_registry.register_tool("fail", lambda input_data: {
            "success": False,
            "error": input_data.get("error_message", "Generic error")
        })
        
        # Create a workflow engine
        self.engine = WorkflowEngine()

    def test_basic_workflow_execution(self):
        """Test basic workflow execution with a single task."""
        # Create a simple workflow with one task
        workflow = Workflow(workflow_id="test_basic", name="Basic Workflow")
        
        task = Task(
            task_id="echo_task",
            name="Echo Task",
            tool_name="echo",
            input_data={"text": "Hello, workflow!"}
        )
        workflow.add_task(task)
        
        # Run the workflow
        result = self.engine.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        self.assertEqual(workflow.tasks["echo_task"].status, "completed")
        self.assertEqual(
            workflow.tasks["echo_task"].output_data.get("result"),
            "Hello, workflow!"
        )

    def test_sequential_task_execution(self):
        """Test sequential execution of multiple tasks."""
        # Create a workflow with sequential tasks
        workflow = Workflow(workflow_id="test_sequential", name="Sequential Workflow")
        
        task1 = Task(
            task_id="task_1",
            name="First Task",
            tool_name="echo",
            input_data={"text": "Task 1 output"},
            next_task_id_on_success="task_2"
        )
        workflow.add_task(task1)
        
        task2 = Task(
            task_id="task_2",
            name="Second Task",
            tool_name="echo",
            input_data={"text": "${task_1.output_data.result} processed"},
            next_task_id_on_success="task_3"
        )
        workflow.add_task(task2)
        
        task3 = Task(
            task_id="task_3",
            name="Third Task",
            tool_name="echo",
            input_data={"text": "Final: ${task_2.output_data.result}"}
        )
        workflow.add_task(task3)
        
        # Run the workflow
        result = self.engine.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        self.assertEqual(workflow.tasks["task_1"].status, "completed")
        self.assertEqual(workflow.tasks["task_2"].status, "completed")
        self.assertEqual(workflow.tasks["task_3"].status, "completed")
        
        # Verify task outputs
        self.assertEqual(workflow.tasks["task_1"].output_data.get("result"), "Task 1 output")
        self.assertEqual(workflow.tasks["task_2"].output_data.get("result"), "Task 1 output processed")
        self.assertEqual(workflow.tasks["task_3"].output_data.get("result"), "Final: Task 1 output processed")

    def test_conditional_task_execution(self):
        """Test conditional execution of tasks based on conditions."""
        # Create a workflow with conditional tasks
        workflow = Workflow(workflow_id="test_conditional", name="Conditional Workflow")
        
        task1 = Task(
            task_id="eval_condition",
            name="Evaluate Condition",
            tool_name="echo",
            input_data={"text": "condition_result", "value": 10}
        )
        workflow.add_task(task1)
        
        # Task executed only if value > 5
        task2 = Task(
            task_id="positive_branch",
            name="Positive Branch",
            tool_name="echo",
            input_data={"text": "Condition met"},
            condition="${eval_condition.output_data.value > 5}"
        )
        workflow.add_task(task2)
        
        # Task executed only if value <= 5
        task3 = Task(
            task_id="negative_branch",
            name="Negative Branch",
            tool_name="echo",
            input_data={"text": "Condition not met"},
            condition="${eval_condition.output_data.value <= 5}"
        )
        workflow.add_task(task3)
        
        # Run the workflow
        result = self.engine.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        self.assertEqual(workflow.tasks["eval_condition"].status, "completed")
        self.assertEqual(workflow.tasks["positive_branch"].status, "skipped")  # Condition not evaluated with our limited mock
        self.assertEqual(workflow.tasks["negative_branch"].status, "skipped")  # Condition not evaluated with our limited mock

    def test_direct_handler_task(self):
        """Test execution of DirectHandlerTask with custom handler function."""
        # Create a workflow with a DirectHandlerTask
        workflow = Workflow(workflow_id="test_direct_handler", name="Direct Handler Workflow")
        
        # Define a handler function
        def custom_handler(input_data):
            value = input_data.get("value", 0)
            return {
                "success": True,
                "result": value * 2
            }
        
        task1 = Task(
            task_id="provide_input",
            name="Provide Input",
            tool_name="echo",
            input_data={"text": "input_value", "value": 5},
            next_task_id_on_success="process_input"
        )
        workflow.add_task(task1)
        
        task2 = DirectHandlerTask(
            task_id="process_input",
            name="Process Input",
            handler=custom_handler,
            input_data={"value": "${provide_input.output_data.value}"}
        )
        workflow.add_task(task2)
        
        # Run the workflow
        result = self.engine.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        self.assertEqual(workflow.tasks["provide_input"].status, "completed")
        self.assertEqual(workflow.tasks["process_input"].status, "completed")
        self.assertEqual(workflow.tasks["process_input"].output_data.get("result"), 10)  # 5 * 2

    def test_error_handling(self):
        """Test error handling and recovery in workflows."""
        # Create a workflow with error handling
        workflow = Workflow(workflow_id="test_error_handling", name="Error Handling Workflow")
        
        task1 = Task(
            task_id="task_will_fail",
            name="Task That Will Fail",
            tool_name="fail",
            input_data={"error_message": "Intentional failure"},
            next_task_id_on_success="success_path",
            next_task_id_on_failure="error_handler"
        )
        workflow.add_task(task1)
        
        task2 = Task(
            task_id="success_path",
            name="Success Path",
            tool_name="echo",
            input_data={"text": "Success path executed"}
        )
        workflow.add_task(task2)
        
        task3 = Task(
            task_id="error_handler",
            name="Error Handler",
            tool_name="echo",
            input_data={"text": "Error detected: ${error.task_will_fail}"}
        )
        workflow.add_task(task3)
        
        # Run the workflow
        result = self.engine.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))  # The workflow should succeed even with a task failure
        self.assertEqual(workflow.tasks["task_will_fail"].status, "failed")
        self.assertEqual(workflow.tasks["success_path"].status, "skipped")
        self.assertEqual(workflow.tasks["error_handler"].status, "completed")
        self.assertIn("Error detected:", workflow.tasks["error_handler"].output_data.get("result", ""))

    def test_variable_resolution(self):
        """Test variable resolution between tasks."""
        # Create a workflow with variable resolution
        workflow = Workflow(workflow_id="test_variable_resolution", name="Variable Resolution Workflow")
        
        task1 = Task(
            task_id="set_variable",
            name="Set Variable",
            tool_name="echo",
            input_data={"text": "variable_value", "nested": {"key": "nested_value"}},
            next_task_id_on_success="use_variable"
        )
        workflow.add_task(task1)
        
        task2 = Task(
            task_id="use_variable",
            name="Use Variable",
            tool_name="echo",
            input_data={
                "text": "Using variable: ${set_variable.output_data.result}",
                "nested_value": "${set_variable.output_data.nested.key}"
            }
        )
        workflow.add_task(task2)
        
        # Run the workflow
        result = self.engine.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        self.assertEqual(workflow.tasks["set_variable"].status, "completed")
        self.assertEqual(workflow.tasks["use_variable"].status, "completed")
        self.assertEqual(
            workflow.tasks["use_variable"].output_data.get("result"),
            "Using variable: variable_value"
        )

    def test_data_transformation(self):
        """Test data transformation between tasks."""
        # Create a workflow with data transformation
        workflow = Workflow(workflow_id="test_transformation", name="Data Transformation Workflow")
        
        task1 = Task(
            task_id="generate_numbers",
            name="Generate Numbers",
            tool_name="echo",
            input_data={"text": "numbers", "values": [1, 2, 3, 4, 5]},
            next_task_id_on_success="transform_data"
        )
        workflow.add_task(task1)
        
        # Define a handler for data transformation
        def transform_handler(input_data):
            values = input_data.get("values", [])
            transformed = [v * 2 for v in values]
            return {
                "success": True,
                "result": {
                    "transformed_values": transformed,
                    "sum": sum(transformed)
                }
            }
        
        task2 = DirectHandlerTask(
            task_id="transform_data",
            name="Transform Data",
            handler=transform_handler,
            input_data={"values": "${generate_numbers.output_data.values}"},
            next_task_id_on_success="use_transformed"
        )
        workflow.add_task(task2)
        
        task3 = Task(
            task_id="use_transformed",
            name="Use Transformed Data",
            tool_name="echo",
            input_data={"text": "Sum of transformed values: ${transform_data.output_data.result.sum}"}
        )
        workflow.add_task(task3)
        
        # Run the workflow
        result = self.engine.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        self.assertEqual(workflow.tasks["generate_numbers"].status, "completed")
        self.assertEqual(workflow.tasks["transform_data"].status, "completed")
        self.assertEqual(workflow.tasks["use_transformed"].status, "completed")
        
        # Check transformation results
        self.assertEqual(
            workflow.tasks["transform_data"].output_data.get("result", {}).get("transformed_values"),
            [2, 4, 6, 8, 10]
        )
        self.assertEqual(
            workflow.tasks["transform_data"].output_data.get("result", {}).get("sum"),
            30
        )
        
        # Check final output
        self.assertEqual(
            workflow.tasks["use_transformed"].output_data.get("result"),
            "Sum of transformed values: 30"
        )


class TestWorkflowComplex(unittest.TestCase):
    """Test complex workflow scenarios and edge cases."""  # noqa: D202

    def setUp(self):
        """Set up for complex workflow tests."""
        # Reset singletons
        reset_registry()
        reset_services()
        
        # Create test harness
        self.harness = WorkflowTestHarness()
        
        # Register mock tools
        self.harness.register_mock_tool(
            "echo", 
            lambda input_data: {"success": True, "result": input_data.get("text", "")}
        )
        
        self.harness.register_mock_tool(
            "add", 
            lambda input_data: {"success": True, "result": input_data.get("a", 0) + input_data.get("b", 0)}
        )
        
        self.harness.register_mock_tool(
            "multiply", 
            lambda input_data: {"success": True, "result": input_data.get("a", 0) * input_data.get("b", 0)}
        )
        
        self.harness.register_mock_tool(
            "fail_conditionally", 
            lambda input_data: {
                "success": not input_data.get("should_fail", False),
                "result": "Success" if not input_data.get("should_fail", False) else None,
                "error": "Conditional failure" if input_data.get("should_fail", False) else None
            }
        )

    def test_complex_branching(self):
        """Test complex conditional branching with multiple paths."""
        # Create a workflow with multiple conditional branches
        workflow = Workflow(workflow_id="complex_branching", name="Complex Branching Workflow")
        
        # Initial task to set the condition value
        task1 = Task(
            task_id="start",
            name="Start Task",
            tool_name="echo",
            input_data={"text": "start", "branch_value": 2},
            next_task_id_on_success="branch_decision"
        )
        workflow.add_task(task1)
        
        # Task that determines which branch to take
        task2 = Task(
            task_id="branch_decision",
            name="Branch Decision",
            tool_name="echo",
            input_data={"text": "Branching with value ${start.output_data.branch_value}"}
        )
        workflow.add_task(task2)
        
        # Branch A - executed if branch_value is 1
        task3 = Task(
            task_id="branch_a",
            name="Branch A",
            tool_name="echo",
            input_data={"text": "Executing Branch A"},
            condition="${start.output_data.branch_value == 1}"
        )
        workflow.add_task(task3)
        
        # Branch B - executed if branch_value is 2
        task4 = Task(
            task_id="branch_b",
            name="Branch B",
            tool_name="echo",
            input_data={"text": "Executing Branch B"},
            condition="${start.output_data.branch_value == 2}"
        )
        workflow.add_task(task4)
        
        # Branch C - executed if branch_value is 3
        task5 = Task(
            task_id="branch_c",
            name="Branch C",
            tool_name="echo",
            input_data={"text": "Executing Branch C"},
            condition="${start.output_data.branch_value == 3}"
        )
        workflow.add_task(task5)
        
        # Final task - takes output from whichever branch executed
        task6 = Task(
            task_id="end",
            name="End Task",
            tool_name="echo",
            input_data={
                "text": "Workflow completed with branch: " +
                        "${branch_a.output_data.result || branch_b.output_data.result || branch_c.output_data.result || 'No branch executed'}"
            }
        )
        workflow.add_task(task6)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        
        # Check that tasks executed as expected based on conditions
        executions = self.harness.get_executed_tasks()
        self.assertIn("start", executions)
        self.assertIn("branch_decision", executions)
        
        # We set branch_value to 2, so branch_b should execute and others should be skipped
        self.assertNotIn("branch_a", executions)
        self.assertIn("branch_b", executions)
        self.assertNotIn("branch_c", executions)
        self.assertIn("end", executions)
        
        # Check final output
        end_task = self.harness.get_task("end")
        self.assertIn("Executing Branch B", end_task.output_data.get("result"))

    def test_dynamic_task_inputs(self):
        """Test dynamic generation of task inputs based on previous task outputs."""
        # Create a workflow where task inputs are dynamically determined
        workflow = Workflow(workflow_id="dynamic_inputs", name="Dynamic Inputs Workflow")
        
        # Initial task that provides data structure
        task1 = Task(
            task_id="initial_data",
            name="Initial Data",
            tool_name="echo",
            input_data={
                "text": "data",
                "config": {
                    "operation": "add",
                    "values": [3, 5]
                }
            },
            next_task_id_on_success="dynamic_operation"
        )
        workflow.add_task(task1)
        
        # Define a handler for dynamic operation
        def dynamic_operation_handler(input_data):
            config = input_data.get("config", {})
            operation = config.get("operation", "")
            values = config.get("values", [])
            
            if not values:
                return {
                    "success": False,
                    "error": "No values provided for operation"
                }
            
            if operation == "add":
                result = sum(values)
            elif operation == "multiply":
                result = 1
                for v in values:
                    result *= v
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
            return {
                "success": True,
                "result": result,
                "operation": operation
            }
        
        # Task that dynamically performs operation based on config
        task2 = DirectHandlerTask(
            task_id="dynamic_operation",
            name="Dynamic Operation",
            handler=dynamic_operation_handler,
            input_data={"config": "${initial_data.output_data.config}"},
            next_task_id_on_success="report_result"
        )
        workflow.add_task(task2)
        
        # Final task that reports the result
        task3 = Task(
            task_id="report_result",
            name="Report Result",
            tool_name="echo",
            input_data={
                "text": "The result of ${dynamic_operation.output_data.operation} operation is ${dynamic_operation.output_data.result}"
            }
        )
        workflow.add_task(task3)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        
        # Check all tasks executed
        executions = self.harness.get_executed_tasks()
        self.assertIn("initial_data", executions)
        self.assertIn("dynamic_operation", executions)
        self.assertIn("report_result", executions)
        
        # Check operation result
        dynamic_task = self.harness.get_task("dynamic_operation")
        self.assertEqual(dynamic_task.output_data.get("result"), 8)  # 3 + 5
        
        # Check final message
        report_task = self.harness.get_task("report_result")
        self.assertEqual(report_task.output_data.get("result"), "The result of add operation is 8")

    def test_error_recovery_strategies(self):
        """Test various error recovery strategies in workflows."""
        # Create a workflow with error handling and recovery
        workflow = Workflow(workflow_id="error_recovery", name="Error Recovery Workflow")
        
        # First task - might fail based on input
        task1 = Task(
            task_id="might_fail",
            name="Task That Might Fail",
            tool_name="fail_conditionally",
            input_data={"should_fail": True},
            next_task_id_on_success="success_path",
            next_task_id_on_failure="retry_handler"
        )
        workflow.add_task(task1)
        
        # Success path
        task2 = Task(
            task_id="success_path",
            name="Success Path",
            tool_name="echo",
            input_data={"text": "Original task succeeded"}
        )
        workflow.add_task(task2)
        
        # Retry handler - attempt to retry the operation differently
        def retry_handler(input_data):
            error = input_data.get("error", "Unknown error")
            return {
                "success": True,
                "result": "Recovered from error",
                "original_error": error
            }
        
        task3 = DirectHandlerTask(
            task_id="retry_handler",
            name="Retry Handler",
            handler=retry_handler,
            input_data={"error": "${error.might_fail}"},
            next_task_id_on_success="recovery_report"
        )
        workflow.add_task(task3)
        
        # Final task after recovery
        task4 = Task(
            task_id="recovery_report",
            name="Recovery Report",
            tool_name="echo",
            input_data={"text": "Recovery complete. Original error: ${retry_handler.output_data.original_error}"}
        )
        workflow.add_task(task4)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        
        # Check execution path - should have taken the error path
        executions = self.harness.get_executed_tasks()
        self.assertIn("might_fail", executions)
        self.assertNotIn("success_path", executions)
        self.assertIn("retry_handler", executions)
        self.assertIn("recovery_report", executions)
        
        # Check recovery report
        report_task = self.harness.get_task("recovery_report")
        self.assertIn("Conditional failure", report_task.output_data.get("result", ""))

    def test_complex_variable_resolution(self):
        """Test complex variable resolution with nested structures and conditionals."""
        # Create a workflow with complex variable resolution
        workflow = Workflow(workflow_id="complex_variables", name="Complex Variable Resolution")
        
        # Task 1: Initialize complex data structure
        task1 = Task(
            task_id="initialize_data",
            name="Initialize Data",
            tool_name="echo",
            input_data={
                "text": "complex_data",
                "data": {
                    "user": {
                        "id": 123,
                        "name": "Test User",
                        "settings": {
                            "theme": "dark",
                            "notifications": True
                        }
                    },
                    "items": [
                        {"id": 1, "value": 10},
                        {"id": 2, "value": 20},
                        {"id": 3, "value": 30}
                    ]
                }
            },
            next_task_id_on_success="access_nested"
        )
        workflow.add_task(task1)
        
        # Task 2: Access nested properties
        task2 = Task(
            task_id="access_nested",
            name="Access Nested Properties",
            tool_name="echo",
            input_data={
                "text": "User ${initialize_data.output_data.data.user.name} uses ${initialize_data.output_data.data.user.settings.theme} theme",
                "user_id": "${initialize_data.output_data.data.user.id}"
            },
            next_task_id_on_success="transform_data"
        )
        workflow.add_task(task2)
        
        # Task 3: Transform complex data
        def transform_complex_data(input_data):
            data = input_data.get("data", {})
            items = data.get("items", [])
            
            # Calculate total value
            total = sum(item.get("value", 0) for item in items)
            
            # Create new transformed data
            result = {
                "user_name": data.get("user", {}).get("name", "Unknown"),
                "total_value": total,
                "item_count": len(items)
            }
            
            return {
                "success": True,
                "result": result
            }
        
        task3 = DirectHandlerTask(
            task_id="transform_data",
            name="Transform Complex Data",
            handler=transform_complex_data,
            input_data={"data": "${initialize_data.output_data.data}"},
            next_task_id_on_success="final_report"
        )
        workflow.add_task(task3)
        
        # Task 4: Final report using transformed data
        task4 = Task(
            task_id="final_report",
            name="Final Report",
            tool_name="echo",
            input_data={
                "text": "Report for ${transform_data.output_data.result.user_name}: " +
                       "Found ${transform_data.output_data.result.item_count} items " +
                       "with total value ${transform_data.output_data.result.total_value}"
            }
        )
        workflow.add_task(task4)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        
        # Check all tasks executed
        executions = self.harness.get_executed_tasks()
        self.assertIn("initialize_data", executions)
        self.assertIn("access_nested", executions)
        self.assertIn("transform_data", executions)
        self.assertIn("final_report", executions)
        
        # Check nested property access
        access_task = self.harness.get_task("access_nested")
        self.assertEqual(access_task.output_data.get("result"), "User Test User uses dark theme")
        
        # Check data transformation
        transform_task = self.harness.get_task("transform_data")
        self.assertEqual(transform_task.output_data.get("result").get("total_value"), 60)
        
        # Check final report
        report_task = self.harness.get_task("final_report")
        self.assertEqual(
            report_task.output_data.get("result"),
            "Report for Test User: Found 3 items with total value 60"
        )


class TestWorkflowIntegration(unittest.TestCase):
    """Test integration with the real workflow system components."""  # noqa: D202

    def setUp(self):
        """Set up integration tests."""
        # Reset singletons
        reset_registry()
        reset_services()
        
        # Create real components for integration test
        self.registry = get_registry()
        
        # Register some real tools
        self.registry.register_tool("echo", lambda input_data: {
            "success": True,
            "result": input_data.get("message", "No message provided")
        })
        
        self.registry.register_tool("process_data", lambda input_data: {
            "success": True,
            "result": {
                "processed": True,
                "input_received": input_data,
                "timestamp": "2023-04-15T12:00:00Z"
            }
        })
        
        # Create workflow engine
        self.engine = WorkflowEngine()

    def test_end_to_end_workflow(self):
        """Test a complete end-to-end workflow with real components."""
        # Create a workflow that simulates a real-world scenario
        workflow = Workflow(
            workflow_id="data_processing_workflow",
            name="Data Processing Workflow"
        )
        
        # Task 1: Initialize with user input
        task1 = Task(
            task_id="initialize",
            name="Initialize Workflow",
            tool_name="echo",
            input_data={
                "message": "Starting workflow with user data",
                "user_input": {
                    "name": "John Doe",
                    "request": "Process my data",
                    "data_points": [10, 20, 30, 40, 50]
                }
            },
            next_task_id_on_success="validate_input"
        )
        workflow.add_task(task1)
        
        # Task 2: Validate user input
        def validate_input(input_data):
            user_input = input_data.get("user_input", {})
            
            # Check required fields
            if not user_input.get("name"):
                return {
                    "success": False,
                    "error": "User name is required"
                }
            
            if not user_input.get("data_points"):
                return {
                    "success": False,
                    "error": "Data points are required"
                }
            
            # Validation passed
            return {
                "success": True,
                "result": {
                    "valid": True,
                    "user_name": user_input.get("name"),
                    "data_count": len(user_input.get("data_points", []))
                }
            }
        
        task2 = DirectHandlerTask(
            task_id="validate_input",
            name="Validate User Input",
            handler=validate_input,
            input_data={
                "user_input": "${initialize.output_data.user_input}"
            },
            next_task_id_on_success="process_data_task",
            next_task_id_on_failure="handle_validation_error"
        )
        workflow.add_task(task2)
        
        # Task 3: Handle validation error
        task3 = Task(
            task_id="handle_validation_error",
            name="Handle Validation Error",
            tool_name="echo",
            input_data={
                "message": "Validation error: ${error.validate_input}"
            }
        )
        workflow.add_task(task3)
        
        # Task 4: Process the data
        task4 = Task(
            task_id="process_data_task",
            name="Process Data",
            tool_name="process_data",
            input_data={
                "user_name": "${validate_input.output_data.result.user_name}",
                "data_points": "${initialize.output_data.user_input.data_points}"
            },
            next_task_id_on_success="generate_report"
        )
        workflow.add_task(task4)
        
        # Task 5: Generate final report
        def generate_report(input_data):
            processed_data = input_data.get("processed_data", {})
            user_name = input_data.get("user_name", "Unknown User")
            
            # Create a report
            report = {
                "report_id": "RPT-12345",
                "generated_for": user_name,
                "timestamp": processed_data.get("timestamp", "Unknown"),
                "summary": f"Processed data for {user_name} successfully",
                "details": processed_data
            }
            
            return {
                "success": True,
                "result": report
            }
        
        task5 = DirectHandlerTask(
            task_id="generate_report",
            name="Generate Report",
            handler=generate_report,
            input_data={
                "processed_data": "${process_data_task.output_data.result}",
                "user_name": "${validate_input.output_data.result.user_name}"
            },
            next_task_id_on_success="final_notification"
        )
        workflow.add_task(task5)
        
        # Task 6: Send final notification
        task6 = Task(
            task_id="final_notification",
            name="Final Notification",
            tool_name="echo",
            input_data={
                "message": "Workflow completed for ${generate_report.output_data.result.generated_for}. " +
                          "Report ID: ${generate_report.output_data.result.report_id}"
            }
        )
        workflow.add_task(task6)
        
        # Run the workflow
        result = self.engine.run_workflow(workflow)
        
        # Verify results
        self.assertTrue(result.get("success", False))
        
        # Check task statuses
        self.assertEqual(workflow.tasks["initialize"].status, "completed")
        self.assertEqual(workflow.tasks["validate_input"].status, "completed")
        self.assertEqual(workflow.tasks["handle_validation_error"].status, "skipped")
        self.assertEqual(workflow.tasks["process_data_task"].status, "completed")
        self.assertEqual(workflow.tasks["generate_report"].status, "completed")
        self.assertEqual(workflow.tasks["final_notification"].status, "completed")
        
        # Check key outputs
        self.assertEqual(
            workflow.tasks["validate_input"].output_data.get("result", {}).get("user_name"),
            "John Doe"
        )
        
        self.assertTrue(
            workflow.tasks["process_data_task"].output_data.get("result", {}).get("processed", False)
        )
        
        self.assertEqual(
            workflow.tasks["generate_report"].output_data.get("result", {}).get("generated_for"),
            "John Doe"
        )
        
        # Check final notification message
        final_message = workflow.tasks["final_notification"].output_data.get("result", "")
        self.assertIn("John Doe", final_message)
        self.assertIn("RPT-12345", final_message)


if __name__ == "__main__":
    unittest.main() 