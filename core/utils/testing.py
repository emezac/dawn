#!/usr/bin/env python3
"""
Testing utilities for Dawn workflows and tasks.

This module provides utilities for testing workflows and individual tasks
with mocked tool executions, allowing for unit testing without external dependencies.

Key components:
- create_mock_tool_execution: Creates a mock tool execution configuration
- workflow_test_context: Context manager for testing workflows with mocked tools
- WorkflowTestHarness: Class for testing complete workflows
- TaskTestHarness: Class for testing individual tasks
- ToolExecutionRecorder: Records tool executions for replay in tests
"""  # noqa: D202

import contextlib
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from contextlib import contextmanager
import re
import os
import json
import datetime
import time
import uuid
import inspect
import functools
from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch
from enum import Enum

# Update imports to match actual module structure
from core.task import Task
from core.workflow import Workflow
from core.tools.mock_registry import MockToolRegistry

# Define TaskStatus enum locally since it doesn't exist in core.task
class TaskStatus(Enum):
    """Task status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# ExecutionContext might be in one of these locations
try:
    from core.workflow.execution_context import ExecutionContext
except ImportError:
    try:
        from core.execution_context import ExecutionContext
    except ImportError:
        # If we can't find it, provide a simple implementation
        class ExecutionContext:
            def __init__(self, variables=None):
                self.variables = variables or {}
                self.task_data = {}


def create_mock_tool_execution(
    input_pattern: Dict[str, Any],
    output: Optional[Dict[str, Any]] = None,
    exception: Optional[Exception] = None
) -> Dict[str, Any]:
    """
    Create a mock tool execution configuration.
    
    Args:
        input_pattern: Dict specifying the input pattern to match.
            Values can be exact matches or callable functions that return a boolean.
        output: Dict containing the output to return when the input pattern matches.
        exception: Exception to raise when the input pattern matches.
    
    Returns:
        Dict containing the mock execution configuration.
    
    Example:
        >>> create_mock_tool_execution(
        ...     {"prompt": "Extract entities", "temperature": 0.7},
        ...     {"content": "Entity extraction result"}
        ... )
        
        >>> create_mock_tool_execution(
        ...     {"prompt": lambda p: "extract" in p.lower()},
        ...     {"content": "Entity extraction result"}
        ... )
        
        >>> create_mock_tool_execution(
        ...     {"path": "missing.pdf"},
        ...     exception=FileNotFoundError("File not found")
        ... )
    """
    return {
        "input_pattern": input_pattern,
        "output": output,
        "exception": exception
    }

@contextmanager
def workflow_test_context(
    workflow: Workflow,
    mock_executions: Dict[str, List[Dict[str, Any]]],
    initial_variables: Optional[Dict[str, Any]] = None
) -> Tuple[Workflow, 'WorkflowTestHarness']:
    """
    Context manager for testing a workflow with mocked tool executions.
    
    Args:
        workflow: The workflow instance to test.
        mock_executions: Dict mapping tool names to lists of mock execution configurations.
            Each configuration should be created with create_mock_tool_execution.
        initial_variables: Dict containing initial variables for the workflow.
    
    Yields:
        Tuple containing the workflow instance and a WorkflowTestHarness instance.
    
    Example:
        >>> workflow = MyWorkflow()
        >>> mock_executions = {
        ...     "openai": [
        ...         create_mock_tool_execution(
        ...             {"prompt": lambda p: "extract" in p.lower()},
        ...             {"content": "Entity extraction result"}
        ...         )
        ...     ]
        ... }
        >>> with workflow_test_context(workflow, mock_executions) as (workflow, harness):
        ...     result = harness.execute()
        ...     harness.assert_workflow_completed()
        ...     harness.assert_task_executed("extract_entities")
    """
    # Create a mock tool registry
    mock_registry = MockToolRegistry()
    
    # Configure mock executions
    for tool_name, executions in mock_executions.items():
        for mock_config in executions:
            input_pattern = mock_config.get("input_pattern", {})
            output = mock_config.get("output", {})
            exception = mock_config.get("exception")
            
            if exception:
                # Configure an exception to be raised
                mock_registry.mock_tool_as_failure(
                    tool_name, 
                    str(exception),
                )
            else:
                # Configure a success response
                mock_registry.add_mock_response(
                    tool_name,
                    input_pattern,
                    output or {}
                )
    
    # Set up workflow with the mock registry
    workflow.set_tool_registry(mock_registry)
    
    # Create a test harness
    harness = WorkflowTestHarness(workflow, mock_registry, initial_variables)
    
    try:
        # Yield the workflow and harness
        yield workflow, harness
    finally:
        # Clean up
        pass


class WorkflowTestHarness:
    """
    Test harness for workflows.
    
    This class helps test workflows by mocking tool executions and
    tracking executed tasks.
    
    Args:
        workflow: The workflow instance to test.
        mock_registry: The MockToolRegistry to use for tool executions.
        initial_variables: Dict containing initial variables for the workflow.
    """  # noqa: D202
    
    def __init__(
        self,
        workflow: Workflow,
        mock_registry: MockToolRegistry,
        initial_variables: Optional[Dict[str, Any]] = None
    ):
        self.workflow = workflow
        self.mock_registry = mock_registry
        self.initial_variables = initial_variables or {}
        self.executed_tasks: List[str] = []
        self.task_outputs: Dict[str, Dict[str, Any]] = {}
        self.execution_context: Optional[ExecutionContext] = None
        self.result: Optional[Dict[str, Any]] = None
        self.exception: Optional[Exception] = None
        
    def execute(self) -> Dict[str, Any]:
        """
        Execute the workflow with mocked tool executions.
        
        Returns:
            Dict containing the workflow result.
            
        Raises:
            Exception: If the workflow execution fails.
        """
        try:
            # Initialize the workflow
            self.execution_context = ExecutionContext(variables=self.initial_variables)
            
            # Execute the workflow
            self.result = self.workflow.execute(self.execution_context)
            
            # Track executed tasks
            self._track_executed_tasks()
            
            return self.result
        except Exception as e:
            self.exception = e
            # Track executed tasks even if the workflow fails
            self._track_executed_tasks()
            raise
            
    def _track_executed_tasks(self):
        """
        Track which tasks were executed and their outputs.
        """
        if not self.execution_context:
            return
            
        for task_id, task_data in self.execution_context.task_data.items():
            if task_data.get("status") == TaskStatus.COMPLETED.value:
                self.executed_tasks.append(task_id)
                self.task_outputs[task_id] = task_data.get("output", {})
                
    def assert_workflow_completed(self):
        """
        Assert that the workflow completed successfully.
        
        Raises:
            AssertionError: If the workflow did not complete successfully.
        """
        if self.exception:
            raise AssertionError(f"Workflow failed with exception: {self.exception}")
        
        assert self.result is not None, "Workflow did not produce a result"
        
    def assert_workflow_failed(self, exception_type: Optional[Type[Exception]] = None):
        """
        Assert that the workflow failed with the expected exception type.
        
        Args:
            exception_type: Expected exception type. If None, just assert that the workflow failed.
            
        Raises:
            AssertionError: If the workflow did not fail or failed with the wrong exception type.
        """
        assert self.exception is not None, "Workflow did not fail"
        
        if exception_type:
            assert isinstance(self.exception, exception_type), f"Workflow failed with {type(self.exception)}, expected {exception_type}"
            
    def assert_task_executed(self, task_id: str):
        """
        Assert that a specific task was executed.
        
        Args:
            task_id: ID of the task to check.
            
        Raises:
            AssertionError: If the task was not executed.
        """
        assert task_id in self.executed_tasks, f"Task '{task_id}' was not executed"
        
    def assert_task_not_executed(self, task_id: str):
        """
        Assert that a specific task was not executed.
        
        Args:
            task_id: ID of the task to check.
            
        Raises:
            AssertionError: If the task was executed.
        """
        assert task_id not in self.executed_tasks, f"Task '{task_id}' was executed"
        
    def assert_tasks_executed_in_order(self, task_ids: List[str]):
        """
        Assert that tasks were executed in the specified order.
        
        Args:
            task_ids: List of task IDs in the expected order.
            
        Raises:
            AssertionError: If the tasks were not executed in the specified order.
        """
        # Check that all tasks were executed
        for task_id in task_ids:
            self.assert_task_executed(task_id)
        
        # Check the order
        task_indices = {task_id: i for i, task_id in enumerate(self.executed_tasks)}
        for i in range(len(task_ids) - 1):
            current_task = task_ids[i]
            next_task = task_ids[i + 1]
            assert task_indices[current_task] < task_indices[next_task], \
                f"Task '{current_task}' was not executed before '{next_task}'"
                
    def get_task_output(self, task_id: str) -> Dict[str, Any]:
        """
        Get the output of a specific task.
        
        Args:
            task_id: ID of the task.
            
        Returns:
            Dict containing the task output.
            
        Raises:
            AssertionError: If the task was not executed.
        """
        self.assert_task_executed(task_id)
        return self.task_outputs[task_id]
        
    def get_variable(self, name: str) -> Any:
        """
        Get the value of a variable from the execution context.
        
        Args:
            name: Name of the variable.
            
        Returns:
            Value of the variable.
            
        Raises:
            AssertionError: If the variable does not exist.
        """
        assert self.execution_context is not None, "Workflow has not been executed"
        assert name in self.execution_context.variables, f"Variable '{name}' does not exist"
        return self.execution_context.variables[name]
        
    def assert_variable_equals(self, name: str, expected_value: Any):
        """
        Assert that a variable has the expected value.
        
        Args:
            name: Name of the variable.
            expected_value: Expected value of the variable.
            
        Raises:
            AssertionError: If the variable does not exist or has the wrong value.
        """
        value = self.get_variable(name)
        assert value == expected_value, f"Variable '{name}' has value {value}, expected {expected_value}"
        
    def assert_variable_contains(self, name: str, substring: str):
        """
        Assert that a string variable contains the specified substring.
        
        Args:
            name: Name of the variable.
            substring: Substring to check for.
            
        Raises:
            AssertionError: If the variable does not exist, is not a string, or does not contain the substring.
        """
        value = self.get_variable(name)
        assert isinstance(value, str), f"Variable '{name}' is not a string"
        assert substring in value, f"Variable '{name}' does not contain '{substring}'"
        
    def assert_variable_matches(self, name: str, pattern: str):
        """
        Assert that a string variable matches the specified regex pattern.
        
        Args:
            name: Name of the variable.
            pattern: Regex pattern to match.
            
        Raises:
            AssertionError: If the variable does not exist, is not a string, or does not match the pattern.
        """
        value = self.get_variable(name)
        assert isinstance(value, str), f"Variable '{name}' is not a string"
        assert re.search(pattern, value), f"Variable '{name}' does not match pattern '{pattern}'"


class TaskTestHarness:
    """
    Test harness for individual tasks.
    
    This class helps test individual tasks in isolation by mocking tool executions
    and capturing outputs.
    
    Args:
        task: The task instance to test.
        mock_executions: Dict mapping tool names to lists of mock execution configurations.
        input_variables: Dict containing input variables for the task.
    """  # noqa: D202
    
    def __init__(
        self,
        task: Task,
        mock_executions: Dict[str, List[Dict[str, Any]]],
        input_variables: Dict[str, Any]
    ):
        self.task = task
        self.mock_executions = mock_executions
        self.input_variables = input_variables
        
        # Create and configure the mock registry
        self.mock_registry = MockToolRegistry()
        
        # Configure mock executions
        for tool_name, executions in mock_executions.items():
            for mock_config in executions:
                input_pattern = mock_config.get("input_pattern", {})
                output = mock_config.get("output", {})
                exception = mock_config.get("exception")
                
                if exception:
                    # Configure an exception to be raised
                    self.mock_registry.mock_tool_as_failure(
                        tool_name, 
                        str(exception),
                    )
                else:
                    # Configure a success response
                    self.mock_registry.add_mock_response(
                        tool_name,
                        input_pattern,
                        output or {}
                    )
                    
        self.execution_context: Optional[ExecutionContext] = None
        self.output: Optional[Dict[str, Any]] = None
        self.exception: Optional[Exception] = None
        
    def execute(self) -> Dict[str, Any]:
        """
        Execute the task with mocked tool executions.
        
        Returns:
            Dict containing the task output.
            
        Raises:
            Exception: If the task execution fails.
        """
        try:
            # Set up the task
            self.task.set_tool_registry(self.mock_registry)
            
            # Create an execution context
            self.execution_context = ExecutionContext(variables=self.input_variables)
            
            # Execute the task
            self.output = self.task.execute(self.execution_context)
            
            return self.output
        except Exception as e:
            self.exception = e
            raise
            
    def assert_task_completed(self):
        """
        Assert that the task completed successfully.
        
        Raises:
            AssertionError: If the task did not complete successfully.
        """
        if self.exception:
            raise AssertionError(f"Task failed with exception: {self.exception}")
        
        assert self.output is not None, "Task did not produce output"
        
    def assert_task_failed(self, exception_type: Optional[Type[Exception]] = None):
        """
        Assert that the task failed with the expected exception type.
        
        Args:
            exception_type: Expected exception type. If None, just assert that the task failed.
            
        Raises:
            AssertionError: If the task did not fail or failed with the wrong exception type.
        """
        assert self.exception is not None, "Task did not fail"
        
        if exception_type:
            assert isinstance(self.exception, exception_type), f"Task failed with {type(self.exception)}, expected {exception_type}"
            
    def get_variable(self, name: str) -> Any:
        """
        Get the value of a variable from the execution context.
        
        Args:
            name: Name of the variable.
            
        Returns:
            Value of the variable.
            
        Raises:
            AssertionError: If the variable does not exist.
        """
        assert self.execution_context is not None, "Task has not been executed"
        assert name in self.execution_context.variables, f"Variable '{name}' does not exist"
        return self.execution_context.variables[name]
        
    def assert_variable_equals(self, name: str, expected_value: Any):
        """
        Assert that a variable has the expected value.
        
        Args:
            name: Name of the variable.
            expected_value: Expected value of the variable.
            
        Raises:
            AssertionError: If the variable does not exist or has the wrong value.
        """
        value = self.get_variable(name)
        assert value == expected_value, f"Variable '{name}' has value {value}, expected {expected_value}"
        
    def assert_variable_contains(self, name: str, substring: str):
        """
        Assert that a string variable contains the specified substring.
        
        Args:
            name: Name of the variable.
            substring: Substring to check for.
            
        Raises:
            AssertionError: If the variable does not exist, is not a string, or does not contain the substring.
        """
        value = self.get_variable(name)
        assert isinstance(value, str), f"Variable '{name}' is not a string"
        assert substring in value, f"Variable '{name}' does not contain '{substring}'"
        
    def assert_variable_matches(self, name: str, pattern: str):
        """
        Assert that a string variable matches the specified regex pattern.
        
        Args:
            name: Name of the variable.
            pattern: Regex pattern to match.
            
        Raises:
            AssertionError: If the variable does not exist, is not a string, or does not match the pattern.
        """
        value = self.get_variable(name)
        assert isinstance(value, str), f"Variable '{name}' is not a string"
        assert re.search(pattern, value), f"Variable '{name}' does not match pattern '{pattern}'"


class ToolExecutionRecorder:
    """
    Records and replays tool executions for testing.
    
    This class allows you to:
    1. Record tool executions during development or manual testing
    2. Generate mock executions from recorded sessions for tests
    3. Replay recorded tool executions in tests
    
    It serves as a wrapper around a real tool registry to record interactions,
    which can then be used to generate mocks for future test runs.
    """  # noqa: D202
    
    def __init__(self, tool_registry, recording_file=None):
        """
        Initialize the recorder.
        
        Args:
            tool_registry: The real tool registry to wrap and record calls to
            recording_file: Optional path to save recordings to. If not provided,
                            a default path will be generated based on date/time.
        """
        self.tool_registry = tool_registry
        self.recordings = []
        self.recording_file = recording_file or self._generate_recording_path()
        
    def _generate_recording_path(self) -> str:
        """Generate a default recording path based on date/time."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        directory = "tests/recordings"
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f"tool_execution_{timestamp}.json")
    
    def execute_tool(self, tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and record the interaction.
        
        Args:
            tool_name: Name of the tool to execute
            inputs: Inputs to pass to the tool
            
        Returns:
            The output from the tool execution
        """
        try:
            # Execute the real tool
            output = self.tool_registry.execute_tool(tool_name, inputs)
            
            # Record the execution (success)
            self.recordings.append({
                "tool_name": tool_name,
                "inputs": inputs,
                "output": output,
                "success": True,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            return output
        except Exception as e:
            # Record the execution (failure)
            self.recordings.append({
                "tool_name": tool_name,
                "inputs": inputs,
                "error": str(e),
                "error_type": e.__class__.__name__,
                "success": False,
                "timestamp": datetime.datetime.now().isoformat()
            })
            raise
    
    def save_recordings(self, file_path=None):
        """
        Save the recorded tool executions to a file.
        
        Args:
            file_path: Optional path to save to; uses the default if not provided
        """
        file_path = file_path or self.recording_file
        with open(file_path, 'w') as f:
            json.dump({
                "version": "1.0",
                "created_at": datetime.datetime.now().isoformat(),
                "recordings": self.recordings
            }, f, indent=2)
        
        print(f"Saved {len(self.recordings)} tool execution recordings to {file_path}")
    
    def generate_mock_executions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate mock executions from the recorded tool calls.
        
        Returns:
            Dict mapping tool names to lists of mock execution configurations
            suitable for use with MockToolRegistry or create_mock_tool_execution.
        """
        mocks = {}
        
        for recording in self.recordings:
            tool_name = recording["tool_name"]
            if tool_name not in mocks:
                mocks[tool_name] = []
            
            if recording["success"]:
                # Create a successful mock execution
                mocks[tool_name].append(create_mock_tool_execution(
                    input_pattern=recording["inputs"],
                    output=recording["output"]
                ))
            else:
                # Create a mock execution that raises an exception
                # Note: We have to use a generic Exception here since we can't recreate
                # the original exception class from just its name
                mocks[tool_name].append(create_mock_tool_execution(
                    input_pattern=recording["inputs"],
                    exception=Exception(recording["error"])
                ))
        
        return mocks
    
    @classmethod
    def from_recording_file(cls, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load mock executions from a recorded file.
        
        Args:
            file_path: Path to the recording file
            
        Returns:
            Dict mapping tool names to lists of mock execution configurations
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Create an instance without a real tool registry
        recorder = cls(None, file_path)
        recorder.recordings = data["recordings"]
        
        # Generate mocks from the loaded recordings
        return recorder.generate_mock_executions()


def record_tool_executions(func):
    """
    Decorator to record tool executions during a function call.
    
    This decorator wraps the original function, records all tool executions made
    during its execution, and saves them to a file once the function completes.
    
    Example:
        @record_tool_executions
        def process_document(document_path):
            # Function that makes tool calls
            result = execute_tool("file_reader", {"path": document_path})
            return result
    """
    def wrapper(*args, **kwargs):
        try:
            # Try to import using the actual module structure
            from core.tools.registry_access import get_tool_registry, set_tool_registry
        except ImportError:
            # If that doesn't work, fall back to a simpler implementation
            print("Warning: Could not import tool_registry_access. Recording is disabled.")
            return func(*args, **kwargs)
        
        # Save the original tool registry
        original_registry = get_tool_registry()
        
        # Create a recorder wrapped around the original registry
        recorder = ToolExecutionRecorder(original_registry)
        
        # Replace the global tool registry with the recorder
        set_tool_registry(recorder)
        
        try:
            # Execute the original function
            return func(*args, **kwargs)
        finally:
            # Restore the original tool registry
            set_tool_registry(original_registry)
            
            # Save the recordings
            recorder.save_recordings()
    
    return wrapper 