# Tool Recording for Testing Workflows

This document explains how to use the tool recording feature to test Dawn workflows effectively.

## Overview

Testing workflows that interact with external systems can be challenging. The tool recording feature solves this by:

1. **Recording tool executions** during actual workflow runs
2. **Replaying recorded executions** during tests without calling real tools
3. **Creating mock tools** that simulate different responses for testing edge cases

This approach enables deterministic, repeatable testing without requiring access to external systems.

## Recording Tool Executions

### Using the Recording Decorator

The simplest way to record tool executions is with the `@record_tool_executions` decorator:

```python
from core.utils.testing import record_tool_executions

@record_tool_executions
def run_my_workflow(input_data):
    # Workflow implementation that uses tools
    result = compliance_workflow(
        data_type=input_data["data_type"],
        query=input_data["query"]
    )
    return result

# Run the workflow to record tool executions
result = run_my_workflow({
    "data_type": "user_emails",
    "query": "Find sensitive information"
})
```

By default, recordings are saved to `tests/recordings/tool_execution_YYYYMMDD_HHMMSS.json`. You can specify a custom path:

```python
@record_tool_executions(output_file="tests/recordings/my_custom_recording.json")
def run_my_workflow(input_data):
    # Workflow implementation
    pass
```

### Using ToolExecutionRecorder Directly

For more control, you can use `ToolExecutionRecorder` directly:

```python
from core.utils.testing import ToolExecutionRecorder
from core.tools.registry_access import get_registry

# Get the real tool registry
registry = get_registry()

# Create a recorder
recorder = ToolExecutionRecorder(registry, recording_file="my_recording.json")

# Replace the execute_tool method to record executions
original_execute_tool = registry.execute_tool
registry.execute_tool = recorder.execute_tool

try:
    # Run your workflow
    result = my_workflow_function(input_data)
finally:
    # Restore the original execute_tool method
    registry.execute_tool = original_execute_tool
    
    # Save the recordings
    recorder.save_recordings()
```

## Using Recordings in Tests

### Option 1: Testing with WorkflowTestHarness

The `WorkflowTestHarness` class makes it easy to test workflows with recorded tool executions:

```python
import unittest
from core.utils.testing import WorkflowTestHarness, load_tool_recordings

class TestMyWorkflow(unittest.TestCase):
    def setUp(self):
        # Load recordings
        self.recordings = load_tool_recordings("tests/recordings/my_recording.json")
        
        # Create test harness
        self.harness = WorkflowTestHarness(
            workflow=my_workflow,
            initial_variables={"data_type": "user_emails"}
        )
        
        # Set up mock tools from recordings
        mock_registry = self.harness.mock_registry
        for recording in self.recordings:
            tool_name = recording["tool_name"]
            mock_registry.register_tool(
                tool_name, 
                lambda **kwargs, r=recording: r["output"]
            )
        
    def test_workflow_success(self):
        # Execute the workflow with test harness
        result = self.harness.execute()
        
        # Assertions
        self.assertTrue(result["success"])
        self.harness.assert_task_executed("format_results")
        self.harness.assert_variable_equals("risk_level", "high")
```

### Option 2: Using Example Test Pattern

The pattern shown in `examples/test_with_recordings.py` provides another approach:

```python
from core.utils.testing import load_tool_recordings

# Load recordings
recordings = load_tool_recordings(RECORDING_FILE)

# Create registry with recording-based mocks
registry = create_mock_tool_registry()
patch_tool_registry_with_recordings(registry, recordings)

# Monkey patch the execute_tool method
original_execute_tool = MockToolRegistry.execute_tool
MockToolRegistry.execute_tool = registry.execute_tool

try:
    # Run the workflow
    result = compliance_workflow(
        data_type="user_emails",
        query="Find sensitive information"
    )
    
    # Verify results
    assert result["success"]
    assert result["result"]["risk_level"] == "high"
finally:
    # Restore original method
    MockToolRegistry.execute_tool = original_execute_tool
```

## Testing with Manual Mocks

For specific test scenarios, you can create mock tools manually:

```python
# Create a registry with custom mock tools
registry = MockToolRegistry()

# Define custom mock tool
def mock_search_vector_store(store_name, query, **kwargs):
    return {
        "success": True,
        "result": {
            "matches": [
                {
                    "id": "test-doc",
                    "metadata": {
                        "content": "Test content with sensitive information"
                    }
                }
            ]
        },
        "status": "success"
    }

# Register mock tools
registry.register_tool("search_vector_store", mock_search_vector_store)

# Monkey patch the execute_tool method
original_execute_tool = MockToolRegistry.execute_tool
MockToolRegistry.execute_tool = registry.execute_tool

try:
    # Run the workflow with mock tools
    result = workflow_function(input_data)
finally:
    # Restore original method
    MockToolRegistry.execute_tool = original_execute_tool
```

## Testing Error Handling

Testing how workflows handle errors is critical. You can create mock tools that simulate failures:

```python
# Define a tool that fails
def mock_failing_search(**kwargs):
    return {
        "success": False,
        "error": "Simulated search failure",
        "status": "error"
    }

# Register the failing tool
registry.register_tool("search_vector_store", mock_failing_search)

# Test that the workflow handles the error correctly
result = workflow_function(input_data)
assert not result["success"]
assert "error" in result
assert "Simulated search failure" in result["error"]
```

## Best Practices

1. **Record real executions for happy paths**: Use real tool executions for the main success paths.

2. **Create mock tools for edge cases**: Manually define mock tools for error conditions and edge cases.

3. **Test workflows and tasks independently**: Use `WorkflowTestHarness` for complete workflows and `TaskTestHarness` for individual tasks.

4. **Use descriptive recording filenames**: Name recordings to indicate their purpose (e.g., `compliance_workflow_high_risk.json`).

5. **Clean sensitive data**: Remove sensitive information from recordings before committing them.

6. **Verify task execution order**: Use `assert_tasks_executed_in_order()` to verify workflows execute tasks in the expected sequence.

7. **Assert on final variables**: Assert that workflows set expected variables upon completion.

8. **Test error recovery paths**: Verify that workflows can recover from errors when appropriate.

## Example Implementation

For a complete example, refer to:
- `examples/mock_compliance_workflow.py`: Example workflow with recording capability
- `examples/test_with_recordings.py`: Tests using recordings

## Troubleshooting

### Recording Not Working

- Ensure the tool registry is properly set up
- Check that the tool function is being called through the registry
- Verify the recording directory exists and is writable

### Test Failing with Recorded Data

- Check that the recordings contain the expected tool executions
- Verify that the mocked tool parameters match what the workflow is sending
- Ensure all required tools are mocked

### Tool Registry Already Contains Mocks

If you get errors about tools already being registered:
```python
# Clear the registry before registering mocks
registry.tools = {}
```

## Related Resources

- [Testing Workflows and Tasks](testing_workflows_and_tasks.md)
- [Workflow System](workflow_system.md)
- [Task and Tool Development Guide](creating_custom_tasks.md) 