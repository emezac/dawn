#!/usr/bin/env python3
"""
Integration Tests for Error Handling in Workflows

This module tests the error handling capabilities of the Dawn workflow engine,
ensuring that errors are properly caught, processed, and workflows can recover
or fail gracefully in various error scenarios.
"""  # noqa: D202

import unittest
import os
import sys
import logging
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import workflow components
from core.workflow import Workflow
from core.task import Task
from core.engine import WorkflowEngine
from core.utils.testing import MockToolRegistry, WorkflowTestHarness

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestErrorHandling(unittest.TestCase):
    """Test suite for error handling in workflows."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Create a clean test harness
        self.harness = WorkflowTestHarness()
        
        # Register tools for testing
        def success_tool(input_data):
            """Tool that always succeeds."""
            return {
                "success": True,
                "message": "Operation completed successfully",
                "data": input_data
            }
        
        def fail_tool(input_data):
            """Tool that always fails."""
            error_message = input_data.get("error_message", "Generic error occurred")
            error_type = input_data.get("error_type", "GenericError")
            
            if error_type == "ValueError":
                raise ValueError(error_message)
            elif error_type == "TypeError":
                raise TypeError(error_message)
            elif error_type == "KeyError":
                raise KeyError(error_message)
            elif error_type == "Exception":
                raise Exception(error_message)
            else:
                # Return failed response without raising exception
                return {
                    "success": False,
                    "error": error_message
                }
        
        def conditional_fail_tool(input_data):
            """Tool that fails based on input conditions."""
            should_fail = input_data.get("should_fail", False)
            fail_chance = input_data.get("fail_chance", 0)
            
            if should_fail or (fail_chance > 0):
                return {
                    "success": False,
                    "error": "Conditional failure triggered",
                    "input_data": input_data
                }
            else:
                return {
                    "success": True,
                    "message": "Operation completed successfully",
                    "data": input_data
                }
        
        def recovery_tool(input_data):
            """Tool that attempts to recover from errors."""
            error = input_data.get("error", None)
            original_data = input_data.get("original_data", {})
            
            if error:
                return {
                    "success": True,
                    "message": f"Recovered from error: {error}",
                    "recovered_data": original_data,
                    "is_recovery": True
                }
            else:
                return {
                    "success": True,
                    "message": "No recovery needed",
                    "data": original_data
                }
                
        # Register tools
        self.harness.register_mock_tool("success_tool", success_tool)
        self.harness.register_mock_tool("fail_tool", fail_tool)
        self.harness.register_mock_tool("conditional_fail_tool", conditional_fail_tool)
        self.harness.register_mock_tool("recovery_tool", recovery_tool)
    
    def test_basic_error_handling(self):
        """Test basic error handling with explicit error branches."""
        workflow = Workflow(workflow_id="basic_error_test", name="Basic Error Handling")
        
        # Task 1: This task will fail
        fail_task = Task(
            task_id="deliberate_fail",
            name="Deliberately Fail",
            tool_name="fail_tool",
            input_data={
                "error_message": "This is a deliberate failure",
                "error_type": "GenericError"
            },
            next_task_id_on_success="should_not_reach",
            next_task_id_on_error="handle_error"
        )
        workflow.add_task(fail_task)
        
        # Task 2a: Success path (should not be reached)
        success_path_task = Task(
            task_id="should_not_reach",
            name="Should Not Reach",
            tool_name="success_tool",
            input_data={
                "message": "This task should not be executed"
            }
        )
        workflow.add_task(success_path_task)
        
        # Task 2b: Error handling path
        error_handler_task = Task(
            task_id="handle_error",
            name="Handle Error",
            tool_name="recovery_tool",
            input_data={
                "error": "${deliberate_fail.error}",
                "original_data": "${deliberate_fail.input_data}"
            },
            next_task_id_on_success="final_task"
        )
        workflow.add_task(error_handler_task)
        
        # Task 3: Final task
        final_task = Task(
            task_id="final_task",
            name="Final Task",
            tool_name="success_tool",
            input_data={
                "message": "Workflow completed with error handling",
                "recovery_result": "${handle_error.output_data}"
            }
        )
        workflow.add_task(final_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully despite the error
        self.assertTrue(result.get("success", False))
        
        # Check which tasks were executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("deliberate_fail", executed_tasks)
        self.assertIn("handle_error", executed_tasks)
        self.assertIn("final_task", executed_tasks)
        self.assertNotIn("should_not_reach", executed_tasks)
        
        # Verify task statuses
        deliberate_fail_task = self.harness.get_task("deliberate_fail")
        self.assertFalse(deliberate_fail_task.success)
        self.assertIsNotNone(deliberate_fail_task.error)
        
        error_handler_task = self.harness.get_task("handle_error")
        self.assertTrue(error_handler_task.success)
        self.assertEqual(error_handler_task.output_data.get("is_recovery"), True)
        
        final_task = self.harness.get_task("final_task")
        self.assertTrue(final_task.success)

    def test_exception_handling(self):
        """Test handling of actual exceptions thrown by tools."""
        workflow = Workflow(workflow_id="exception_test", name="Exception Handling")
        
        # Task 1: This task will throw an exception
        exception_task = Task(
            task_id="throw_exception",
            name="Throw Exception",
            tool_name="fail_tool",
            input_data={
                "error_message": "This is a deliberate exception",
                "error_type": "ValueError"
            },
            next_task_id_on_success="success_path",
            next_task_id_on_error="handle_exception"
        )
        workflow.add_task(exception_task)
        
        # Task 2a: Success path
        success_path_task = Task(
            task_id="success_path",
            name="Success Path",
            tool_name="success_tool",
            input_data={
                "message": "This task should not be executed"
            }
        )
        workflow.add_task(success_path_task)
        
        # Task 2b: Exception handler
        exception_handler_task = Task(
            task_id="handle_exception",
            name="Handle Exception",
            tool_name="recovery_tool",
            input_data={
                "error": "${throw_exception.error}",
                "original_data": "${throw_exception.input_data}"
            }
        )
        workflow.add_task(exception_handler_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed but with error indication
        self.assertTrue(result.get("success", False))
        
        # Check which tasks were executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("throw_exception", executed_tasks)
        self.assertIn("handle_exception", executed_tasks)
        self.assertNotIn("success_path", executed_tasks)
        
        # Verify the exception was properly captured and handled
        exception_task = self.harness.get_task("throw_exception")
        self.assertFalse(exception_task.success)
        self.assertIsNotNone(exception_task.error)
        self.assertIn("ValueError", str(exception_task.error))
        
        exception_handler_task = self.harness.get_task("handle_exception")
        self.assertTrue(exception_handler_task.success)
        self.assertEqual(exception_handler_task.output_data.get("is_recovery"), True)

    def test_multiple_error_paths(self):
        """Test handling different types of errors with specific error paths."""
        workflow = Workflow(workflow_id="multi_error_test", name="Multiple Error Paths")
        
        # Setup initial workflow variables
        workflow.variables = {
            "error_type": "TypeError"  # This determines which error to trigger
        }
        
        # Task 1: This task will generate a specific type of error
        error_generator_task = Task(
            task_id="generate_error",
            name="Generate Error",
            tool_name="fail_tool",
            input_data={
                "error_message": "Generated error for testing",
                "error_type": "${workflow.variables.error_type}"
            },
            # Different error paths based on error type
            next_task_id_on_success="no_error_path",
            next_task_id_on_error={
                "path_conditions": [
                    {"condition": "${contains(error, 'ValueError')}", "task_id": "handle_value_error"},
                    {"condition": "${contains(error, 'TypeError')}", "task_id": "handle_type_error"},
                    {"condition": "${contains(error, 'KeyError')}", "task_id": "handle_key_error"}
                ],
                "default_task_id": "handle_generic_error"
            }
        )
        workflow.add_task(error_generator_task)
        
        # Task 2a: No error path
        no_error_task = Task(
            task_id="no_error_path",
            name="No Error Path",
            tool_name="success_tool",
            input_data={"message": "No error occurred"}
        )
        workflow.add_task(no_error_task)
        
        # Task 2b: Handle ValueError
        value_error_task = Task(
            task_id="handle_value_error",
            name="Handle Value Error",
            tool_name="recovery_tool",
            input_data={
                "error": "${generate_error.error}",
                "original_data": "${generate_error.input_data}",
                "error_type": "ValueError"
            },
            next_task_id_on_success="final_reporting"
        )
        workflow.add_task(value_error_task)
        
        # Task 2c: Handle TypeError
        type_error_task = Task(
            task_id="handle_type_error",
            name="Handle Type Error",
            tool_name="recovery_tool",
            input_data={
                "error": "${generate_error.error}",
                "original_data": "${generate_error.input_data}",
                "error_type": "TypeError"
            },
            next_task_id_on_success="final_reporting"
        )
        workflow.add_task(type_error_task)
        
        # Task 2d: Handle KeyError
        key_error_task = Task(
            task_id="handle_key_error",
            name="Handle Key Error",
            tool_name="recovery_tool",
            input_data={
                "error": "${generate_error.error}",
                "original_data": "${generate_error.input_data}",
                "error_type": "KeyError"
            },
            next_task_id_on_success="final_reporting"
        )
        workflow.add_task(key_error_task)
        
        # Task 2e: Handle generic error
        generic_error_task = Task(
            task_id="handle_generic_error",
            name="Handle Generic Error",
            tool_name="recovery_tool",
            input_data={
                "error": "${generate_error.error}",
                "original_data": "${generate_error.input_data}",
                "error_type": "GenericError"
            },
            next_task_id_on_success="final_reporting"
        )
        workflow.add_task(generic_error_task)
        
        # Task 3: Final reporting task
        final_task = Task(
            task_id="final_reporting",
            name="Final Reporting",
            tool_name="success_tool",
            input_data={
                "message": "Error was handled",
                "error_type": "${workflow.variables.error_type}"
            }
        )
        workflow.add_task(final_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that the correct error handler was executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("generate_error", executed_tasks)
        self.assertIn("handle_type_error", executed_tasks)
        self.assertIn("final_reporting", executed_tasks)
        self.assertNotIn("no_error_path", executed_tasks)
        self.assertNotIn("handle_value_error", executed_tasks)
        self.assertNotIn("handle_key_error", executed_tasks)
        self.assertNotIn("handle_generic_error", executed_tasks)
        
        # Verify error details
        error_task = self.harness.get_task("generate_error")
        self.assertFalse(error_task.success)
        self.assertIn("TypeError", str(error_task.error))
        
        # Now change the error type and rerun to test another path
        workflow.variables = {"error_type": "ValueError"}
        result = self.harness.run_workflow(workflow)
        
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("handle_value_error", executed_tasks)
        self.assertNotIn("handle_type_error", executed_tasks)
        
        # Test generic error fallback
        workflow.variables = {"error_type": "UnknownError"}
        result = self.harness.run_workflow(workflow)
        
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("handle_generic_error", executed_tasks)

    def test_retry_mechanism(self):
        """Test task retry mechanism for transient errors."""
        workflow = Workflow(workflow_id="retry_test", name="Retry Mechanism")
        
        # Task that will fail initially but succeed on retry
        retry_task = Task(
            task_id="retry_task",
            name="Task With Retry",
            tool_name="conditional_fail_tool",
            input_data={
                "should_fail": True,  # Will be changed by retry mechanism
                "retry_count": 0      # Will be incremented by retry logic
            },
            # Retry configuration
            retry={
                "max_attempts": 3,
                "retry_variable_updates": {
                    "should_fail": "${retry_count >= 2 ? false : true}",  # Succeed on 3rd attempt
                    "retry_count": "${retry_count + 1}"
                }
            },
            next_task_id_on_success="success_after_retry",
            next_task_id_on_error="handle_retry_failure"
        )
        workflow.add_task(retry_task)
        
        # Task for successful retry
        success_after_retry_task = Task(
            task_id="success_after_retry",
            name="Success After Retry",
            tool_name="success_tool",
            input_data={
                "message": "Task succeeded after retry",
                "retry_count": "${retry_task.input_data.retry_count}"
            }
        )
        workflow.add_task(success_after_retry_task)
        
        # Task for retry failure
        handle_retry_failure_task = Task(
            task_id="handle_retry_failure",
            name="Handle Retry Failure",
            tool_name="recovery_tool",
            input_data={
                "error": "Max retries exceeded",
                "original_data": "${retry_task.input_data}"
            }
        )
        workflow.add_task(handle_retry_failure_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that the task was retried and eventually succeeded
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("retry_task", executed_tasks)
        self.assertIn("success_after_retry", executed_tasks)
        self.assertNotIn("handle_retry_failure", executed_tasks)
        
        # Verify retry count
        retry_task = self.harness.get_task("retry_task")
        self.assertTrue(retry_task.success)
        self.assertEqual(retry_task.input_data.get("retry_count"), 3)  # Retry count should be 3
        
        # Now test a scenario where max retries are exceeded
        # Create a new workflow where retry will always fail
        workflow_fail = Workflow(workflow_id="retry_fail_test", name="Retry Failure")
        
        # Task that will always fail despite retries
        always_fail_task = Task(
            task_id="always_fail_task",
            name="Always Fail Despite Retry",
            tool_name="conditional_fail_tool",
            input_data={
                "should_fail": True,
                "retry_count": 0
            },
            # Retry configuration (will always fail)
            retry={
                "max_attempts": 2,
                "retry_variable_updates": {
                    "should_fail": True,  # Always fail
                    "retry_count": "${retry_count + 1}"
                }
            },
            next_task_id_on_success="should_not_reach_success",
            next_task_id_on_error="handle_max_retries"
        )
        workflow_fail.add_task(always_fail_task)
        
        # Success path (should not reach)
        success_task = Task(
            task_id="should_not_reach_success",
            name="Should Not Reach Success",
            tool_name="success_tool",
            input_data={"message": "This should not be reached"}
        )
        workflow_fail.add_task(success_task)
        
        # Error path after max retries
        handle_max_retries_task = Task(
            task_id="handle_max_retries",
            name="Handle Max Retries",
            tool_name="recovery_tool",
            input_data={
                "error": "Max retries exceeded",
                "original_data": "${always_fail_task.input_data}",
                "retry_count": "${always_fail_task.input_data.retry_count}"
            }
        )
        workflow_fail.add_task(handle_max_retries_task)
        
        # Run the workflow
        result_fail = self.harness.run_workflow(workflow_fail)
        
        # Verify workflow still completed (with handled error)
        self.assertTrue(result_fail.get("success", False))
        
        # Check that the error handler was executed after max retries
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("always_fail_task", executed_tasks)
        self.assertIn("handle_max_retries", executed_tasks)
        self.assertNotIn("should_not_reach_success", executed_tasks)
        
        # Verify retry count and that task ultimately failed
        always_fail_task = self.harness.get_task("always_fail_task")
        self.assertFalse(always_fail_task.success)
        self.assertEqual(always_fail_task.input_data.get("retry_count"), 2)  # Should have tried 2 times

    def test_parallel_error_handling(self):
        """Test error handling in parallel task execution."""
        workflow = Workflow(workflow_id="parallel_error_test", name="Parallel Error Handling")
        
        # Initial task
        start_task = Task(
            task_id="start_task",
            name="Start Task",
            tool_name="success_tool",
            input_data={"message": "Starting parallel tasks"},
            next_task_ids=["parallel_success_1", "parallel_success_2", "parallel_fail"]
        )
        workflow.add_task(start_task)
        
        # Parallel task 1 (succeeds)
        parallel_success_1 = Task(
            task_id="parallel_success_1",
            name="Parallel Success 1",
            tool_name="success_tool",
            input_data={"message": "Parallel task 1 succeeds"},
            next_task_id_on_success="join_task"
        )
        workflow.add_task(parallel_success_1)
        
        # Parallel task 2 (succeeds)
        parallel_success_2 = Task(
            task_id="parallel_success_2",
            name="Parallel Success 2",
            tool_name="success_tool",
            input_data={"message": "Parallel task 2 succeeds"},
            next_task_id_on_success="join_task"
        )
        workflow.add_task(parallel_success_2)
        
        # Parallel task 3 (fails)
        parallel_fail = Task(
            task_id="parallel_fail",
            name="Parallel Fail",
            tool_name="fail_tool",
            input_data={
                "error_message": "This parallel task fails",
                "error_type": "Exception"
            },
            next_task_id_on_success="join_task",
            next_task_id_on_error="handle_parallel_error"
        )
        workflow.add_task(parallel_fail)
        
        # Error handler for parallel task
        handle_parallel_error = Task(
            task_id="handle_parallel_error",
            name="Handle Parallel Error",
            tool_name="recovery_tool",
            input_data={
                "error": "${parallel_fail.error}",
                "original_data": "${parallel_fail.input_data}"
            },
            next_task_id_on_success="join_task"
        )
        workflow.add_task(handle_parallel_error)
        
        # Join task (waits for all parallel branches)
        join_task = Task(
            task_id="join_task",
            name="Join Task",
            tool_name="success_tool",
            input_data={
                "message": "All parallel tasks completed or handled",
                "successful_paths": ["${parallel_success_1.success}", "${parallel_success_2.success}"],
                "failed_paths": ["${parallel_fail.success}"],
                "error_handled": "${handle_parallel_error.success}"
            },
            join_type="all"  # Wait for all incoming branches
        )
        workflow.add_task(join_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that all tasks were executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("start_task", executed_tasks)
        self.assertIn("parallel_success_1", executed_tasks)
        self.assertIn("parallel_success_2", executed_tasks)
        self.assertIn("parallel_fail", executed_tasks)
        self.assertIn("handle_parallel_error", executed_tasks)
        self.assertIn("join_task", executed_tasks)
        
        # Verify task statuses
        self.assertTrue(self.harness.get_task("parallel_success_1").success)
        self.assertTrue(self.harness.get_task("parallel_success_2").success)
        self.assertFalse(self.harness.get_task("parallel_fail").success)
        self.assertTrue(self.harness.get_task("handle_parallel_error").success)
        self.assertTrue(self.harness.get_task("join_task").success)
        
        # Verify join task received correct data
        join_task = self.harness.get_task("join_task")
        self.assertEqual(join_task.input_data.get("successful_paths"), [True, True])
        self.assertEqual(join_task.input_data.get("failed_paths"), [False])
        self.assertEqual(join_task.input_data.get("error_handled"), True)

    def test_task_timeout_handling(self):
        """Test handling of task timeouts."""
        workflow = Workflow(workflow_id="timeout_test", name="Task Timeout Handling")
        
        # Task with timeout
        timeout_task = Task(
            task_id="timeout_task",
            name="Task With Timeout",
            tool_name="fail_tool",  # We'll use fail_tool to simulate a long-running task
            input_data={
                "error_message": "This task would normally time out",
                "error_type": "TimeoutError"
            },
            timeout_seconds=1,  # Very short timeout for testing
            next_task_id_on_success="should_not_reach",
            next_task_id_on_timeout="handle_timeout",
            next_task_id_on_error="handle_other_error"
        )
        workflow.add_task(timeout_task)
        
        # Success path (should not be reached)
        success_path = Task(
            task_id="should_not_reach",
            name="Should Not Reach",
            tool_name="success_tool",
            input_data={"message": "This should not be reached"}
        )
        workflow.add_task(success_path)
        
        # Timeout handler
        timeout_handler = Task(
            task_id="handle_timeout",
            name="Handle Timeout",
            tool_name="recovery_tool",
            input_data={
                "error": "Task timed out",
                "original_data": "${timeout_task.input_data}"
            }
        )
        workflow.add_task(timeout_handler)
        
        # Other error handler
        other_error_handler = Task(
            task_id="handle_other_error",
            name="Handle Other Error",
            tool_name="recovery_tool",
            input_data={
                "error": "${timeout_task.error}",
                "original_data": "${timeout_task.input_data}"
            }
        )
        workflow.add_task(other_error_handler)
        
        # Mock the workflow engine's timeout detection
        # This requires a special setup in the test harness
        self.harness.mock_timeout("timeout_task")
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed
        self.assertTrue(result.get("success", False))
        
        # Check that timeout handler was executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("timeout_task", executed_tasks)
        self.assertIn("handle_timeout", executed_tasks)
        self.assertNotIn("should_not_reach", executed_tasks)
        self.assertNotIn("handle_other_error", executed_tasks)
        
        # Verify task status
        timeout_task = self.harness.get_task("timeout_task")
        self.assertFalse(timeout_task.success)
        self.assertTrue(timeout_task.timed_out)


if __name__ == "__main__":
    unittest.main() 