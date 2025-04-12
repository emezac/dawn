# Testing Workflows and Tasks

This document describes how to use the testing utilities provided in `core.utils.testing` to effectively test workflows and tasks in the Dawn platform.

## Overview

The Dawn platform provides specialized testing utilities to make it easier to test workflows and tasks. These utilities allow you to:

1. Test complete workflows end-to-end with mocked tool executions
2. Test individual tasks in isolation with controlled inputs
3. Track execution paths through workflows
4. Verify outputs from specific tasks
5. Assert which tasks were executed, completed, or failed

## Key Components

### WorkflowTestHarness

This class provides a testing environment for workflows. It allows you to:

- Execute a workflow with mocked tool responses
- Track which tasks were executed, completed, or failed
- Assert workflow completion or failure 
- Retrieve outputs from specific tasks

### TaskTestHarness

This class provides a testing environment for individual tasks. It allows you to:

- Test a task in isolation with controlled inputs
- Mock dependencies on other tasks
- Verify task outputs and state transitions

### create_mock_tool_execution

This function creates a mock tool execution for use with the test harnesses. It configures how a specific tool invocation should respond during testing.

### workflow_test_context

A context manager that sets up a test environment for workflows, handling the necessary initialization and cleanup.

## Using WorkflowTestHarness

Here's a basic example of testing a workflow:

```python
def test_basic_workflow():
    # Create the workflow instance
    workflow = MyWorkflow()
    
    # Define mock executions for any tools the workflow will use
    mock_executions = {
        "llm": [
            create_mock_tool_execution(
                {"prompt": "Analyze this document"},  # Input pattern to match
                {"response": '{"result": "analysis complete"}'}  # Output to return
            )
        ],
        "s3": [
            create_mock_tool_execution(
                {"action": "upload", "key": "reports/report.json"},
                {"url": "https://example.com/report.json"}
            )
        ]
    }
    
    # Initialize test harness with workflow, mocks, and initial variables
    harness = WorkflowTestHarness(
        workflow=workflow,
        mock_executions=mock_executions,
        initial_variables={"document_path": "test_doc.pdf"}
    )
    
    # Execute the workflow
    result = harness.execute()
    
    # Verify workflow completed successfully
    harness.assert_workflow_completed()
    
    # Assert specific tasks were executed
    harness.assert_task_executed("extract_text")
    harness.assert_task_executed("analyze_document")
    
    # Assert specific tasks were NOT executed (e.g., error path)
    harness.assert_task_not_executed("handle_error")
    
    # Retrieve output from a specific task
    analysis = harness.get_task_output("analyze_document")
    assert analysis["result"] == "analysis complete"
    
    # Verify final workflow output
    assert "report_url" in result
    assert result["report_url"] == "https://example.com/report.json"
```

### Mock Execution Matching

When defining mock executions, you can match inputs in several ways:

1. **Exact match**: The input value must match exactly
2. **Function match**: Provide a lambda or function that returns True if the input matches
3. **Partial dict match**: For dict inputs, only the specified keys need to match

Example of different matching approaches:

```python
mock_executions = {
    "llm": [
        # Exact match - prompt must be exactly this string
        create_mock_tool_execution(
            {"prompt": "Exact prompt text"},
            {"response": "Output 1"}
        ),
        
        # Function match - prompt must contain "analyze"
        create_mock_tool_execution(
            {"prompt": lambda x: "analyze" in x.lower()},
            {"response": "Output 2"}
        ),
        
        # Partial dict match - only temperature is checked
        create_mock_tool_execution(
            {"temperature": 0.7},
            {"response": "Output 3"}
        )
    ]
}
```

## Using TaskTestHarness

Here's a basic example of testing an individual task:

```python
def test_individual_task():
    # Create a task instance
    task = MyTask()
    
    # Define mock executions for any tools the task will use
    mock_executions = {
        "llm": [
            create_mock_tool_execution(
                {"prompt": "Generate summary"},
                {"response": "This is a summary"}
            )
        ]
    }
    
    # Initialize test harness with task, mocks, and inputs
    harness = TaskTestHarness(
        task=task,
        mock_executions=mock_executions,
        input_variables={
            "document_text": "This is a test document"
        }
    )
    
    # Execute the task
    result = harness.execute()
    
    # Verify task completed successfully
    harness.assert_task_completed()
    
    # Verify task output
    assert "summary" in result
    assert result["summary"] == "This is a summary"
```

## Testing Best Practices

1. **Test both success and failure paths**: Make sure to test how workflows handle errors by providing mock executions that trigger error conditions.

2. **Test variable resolution issues**: Test how workflows handle unresolved template variables by providing string values that match the variable pattern (e.g., `${var_name}`).

3. **Test each task in isolation first**: Use `TaskTestHarness` to test individual tasks thoroughly before testing the complete workflow.

4. **Create comprehensive test fixtures**: Define reusable mock executions for common tools to maintain consistency across tests.

5. **Test edge cases**: Include tests for boundary conditions, malformed inputs, and unexpected outputs from tools.

6. **Check task execution order**: Use `get_executed_tasks()` to verify tasks were executed in the expected order.

7. **Document expected workflow behavior**: Include comments in tests that describe the expected behavior of workflows and tasks.

## Advanced Features

### Testing Task Failure Handling

To test how workflows handle task failures:

```python
# Mock a tool execution that will fail
mock_executions = {
    "llm": [
        create_mock_tool_execution(
            {"prompt": "Generate content"},
            exception=ValueError("LLM service unavailable")
        )
    ]
}

harness = WorkflowTestHarness(workflow, mock_executions, initial_variables)
result = harness.execute()

# Verify the expected failure handling task was executed
harness.assert_task_failed("generate_content")
harness.assert_task_executed("handle_generation_error")
```

### Testing Workflows with Multiple Tool Calls

When testing workflows that make multiple calls to the same tool, you can define multiple mock executions in sequence:

```python
mock_executions = {
    "llm": [
        # First call to LLM
        create_mock_tool_execution(
            {"prompt": lambda x: "extract" in x.lower()},
            {"response": "First response"}
        ),
        # Second call to LLM
        create_mock_tool_execution(
            {"prompt": lambda x: "analyze" in x.lower()},
            {"response": "Second response"}
        ),
        # Third call to LLM
        create_mock_tool_execution(
            {"prompt": lambda x: "summarize" in x.lower()},
            {"response": "Third response"}
        )
    ]
}
```

The mock executions will be consumed in order as the workflow makes calls to the tool.

## Example Test Files

For complete examples of how to test workflows, refer to these test files:

- `tests/test_compliance_workflows.py`: Tests for the compliance workflows
- `tests/test_document_processing_workflows.py`: Tests for document processing workflows

These files demonstrate comprehensive testing strategies for workflows and tasks. 