#!/usr/bin/env python3
"""
Integration Tests for Workflow Retry Mechanism

This module tests the retry mechanism in the Dawn workflow engine,
verifying that tasks can be retried after temporary failures.
"""  # noqa: D202

import unittest
import os
import sys
import logging
import time
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


class TestRetryMechanism(unittest.TestCase):
    """Test suite for workflow retry mechanisms."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Reset singletons
        reset_registry()
        reset_services()
        
        # Create a clean test harness
        self.harness = WorkflowTestHarness()
        
        # Track call counts for mock tools to verify retry behavior
        self.call_counts = {}
        
        # Register a transient failing tool that will succeed after a few attempts
        def transient_failing_tool(input_data):
            tool_name = "transient_failing_tool"
            self.call_counts[tool_name] = self.call_counts.get(tool_name, 0) + 1
            
            # Succeed after 3 attempts
            if self.call_counts[tool_name] >= 3:
                return {
                    "success": True,
                    "result": f"Success on attempt {self.call_counts[tool_name]}"
                }
            
            # Otherwise fail
            return {
                "success": False,
                "error": f"Temporary failure on attempt {self.call_counts[tool_name]}",
                "error_code": "TEMP_FAILURE"
            }
        
        self.harness.register_mock_tool("transient_failing_tool", transient_failing_tool)
        
        # Register a permanently failing tool
        def permanent_failing_tool(input_data):
            tool_name = "permanent_failing_tool"
            self.call_counts[tool_name] = self.call_counts.get(tool_name, 0) + 1
            
            return {
                "success": False,
                "error": f"Permanent failure on attempt {self.call_counts[tool_name]}",
                "error_code": "PERM_FAILURE"
            }
        
        self.harness.register_mock_tool("permanent_failing_tool", permanent_failing_tool)
        
        # Register a dependency tool that works normally
        def echo_tool(input_data):
            tool_name = "echo_tool"
            self.call_counts[tool_name] = self.call_counts.get(tool_name, 0) + 1
            
            return {
                "success": True,
                "result": input_data.get("message", "Default echo message")
            }
        
        self.harness.register_mock_tool("echo_tool", echo_tool)

    def test_automatic_retry_of_failing_task(self):
        """Test that a task with temporary failures is automatically retried."""
        workflow = Workflow(workflow_id="retry_workflow", name="Retry Workflow")
        
        # Task 1: A task that will fail temporarily
        task1 = Task(
            task_id="retry_task",
            name="Task That Needs Retry",
            tool_name="transient_failing_tool",
            input_data={},
            retry_config={
                "max_retries": 5,
                "retry_delay": 0.1  # Short delay for tests
            },
            next_task_id_on_success="success_task"
        )
        workflow.add_task(task1)
        
        # Task 2: Task to run after successful execution
        task2 = Task(
            task_id="success_task",
            name="Success Task",
            tool_name="echo_tool",
            input_data={
                "message": "All retries succeeded!"
            }
        )
        workflow.add_task(task2)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow succeeded
        self.assertTrue(result.get("success", False))
        
        # Check that the transient failing tool was called the right number of times
        self.assertEqual(self.call_counts["transient_failing_tool"], 3)
        
        # Verify the success task was executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("retry_task", executed_tasks)
        self.assertIn("success_task", executed_tasks)
        
        # Check the final result
        retry_task = self.harness.get_task("retry_task")
        self.assertTrue(retry_task.output_data.get("success"))
        self.assertIn("Success on attempt 3", retry_task.output_data.get("result"))

    def test_retry_with_different_input(self):
        """Test retrying a task with modified input data on each attempt."""
        workflow = Workflow(workflow_id="retry_with_input_mod", name="Retry With Input Modification")
        
        # Create a tool that checks for a specific flag
        def check_retry_flag(input_data):
            tool_name = "check_retry_flag"
            self.call_counts[tool_name] = self.call_counts.get(tool_name, 0) + 1
            attempt = self.call_counts[tool_name]
            
            # Only succeed if retry_attempt flag is 3
            retry_attempt = input_data.get("retry_attempt", 1)
            if retry_attempt >= 3:
                return {
                    "success": True,
                    "result": f"Success on attempt {attempt} with flag {retry_attempt}"
                }
            
            return {
                "success": False,
                "error": f"Need higher retry attempt. Current: {retry_attempt}",
                "error_code": "RETRY_NEEDED"
            }
        
        self.harness.register_mock_tool("check_retry_flag", check_retry_flag)
        
        # Create a retry handler that increments the retry attempt flag
        def increment_retry_flag(input_data, error_data, attempt):
            current_attempt = input_data.get("retry_attempt", 1)
            return {
                "retry_attempt": current_attempt + 1,
                "last_error": error_data.get("error")
            }
        
        # Task with custom retry handler
        task1 = Task(
            task_id="incrementing_retry",
            name="Task With Incrementing Retry Flag",
            tool_name="check_retry_flag",
            input_data={"retry_attempt": 1},
            retry_config={
                "max_retries": 5,
                "retry_delay": 0.1,
                "retry_data_handler": increment_retry_flag
            },
            next_task_id_on_success="record_success"
        )
        workflow.add_task(task1)
        
        # Task to record success
        task2 = Task(
            task_id="record_success",
            name="Record Success",
            tool_name="echo_tool",
            input_data={
                "message": "Retry with input modification succeeded",
                "final_retry_attempt": "${incrementing_retry.input_data.retry_attempt}"
            }
        )
        workflow.add_task(task2)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow succeeded
        self.assertTrue(result.get("success", False))
        
        # Check call counts
        self.assertEqual(self.call_counts["check_retry_flag"], 3)
        
        # Verify both tasks executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("incrementing_retry", executed_tasks)
        self.assertIn("record_success", executed_tasks)
        
        # Check the retry task output
        retry_task = self.harness.get_task("incrementing_retry")
        self.assertTrue(retry_task.output_data.get("success"))
        
        # Check that the final input had the correct retry_attempt value
        record_task = self.harness.get_task("record_success")
        self.assertEqual(record_task.input_data.get("final_retry_attempt"), 3)

    def test_max_retries_exceeded(self):
        """Test that a workflow correctly handles a task exceeding max retries."""
        workflow = Workflow(workflow_id="max_retries", name="Max Retries Workflow")
        
        # Task 1: A permanently failing task
        task1 = Task(
            task_id="failing_task",
            name="Permanently Failing Task",
            tool_name="permanent_failing_tool",
            input_data={},
            retry_config={
                "max_retries": 3,
                "retry_delay": 0.1
            },
            next_task_id_on_success="never_reached",
            next_task_id_on_failure="handle_failure"
        )
        workflow.add_task(task1)
        
        # Task 2: Success path that should never be reached
        task2 = Task(
            task_id="never_reached",
            name="Success Path",
            tool_name="echo_tool",
            input_data={"message": "This should never be reached"}
        )
        workflow.add_task(task2)
        
        # Task 3: Failure handler
        task3 = Task(
            task_id="handle_failure",
            name="Failure Handler",
            tool_name="echo_tool",
            input_data={
                "message": "Task failed after max retries",
                "error": "${error.failing_task}",
                "error_code": "${error_code.failing_task}",
                "attempts": "${retry_count.failing_task}"
            }
        )
        workflow.add_task(task3)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed - note this will be success because the error handler completed
        self.assertTrue(result.get("success", False))
        
        # Check the failing tool was called the right number of times (including initial attempt)
        self.assertEqual(self.call_counts["permanent_failing_tool"], 4)
        
        # Verify execution path
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("failing_task", executed_tasks)
        self.assertNotIn("never_reached", executed_tasks)
        self.assertIn("handle_failure", executed_tasks)
        
        # Check error handler received the correct error information
        handler_task = self.harness.get_task("handle_failure")
        self.assertIn("Permanent failure", handler_task.input_data.get("error"))
        self.assertEqual(handler_task.input_data.get("error_code"), "PERM_FAILURE")
        self.assertEqual(handler_task.input_data.get("attempts"), 4)  # Initial + 3 retries

    def test_exponential_backoff(self):
        """Test retry with exponential backoff."""
        workflow = Workflow(workflow_id="backoff_workflow", name="Backoff Workflow")
        
        # Keep track of execution times
        execution_times = []
        
        def time_tracking_tool(input_data):
            tool_name = "time_tracking_tool"
            self.call_counts[tool_name] = self.call_counts.get(tool_name, 0) + 1
            execution_times.append(time.time())
            
            # Succeed on the 4th attempt
            if self.call_counts[tool_name] >= 4:
                return {
                    "success": True,
                    "result": f"Success after {self.call_counts[tool_name]} attempts"
                }
            
            return {
                "success": False,
                "error": "Time tracking failure",
                "error_code": "TRACKING_ERROR"
            }
        
        self.harness.register_mock_tool("time_tracking_tool", time_tracking_tool)
        
        # Task with exponential backoff
        task = Task(
            task_id="backoff_task",
            name="Exponential Backoff Task",
            tool_name="time_tracking_tool",
            input_data={},
            retry_config={
                "max_retries": 5,
                "retry_delay": 0.1,
                "backoff_factor": 2.0  # Double the delay on each retry
            }
        )
        workflow.add_task(task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow succeeded
        self.assertTrue(result.get("success", False))
        
        # Check that the tool was called the right number of times
        self.assertEqual(self.call_counts["time_tracking_tool"], 4)
        
        # Check that the delays between executions increased
        # Calculate delays between executions
        if len(execution_times) >= 4:
            delays = [execution_times[i] - execution_times[i-1] for i in range(1, len(execution_times))]
            
            # Each delay should be approximately double the previous one
            # Allow for some flexibility in timing due to test execution variability
            for i in range(1, len(delays)):
                self.assertGreaterEqual(delays[i], delays[i-1] * 1.5)  # Not exactly 2x due to processing overhead

    def test_conditional_retry(self):
        """Test conditional retry based on error type."""
        workflow = Workflow(workflow_id="conditional_retry", name="Conditional Retry Workflow")
        
        # Create a tool that returns different error types
        def error_type_tool(input_data):
            tool_name = "error_type_tool"
            self.call_counts[tool_name] = self.call_counts.get(tool_name, 0) + 1
            attempt = self.call_counts[tool_name]
            
            error_type = input_data.get("error_type", "transient")
            
            if attempt >= 3 and error_type == "transient":
                return {
                    "success": True,
                    "result": "Recovered from transient error"
                }
            
            return {
                "success": False,
                "error": f"{error_type.upper()} error on attempt {attempt}",
                "error_code": f"{error_type.upper()}_ERROR"
            }
        
        self.harness.register_mock_tool("error_type_tool", error_type_tool)
        
        # Create a retry condition function
        def should_retry(error_data, attempt):
            error_code = error_data.get("error_code", "")
            # Only retry for transient errors
            return "TRANSIENT" in error_code
        
        # Transient error task - should be retried
        task1 = Task(
            task_id="transient_error_task",
            name="Transient Error Task",
            tool_name="error_type_tool",
            input_data={"error_type": "transient"},
            retry_config={
                "max_retries": 5,
                "retry_delay": 0.1,
                "retry_condition": should_retry
            },
            next_task_id_on_success="echo_transient_success"
        )
        workflow.add_task(task1)
        
        # Success handler for transient task
        task2 = Task(
            task_id="echo_transient_success",
            name="Echo Transient Success",
            tool_name="echo_tool",
            input_data={"message": "Recovered from transient error"}
        )
        workflow.add_task(task2)
        
        # Permanent error task - should not be retried
        task3 = Task(
            task_id="permanent_error_task",
            name="Permanent Error Task",
            tool_name="error_type_tool",
            input_data={"error_type": "permanent"},
            retry_config={
                "max_retries": 5,
                "retry_delay": 0.1,
                "retry_condition": should_retry
            },
            next_task_id_on_success="never_reached",
            next_task_id_on_failure="echo_permanent_failure"
        )
        workflow.add_task(task3)
        
        # Failure handler for permanent task
        task4 = Task(
            task_id="echo_permanent_failure",
            name="Echo Permanent Failure",
            tool_name="echo_tool",
            input_data={"message": "Permanent error not retried"}
        )
        workflow.add_task(task4)
        
        # Run the workflow with transient error
        result1 = self.harness.run_workflow(workflow)
        
        # Reset for the second workflow
        self.call_counts = {}
        self.harness = WorkflowTestHarness()
        self.harness.register_mock_tool("error_type_tool", error_type_tool)
        self.harness.register_mock_tool("echo_tool", echo_tool)
        
        # Run the workflow with permanent error
        task1.next_task_id_on_success = None  # Modify to end workflow after first task
        task3.next_task_id_on_failure = None  # Modify to end workflow after error
        
        # Create a new workflow with just the permanent error task
        perm_workflow = Workflow(workflow_id="permanent_error", name="Permanent Error Workflow")
        perm_workflow.add_task(task3)
        result2 = self.harness.run_workflow(perm_workflow)
        
        # First workflow with transient error should have succeeded after retries
        self.assertTrue(result1.get("success", False))
        
        # Second workflow with permanent error should have failed immediately without retries
        self.assertFalse(result2.get("success", False))
        
        # Check call counts - transient should be 3, permanent should be 1
        self.assertEqual(self.call_counts["error_type_tool"], 1)  # No retries for permanent error


if __name__ == "__main__":
    unittest.main() 