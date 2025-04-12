# Recording Tool Executions for Tests

This document explains how to use the tool execution recording functionality in the Dawn platform to create more realistic tests.

## Overview

The `ToolExecutionRecorder` allows you to:

1. Record real tool executions during development or manual testing
2. Save these recordings to a file
3. Generate mock executions from the recordings for use in tests
4. Replay the recorded tool executions in automated tests

This approach helps create more realistic test scenarios by using actual tool responses rather than manually crafted mock responses.

## Basic Usage

### Recording Tool Executions

You can record tool executions by wrapping an existing tool registry with a `ToolExecutionRecorder`:

```python
from core.utils.testing import ToolExecutionRecorder
from core.workflow.tool_registry_access import get_tool_registry

# Get the real tool registry
real_registry = get_tool_registry()

# Create a recorder wrapped around the real registry
recorder = ToolExecutionRecorder(real_registry)

# Use the recorder to execute tools
result = recorder.execute_tool("openai", {
    "prompt": "Extract entities from this text",
    "temperature": 0.7
})

# Save the recordings when done
recorder.save_recordings("my_recordings.json")
```

### Using the Recording Decorator

For convenience, a decorator is provided that automatically records all tool executions in a function:

```python
from core.utils.testing import record_tool_executions

@record_tool_executions
def process_document(document_path):
    # This function will have all its tool calls recorded
    from core.workflow.tool_registry_access import execute_tool
    
    # Read the document
    document = execute_tool("file_system", {
        "path": document_path,
        "operation": "read"
    })
    
    # Analyze with LLM
    analysis = execute_tool("openai", {
        "prompt": f"Analyze this document: {document['content']}",
        "temperature": 0.3
    })
    
    return analysis

# The tool executions will be automatically recorded when this function runs
result = process_document("my_document.pdf")
```

The recordings will be saved to a file in the `tests/recordings` directory with a timestamp in the filename.

### Generating Mocks from Recordings

You can convert recordings into mock executions for tests:

```python
from core.utils.testing import ToolExecutionRecorder

# Load recordings directly into mock executions
mock_executions = ToolExecutionRecorder.from_recording_file("my_recordings.json")

# Use the mock executions with a WorkflowTestHarness
from core.utils.testing import WorkflowTestHarness

workflow = MyWorkflow()
harness = WorkflowTestHarness(workflow, mock_executions, initial_variables={})
result = harness.execute()
```

## Advanced Usage

### Recording Specific Workflows

You can record tool executions for a specific workflow by wrapping the workflow's tool registry:

```python
from core.utils.testing import ToolExecutionRecorder

# Create a workflow
workflow = MyWorkflow()

# Get the workflow's tool registry
registry = workflow.tool_registry

# Create a recorder and replace the workflow's registry
recorder = ToolExecutionRecorder(registry)
workflow.set_tool_registry(recorder)

# Execute the workflow (all tool calls will be recorded)
result = workflow.execute(...)

# Save the recordings
recorder.save_recordings("my_workflow_recordings.json")
```

### Selective Recording

You can be selective about what gets recorded by controlling when the recorder is active:

```python
from core.utils.testing import ToolExecutionRecorder
from core.workflow.tool_registry_access import get_tool_registry, set_tool_registry

# Start with the real registry
real_registry = get_tool_registry()

# Only record certain operations
def process_with_selective_recording():
    # Create a recorder
    recorder = ToolExecutionRecorder(real_registry)
    
    # Normal unrecorded operation
    result1 = real_registry.execute_tool("tool1", {"param": "value"})
    
    # Start recording
    set_tool_registry(recorder)
    
    # This will be recorded
    result2 = execute_tool("openai", {"prompt": "Important operation"})
    
    # Stop recording
    set_tool_registry(real_registry)
    
    # Save what was recorded
    recorder.save_recordings()
    
    return result1, result2
```

## Testing Best Practices

When using recorded tool executions for tests, follow these best practices:

1. **Isolate recordings by functionality**: Create separate recording files for different features or workflows.

2. **Version control recordings**: For stable tests, commit recording files to version control.

3. **Refresh recordings periodically**: Update recordings when APIs or expected responses change.

4. **Add variability**: Create multiple recordings with different inputs to test a range of scenarios.

5. **Handle sensitive data**: Review recordings before committing to ensure they don't contain sensitive information.

6. **Combine with manual mocks**: For edge cases, supplement recordings with manually created mock executions.

## Example: Complete Testing Workflow

Here's a complete workflow for using recordings in tests:

1. **Record real executions**:
   ```python
   @record_tool_executions
   def manual_test():
       # Perform operations with real tool calls
       result = execute_tool("openai", {"prompt": "Test prompt"})
       print(result)
   
   # Run this during development to generate recordings
   manual_test()
   ```

2. **Create a test using the recordings**:
   ```python
   def test_my_workflow():
       # Load the recorded mock executions
       mock_executions = ToolExecutionRecorder.from_recording_file(
           "tests/recordings/tool_execution_20230615_152233.json"
       )
       
       # Use them in a test harness
       workflow = MyWorkflow()
       harness = WorkflowTestHarness(workflow, mock_executions)
       result = harness.execute()
       
       # Make assertions based on the expected results
       assert "expected_key" in result
       assert result["expected_key"] == "expected_value"
   ```

3. **Run the automated test**:
   ```bash
   python -m unittest tests/test_my_workflow.py
   ```

This approach gives you the best of both worlds: tests that use realistic tool responses without requiring external services during test execution. 