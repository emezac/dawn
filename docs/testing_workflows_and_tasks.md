# Testing Workflows and Tasks

This document provides comprehensive guidance on how to use the testing utilities in the Dawn platform, focusing on the `core.utils.testing` module. These utilities make it easy to test workflows and individual tasks with mocked tool executions, allowing for fast, deterministic tests without external dependencies.

## Table of Contents

1. [Overview](#overview)
2. [Key Components](#key-components)
3. [Setting Up for Testing](#setting-up-for-testing)
4. [Testing Complete Workflows](#testing-complete-workflows)
5. [Testing Individual Tasks](#testing-individual-tasks)
6. [Best Practices](#best-practices)
7. [Advanced Testing Techniques](#advanced-testing-techniques)
8. [Related Documentation](#related-documentation)

## Overview

Dawn's workflow system is designed to be highly testable. The `core.utils.testing` module provides a set of tools that make it easy to:

- Mock tool executions (like API calls to LLMs, database operations, etc.)
- Track which tasks are executed and in what order
- Verify task outputs and workflow variables
- Test error handling and edge cases

By using these testing utilities, you can ensure that your workflows and tasks behave as expected without relying on external services or APIs.

## Key Components

The testing module offers several key components:

### WorkflowTestHarness

A class for testing complete workflows. It tracks task execution order, captures outputs, and provides assertions for workflow behavior.

### TaskTestHarness

A class for testing individual tasks in isolation. It provides a controlled environment for tasks and allows mocking of tool executions.

### MockToolRegistry

A registry that intercepts tool calls and returns predefined responses. This lets you simulate different scenarios, including success and error cases.

## Setting Up for Testing

To get started with testing workflows and tasks, import the necessary components from the testing module:

```python
# Import testing utilities
from core.utils.testing import (
    create_mock_tool_execution,
    workflow_test_context,
    WorkflowTestHarness,
    TaskTestHarness
)

# Import your workflow and task classes
from workflows.your_workflow import YourWorkflow
from tasks.your_task import YourTask
```

### Defining Mock Tool Executions

The first step is to define how your tools should behave during tests. Use the `create_mock_tool_execution` function to create mock tool executions:

```python
# Define mock tool executions
mock_executions = {
    "openai": [
        # Mock a successful LLM call
        create_mock_tool_execution(
            {"prompt": "Extract entities", "temperature": 0.7},
            {"content": "Entity extraction result"}
        ),
        # Mock using a function to match inputs
        create_mock_tool_execution(
            {"prompt": lambda p: "summarize" in p.lower()},
            {"content": "Summarization result"}
        ),
        # Mock an error condition
        create_mock_tool_execution(
            {"prompt": "This will fail"},
            exception=ValueError("LLM API error")
        )
    ],
    "file_system": [
        # Mock file reading
        create_mock_tool_execution(
            {"path": "document.pdf", "operation": "read"},
            {"content": "File content"}
        ),
        # Mock file not found error
        create_mock_tool_execution(
            {"path": "missing.pdf", "operation": "read"},
            exception=FileNotFoundError("File not found")
        )
    ]
}
```

You can specify exact matches for inputs or use functions to match inputs dynamically:

- **Exact Match**: The input must exactly match the specified pattern
- **Function Match**: The input is passed to the function, which returns `True` if it matches

## Testing Complete Workflows

To test a complete workflow, use the `workflow_test_context` context manager:

```python
def test_document_analysis_workflow():
    # Create workflow instance
    workflow = DocumentAnalysisWorkflow()
    
    # Set up mock executions
    mock_executions = {
        "openai": [
            create_mock_tool_execution(
                {"prompt": lambda p: "extract entities" in p.lower()},
                {"content": "Entity1, Entity2, Entity3"}
            ),
            create_mock_tool_execution(
                {"prompt": lambda p: "summarize" in p.lower()},
                {"content": "Document summary"}
            )
        ],
        "file_system": [
            create_mock_tool_execution(
                {"path": "document.pdf", "operation": "read"},
                {"content": "Document content"}
            )
        ]
    }
    
    # Set up initial variables
    initial_variables = {
        "document_path": "document.pdf",
        "analysis_type": "full"
    }
    
    # Execute workflow with mocked tool executions
    with workflow_test_context(workflow, mock_executions, initial_variables) as (workflow, harness):
        # Execute the workflow
        result = harness.execute()
        
        # Assert workflow completed successfully
        harness.assert_workflow_completed()
        
        # Assert tasks were executed
        harness.assert_task_executed("read_document")
        harness.assert_task_executed("extract_entities")
        harness.assert_task_executed("summarize_document")
        
        # Assert task execution order
        harness.assert_tasks_executed_in_order([
            "read_document",
            "extract_entities",
            "summarize_document"
        ])
        
        # Assert variable values
        harness.assert_variable_equals("entities", "Entity1, Entity2, Entity3")
        harness.assert_variable_equals("summary", "Document summary")
        harness.assert_variable_contains("summary", "summary")
        
        # Get task output
        entity_extraction_output = harness.get_task_output("extract_entities")
        assert "entities" in entity_extraction_output
```

### Testing Error Handling in Workflows

You can also test how your workflow handles errors:

```python
def test_workflow_handles_missing_file():
    # Create workflow instance
    workflow = DocumentAnalysisWorkflow()
    
    # Set up mock executions with file not found error
    mock_executions = {
        "file_system": [
            create_mock_tool_execution(
                {"path": "missing.pdf", "operation": "read"},
                exception=FileNotFoundError("File not found")
            )
        ]
    }
    
    # Set up initial variables
    initial_variables = {
        "document_path": "missing.pdf",
        "analysis_type": "full"
    }
    
    # Execute workflow with mocked tool executions
    with workflow_test_context(workflow, mock_executions, initial_variables) as (workflow, harness):
        # Execute the workflow (should not raise an exception if error handling works)
        result = harness.execute()
        
        # Assert workflow completed (with error handling)
        harness.assert_workflow_completed()
        
        # Assert error handling tasks were executed
        harness.assert_task_executed("handle_file_not_found")
        
        # Assert error message was set
        harness.assert_variable_contains("error_message", "File not found")
```

## Testing Individual Tasks

To test an individual task, use the `TaskTestHarness` class:

```python
def test_extract_entities_task():
    # Create task instance
    task = ExtractEntitiesTask()
    
    # Set up mock executions
    mock_executions = {
        "openai": [
            create_mock_tool_execution(
                {"prompt": lambda p: "extract entities" in p.lower()},
                {"content": "Entity1, Entity2, Entity3"}
            )
        ]
    }
    
    # Set up input variables
    input_variables = {
        "document_content": "This is a document about Entity1 and Entity2.",
        "extraction_prompt": "Please extract entities from this document."
    }
    
    # Create task test harness
    harness = TaskTestHarness(task, mock_executions, input_variables)
    
    # Execute the task
    output = harness.execute()
    
    # Assert task completed successfully
    harness.assert_task_completed()
    
    # Assert output variables
    harness.assert_variable_equals("entities", "Entity1, Entity2, Entity3")
```

### Testing Error Handling in Tasks

You can also test how your task handles errors:

```python
def test_task_handles_invalid_input():
    # Create task instance
    task = ExtractEntitiesTask()
    
    # Set up mock executions
    mock_executions = {
        "openai": [
            create_mock_tool_execution(
                {"prompt": lambda p: True},  # Match any prompt
                {"content": "Entity1, Entity2, Entity3"}
            )
        ]
    }
    
    # Set up invalid input variables (missing required field)
    input_variables = {
        # Missing "document_content"
        "extraction_prompt": "Please extract entities from this document."
    }
    
    # Create task test harness
    harness = TaskTestHarness(task, mock_executions, input_variables)
    
    try:
        # Execute the task (should raise an exception)
        output = harness.execute()
        assert False, "Task should have failed but did not"
    except ValueError:
        # Expected exception
        pass
    
    # Assert task failed with the expected exception type
    harness.assert_task_failed(ValueError)
```

## Best Practices

When testing workflows and tasks, follow these best practices:

1. **Focus on Critical Paths**: Test the most important paths through your workflow first.

2. **Create Focused Tests**: Each test should verify a specific aspect of your workflow or task.

3. **Mock External Dependencies**: Always mock external services like LLMs, databases, and file systems.

4. **Verify Task Execution Order**: For workflows with dependent tasks, verify they execute in the expected order.

5. **Test Error Handling**: Include tests for error conditions to ensure your workflow recovers gracefully.

6. **Keep Tests Fast**: Tests should run quickly to support rapid development.

7. **Use Descriptive Test Names**: Name your tests to clearly indicate what they're testing.

## Advanced Testing Techniques

### Testing Task Failures

You can test how a workflow handles task failures by configuring a mock tool execution to raise an exception:

```python
def test_workflow_handles_llm_failure():
    # Create workflow instance
    workflow = DocumentAnalysisWorkflow()
    
    # Set up mock executions with LLM error
    mock_executions = {
        "file_system": [
            create_mock_tool_execution(
                {"path": "document.pdf", "operation": "read"},
                {"content": "Document content"}
            )
        ],
        "openai": [
            create_mock_tool_execution(
                {"prompt": lambda p: "extract entities" in p.lower()},
                exception=ConnectionError("LLM API connection error")
            )
        ]
    }
    
    # Execute workflow with mocked tool executions
    with workflow_test_context(workflow, mock_executions) as (workflow, harness):
        # Execute the workflow
        result = harness.execute()
        
        # Assert error handling tasks were executed
        harness.assert_task_executed("handle_llm_error")
        
        # Assert error message was set
        harness.assert_variable_contains("error_message", "connection error")
```

### Testing Workflows with Multiple Tool Calls

For tasks that make multiple tool calls, set up multiple mock executions that match different inputs:

```python
def test_multi_step_analysis_task():
    # Create task instance
    task = MultiStepAnalysisTask()
    
    # Set up mock executions for multiple calls
    mock_executions = {
        "openai": [
            # First call: entity extraction
            create_mock_tool_execution(
                {"prompt": lambda p: "extract entities" in p.lower()},
                {"content": "Entity1, Entity2, Entity3"}
            ),
            # Second call: sentiment analysis
            create_mock_tool_execution(
                {"prompt": lambda p: "sentiment analysis" in p.lower()},
                {"content": "Positive sentiment"}
            ),
            # Third call: topic classification
            create_mock_tool_execution(
                {"prompt": lambda p: "classify topics" in p.lower()},
                {"content": "Topic1, Topic2"}
            )
        ]
    }
    
    # Create task test harness
    harness = TaskTestHarness(task, mock_executions, {
        "document_content": "Sample document"
    })
    
    # Execute the task
    output = harness.execute()
    
    # Assert variables set by the task
    harness.assert_variable_equals("entities", "Entity1, Entity2, Entity3")
    harness.assert_variable_equals("sentiment", "Positive sentiment")
    harness.assert_variable_equals("topics", "Topic1, Topic2")
```

## Related Documentation

For more information, see these related documentation files:

- [Workflow System Overview](workflow_system.md)
- [Creating Custom Tasks](creating_custom_tasks.md)
- [Tool Registries](tool_registries.md) 