# Tool Recording Feature for Testing Workflows

## Overview

The Dawn platform includes a powerful tool recording feature that allows you to capture tool executions during workflow runs and replay them during testing. This enables reliable, deterministic testing of workflows without actually executing potentially expensive or side-effect-causing tools.

## Key Components

- **`@record_tool_executions` decorator**: Records all tool executions within a workflow to a JSON file
- **`load_tool_recordings`**: Loads recorded tool executions from a file
- **`create_mock_registry_from_recordings`**: Creates a mock tool registry that replays recorded tool responses
- **`WorkflowTestHarness`**: Test harness that uses mock tool registries to test workflows

## Benefits of Using Tool Recordings

1. **Deterministic testing**: Ensures consistent test results regardless of external conditions
2. **Offline testing**: Test workflows without network connectivity or access to production systems
3. **Performance**: Significantly faster test execution compared to running actual tools
4. **Reproducibility**: Easily reproduce and debug specific workflow scenarios
5. **No side effects**: Test workflows without worrying about modifying production data

## Recording Tool Executions

To record tool executions during a workflow run, use the `@record_tool_executions` decorator:

```python
from core.utils.testing import record_tool_executions

@record_tool_executions(output_file="tests/recordings/my_workflow_recording.json")
def my_workflow_function(variables):
    # Your workflow implementation
    # Tool calls will be automatically recorded
    pass
```

This will create a JSON file containing all tool executions, including:
- Tool name
- Input parameters
- Output response
- Timestamps
- Tool execution status (success/error)

## Using Recordings for Testing

There are two main approaches to using recordings for testing:

### 1. Using Recorded Tool Executions

```python
from core.utils.testing import (
    WorkflowTestHarness,
    load_tool_recordings,
    create_mock_registry_from_recordings
)

# Load recordings from a file
recordings = load_tool_recordings("tests/recordings/my_workflow_recording.json")

# Create a mock registry from the recordings
mock_registry = create_mock_registry_from_recordings(recordings)

# Create a test harness with the mock registry
test_harness = WorkflowTestHarness(
    workflow_func=my_workflow_function,
    mock_registry=mock_registry
)

# Execute the workflow with mock tools
result = test_harness.execute_workflow({
    "input_param1": "value1",
    "input_param2": "value2"
})

# Assert on the results
assert result["success"] is True
assert "expected_output" in result["result"]
```

### 2. Manually Defining Mock Tools

For more control, you can manually define mock tool responses:

```python
# Create a test harness
test_harness = WorkflowTestHarness(
    workflow_func=my_workflow_function
)

# Register mock tools with expected responses
test_harness.register_mock_tool(
    tool_name="my_tool",
    tool_response={
        "success": True,
        "result": {"key": "value"},
        "status": "success"
    }
)

# Execute and assert
result = test_harness.execute_workflow({"param": "value"})
assert result["success"] is True
```

## Testing Workflow Error Handling

Tool recordings are particularly useful for testing error handling:

```python
# Create a test harness
test_harness = WorkflowTestHarness(
    workflow_func=my_workflow_function
)

# Register a failing tool
test_harness.register_mock_tool(
    tool_name="my_tool",
    tool_response={
        "success": False,
        "error": "Simulated error",
        "status": "error"
    }
)

# Execute and verify error handling
result = test_harness.execute_workflow({"param": "value"})
assert result["success"] is False
assert "error" in result
```

## Working with Tool Execution Recordings

### Recording File Format

The recording JSON file has the following structure:

```json
[
  {
    "tool_name": "my_tool",
    "input": {"param1": "value1"},
    "output": {"success": true, "result": {...}, "status": "success"},
    "timestamp": "2023-06-15T14:30:00Z",
    "execution_id": "12345"
  },
  ...
]
```

### Modifying Recordings

You can manually edit recording files to test different scenarios:
- Change tool responses to simulate different outcomes
- Add error responses to test error handling
- Modify input parameters to test different input conditions

### Best Practices

1. **Record once, test many times**: Create recording files for key scenarios and reuse them
2. **Version control recordings**: Store recordings in version control with your tests
3. **Clean sensitive data**: Remove any sensitive data from recordings before committing
4. **Use descriptive filenames**: Name recording files to reflect the scenario they represent
5. **Create focused recordings**: Record only the tools needed for specific test cases

## Example Workflow

See the full examples in:
- `examples/mock_compliance_workflow.py` - Example workflow with tool recording
- `examples/test_with_recordings.py` - Example tests using the recordings

## Related Documentation

- [Testing Workflows and Tasks](testing_workflows_and_tasks.md)
- [Workflow System](workflow_system.md)
- [Creating Custom Tools](creating_custom_tools.md) 