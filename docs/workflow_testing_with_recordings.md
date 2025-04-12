# Testing Workflows with Tool Execution Recordings

This guide explains how to use Dawn's tool execution recording and replaying functionality to create reliable, deterministic tests for your workflows.

## Overview

Dawn provides utilities to record tool executions during a workflow run and replay them in your tests. This allows you to:

1. Create deterministic test cases without relying on actual API calls or external services
2. Test complex workflows without setting up elaborate mocks for each tool
3. Capture real-world interactions and use them for regression testing
4. Test error handling by injecting recorded failures

## Recording Tool Executions

The recording process captures the inputs and outputs of tool executions during an actual workflow run. You can implement this in your workflow module with the following pattern:

```python
import json
import os
import pathlib
from typing import Dict, List, Any
from core.tools.registry_access import execute_tool

# Storage for recording tool executions
recorded_executions = []

def execute_and_record_tool(tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool and record the inputs and outputs for testing.
    
    Args:
        tool_name: The name of the tool to execute
        input_data: The input data for the tool
        
    Returns:
        The result of the tool execution
    """
    # Execute the actual tool
    result = execute_tool(tool_name, input_data)
    
    # Record the execution
    recorded_executions.append({
        "tool_name": tool_name,
        "input_data": input_data,
        "result": result
    })
    
    return result

def save_recorded_executions(file_path: str) -> None:
    """
    Save the recorded tool executions to a JSON file.
    
    Args:
        file_path: The path to save the recordings to
    """
    # Create directory if it doesn't exist
    recording_dir = os.path.dirname(file_path)
    pathlib.Path(recording_dir).mkdir(parents=True, exist_ok=True)
    
    # Save recordings to JSON file
    with open(file_path, 'w') as f:
        json.dump(recorded_executions, f, indent=2)
    
    print(f"Saved {len(recorded_executions)} recorded tool executions to {file_path}")

def run_recorded_workflow() -> Dict[str, Any]:
    """
    Run your workflow and record all tool executions.
    
    Returns:
        Dictionary with workflow results
    """
    # Clear previous recordings
    global recorded_executions
    recorded_executions = []
    
    try:
        # Run your actual workflow here, using execute_and_record_tool instead of execute_tool
        # Example:
        # result = your_workflow_function()
        
        # For illustration, we'll just run some sample tool executions
        execute_and_record_tool("list_vector_stores", {})
        execute_and_record_tool("search_vector_store", {
            "vector_store_id": "vs_example",
            "query": "Sample query"
        })
        
        # Save recordings
        save_recorded_executions("tests/recordings/workflow_recording.json")
        
        return {"success": True, "message": "Workflow completed and recorded"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Creating a Mock Tool Registry for Testing

To replay recorded tool executions in your tests, create a mock tool registry that returns predetermined results:

```python
import json
from typing import Dict, Any, List, Callable, Optional, Union
from core.tools.registry import ToolRegistry

class MockToolRegistry:
    """
    A mock tool registry that returns predetermined results for tool executions.
    
    This is used for testing workflows with recorded tool executions.
    """
    
    def __init__(self, recordings_file: Optional[str] = None):
        """
        Initialize the mock tool registry.
        
        Args:
            recordings_file: Optional path to a JSON file containing recorded tool executions
        """
        self.tool_executions = []
        self.tools = {}
        
        if recordings_file:
            self.load_recordings(recordings_file)
    
    def load_recordings(self, file_path: str) -> None:
        """
        Load recorded tool executions from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing recorded tool executions
        """
        with open(file_path, 'r') as f:
            self.tool_executions = json.load(f)
    
    def register_tool(self, tool_name: str, handler: Callable) -> None:
        """
        Register a tool in the mock registry.
        
        Args:
            tool_name: The name of the tool
            handler: The handler function for the tool
        """
        self.tools[tool_name] = handler
    
    def create_mock_tool_execution(self, 
                                  tool_name: str, 
                                  input_matcher: Union[Dict, Callable],
                                  result: Dict[str, Any]) -> None:
        """
        Create a mock tool execution.
        
        Args:
            tool_name: The name of the tool
            input_matcher: Either a dict to match against input data, or a function that takes input data and returns a boolean
            result: The result to return when the tool is executed with matching input
        """
        self.tool_executions.append({
            "tool_name": tool_name,
            "input_matcher": input_matcher,
            "result": result
        })
    
    def execute_tool(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool using recorded results.
        
        Args:
            tool_name: The name of the tool to execute
            input_data: The input data for the tool
            
        Returns:
            The recorded result for the tool execution
        """
        # First check for exact matches in recorded executions
        for execution in self.tool_executions:
            if execution["tool_name"] == tool_name:
                input_matcher = execution.get("input_matcher")
                
                # If it's a callable, use it to match the input
                if callable(input_matcher):
                    if input_matcher(input_data):
                        return execution["result"]
                # If it's a dictionary or None, check for direct equality
                elif input_matcher == input_data:
                    return execution["result"]
                # If it's in the flat recorded format
                elif "input_data" in execution and execution["input_data"] == input_data:
                    return execution["result"]
        
        # If no match found, return a default error
        return {
            "success": False,
            "error": f"No matching mock execution found for tool '{tool_name}'"
        }
```

## Testing a Workflow with Recorded Executions

Here's how to use the `MockToolRegistry` in your tests:

```python
import unittest
import os
import sys
from unittest.mock import patch
from core.tools.registry_access import get_registry, reset_registry
from core.services import get_services, reset_services

# Import your workflow module
# from examples.your_workflow_module import YourWorkflow

class TestWorkflowWithRecordings(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        # Reset both the registry singleton and services container
        reset_registry()
        reset_services()
        
        # Create a mock tool registry
        self.mock_registry = MockToolRegistry("tests/recordings/workflow_recording.json")
        
        # Get the services container and inject our mock registry
        services = get_services()
        services.tool_registry = self.mock_registry
    
    def test_workflow_execution(self):
        """Test workflow execution with recorded tool executions."""
        # Create the workflow
        # workflow = YourWorkflow()
        
        # Run the workflow
        # result = workflow.run()
        
        # Assert expected results
        # self.assertTrue(result["success"])
        # ... other assertions based on your workflow ...
    
    def test_workflow_error_handling(self):
        """Test workflow error handling with recorded failure executions."""
        # Inject a failure result for a specific tool execution
        self.mock_registry.create_mock_tool_execution(
            tool_name="search_vector_store",
            input_matcher={"vector_store_id": "vs_example", "query": "Sample query"},
            result={"success": False, "error": "Simulated failure"}
        )
        
        # Create the workflow
        # workflow = YourWorkflow()
        
        # Run the workflow
        # result = workflow.run()
        
        # Assert that error handling worked correctly
        # self.assertFalse(result["success"])
        # ... other assertions based on your error handling ...
```

## Example: Smart Compliance Workflow Test

Here's a concrete example using the smart compliance workflow:

```python
import unittest
import os
import json
import sys
from unittest.mock import patch
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.tools.registry_access import get_registry, reset_registry
from core.services import get_services, reset_services
from examples.smart_compliance_workflow import build_compliance_check_workflow, WORKFLOW_INPUT

class MockToolRegistry:
    # ... (implementation from above) ...

class TestComplianceWorkflow(unittest.TestCase):
    def setUp(self):
        """Set up the test environment with recorded executions."""
        # Reset singletons
        reset_registry()
        reset_services()
        
        # Load recorded executions
        recordings_file = "tests/recordings/compliance_workflow_recording.json"
        self.mock_registry = MockToolRegistry(recordings_file)
        
        # Register the mock registry
        services = get_services()
        services.tool_registry = self.mock_registry
        
        # Add any additional mock tool handlers needed
        self.mock_registry.register_tool("log_alert", lambda input_data: {"success": True, "result": "Alert logged"})
        self.mock_registry.register_tool("log_info", lambda input_data: {"success": True, "result": "Info logged"})
    
    def test_compliance_workflow_execution(self):
        """Test the compliance workflow with recorded tool executions."""
        # Build the workflow with mock vector store IDs
        workflow = build_compliance_check_workflow(
            compliance_vs_id="vs_mock_compliance_12345",
            ltm_vs_id="vs_mock_ltm_67890",
            initial_input=WORKFLOW_INPUT
        )
        
        # Initialize the workflow engine
        from core.engine import WorkflowEngine
        engine = WorkflowEngine()
        
        # Run the workflow
        result = engine.run_workflow(workflow)
        
        # Check that the workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Verify specific tasks completed as expected
        completed_tasks = [task.id for task in workflow.tasks.values() if task.status == "completed"]
        self.assertIn("task_1_analyze_risk_llm", completed_tasks)
        self.assertIn("task_2_parse_json_output", completed_tasks)
        self.assertIn("task_7_log_info", completed_tasks)
```

## Best Practices for Recording and Replaying

1. **Keep recordings up to date**: Re-record your tool executions when your workflow logic changes significantly.

2. **Store recordings in version control**: These are valuable test fixtures that should be tracked alongside your code.

3. **Record different scenarios**: Create multiple recording files for different test cases (happy path, error paths, etc.).

4. **Use function matchers for dynamic inputs**: When input data contains dynamic values like timestamps or IDs, use callable matchers:

   ```python
   # Example function matcher that ignores the timestamp field
   def match_without_timestamp(recorded_input):
       def matcher(input_data):
           input_copy = input_data.copy()
           recorded_copy = recorded_input.copy()
           
           # Remove timestamp fields before comparing
           if "timestamp" in input_copy:
               del input_copy["timestamp"]
           if "timestamp" in recorded_copy:
               del recorded_copy["timestamp"]
               
           return input_copy == recorded_copy
       return matcher
   
   # Use the matcher in a test
   mock_registry.create_mock_tool_execution(
       tool_name="search_vector_store",
       input_matcher=match_without_timestamp({"query": "example"}),
       result={"success": True, "result": [...]}
   )
   ```

5. **Combine with direct mocks**: You can combine recorded executions with direct mocks for maximum flexibility in testing.

## Related Documentation

- [Workflow System](workflow_system.md)
- [Testing Framework Overview](testing_framework.md)
- [Tool Registry](tool_registry.md) 