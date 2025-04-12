#!/usr/bin/env python3
"""
Example script demonstrating how to record tool executions for testing.

This script shows different ways to record tool executions and use those recordings
for creating mock executions in tests.
"""  # noqa: D202

import os
import sys
import json

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils.testing import ToolExecutionRecorder, record_tool_executions
from core.workflow.tool_registry_access import get_tool_registry, execute_tool
from workflows.examples.document_analysis_workflow import DocumentAnalysisWorkflow


def example_1_basic_recording():
    """Demonstrate basic recording with ToolExecutionRecorder."""
    print("\n=== Example 1: Basic Recording ===")
    
    # Get the real tool registry
    real_registry = get_tool_registry()
    
    # Create a recorder that wraps the real registry
    recorder = ToolExecutionRecorder(real_registry, "examples/basic_recording.json")
    
    try:
        # Execute a tool through the recorder
        print("Executing tool via recorder...")
        result = recorder.execute_tool("file_system", {
            "path": "README.md",
            "operation": "read"
        })
        
        print(f"Successfully read file with {len(result.get('content', ''))} characters")
    except Exception as e:
        print(f"Error executing tool: {e}")
    
    # Save the recordings
    recorder.save_recordings()
    print(f"Saved recordings to {recorder.recording_file}")


@record_tool_executions
def example_function_with_tool_calls():
    """Example function that makes tool calls which will be recorded by the decorator."""
    print("Reading a file...")
    result = execute_tool("file_system", {
        "path": "README.md",
        "operation": "read"
    })
    
    print(f"Read {len(result.get('content', ''))} characters from README.md")
    
    # Try another file that might not exist to record an error case
    try:
        print("Trying to read a non-existent file...")
        execute_tool("file_system", {
            "path": "NON_EXISTENT_FILE.txt",
            "operation": "read"
        })
    except Exception as e:
        print(f"Error reading file as expected: {e}")
    
    return "Completed function with tool calls"


def example_2_using_decorator():
    """Demonstrate recording with the decorator."""
    print("\n=== Example 2: Recording with Decorator ===")
    
    # The decorator will automatically record all tool calls
    result = example_function_with_tool_calls()
    print(f"Function result: {result}")
    print("Recording was saved to the tests/recordings directory")


def example_3_workflow_recording():
    """Demonstrate recording tool executions from a workflow."""
    print("\n=== Example 3: Recording Workflow Tool Calls ===")
    
    # Create the workflow
    workflow = DocumentAnalysisWorkflow()
    
    # Get the workflow's tool registry
    registry = workflow.tool_registry
    
    # Create a recorder
    recorder = ToolExecutionRecorder(registry, "examples/workflow_recording.json")
    
    # Set the workflow to use the recorder
    workflow.set_tool_registry(recorder)
    
    try:
        # Execute the workflow with a file that exists
        print("Executing workflow with README.md...")
        context = {
            "document_path": "README.md"
        }
        result = workflow.execute(context)
        print("Workflow execution successful")
    except Exception as e:
        print(f"Workflow execution failed: {e}")
    
    # Save the recordings
    recorder.save_recordings()
    print(f"Saved workflow recordings to {recorder.recording_file}")


def example_4_generate_mocks_from_recording():
    """Demonstrate generating mock executions from a recording file."""
    print("\n=== Example 4: Generating Mocks from Recording ===")
    
    # Check if the recording file exists
    recording_file = "examples/basic_recording.json"
    if not os.path.exists(recording_file):
        print(f"Recording file {recording_file} not found. Run example_1_basic_recording first.")
        return
    
    # Load the recording file
    print(f"Loading recording from {recording_file}...")
    mock_executions = ToolExecutionRecorder.from_recording_file(recording_file)
    
    # Print the generated mock executions
    print("Generated mock executions:")
    for tool_name, executions in mock_executions.items():
        print(f"  Tool: {tool_name}, Number of executions: {len(executions)}")
    
    # Save the mock executions to a file for inspection
    with open("examples/generated_mocks.json", "w") as f:
        # Convert functions to string representations for JSON serialization
        serializable_mocks = {}
        for tool, execs in mock_executions.items():
            serializable_mocks[tool] = []
            for exec in execs:
                serializable_exec = {
                    "input_pattern": exec["input_pattern"],
                    "output": exec.get("output"),
                    "exception": str(exec.get("exception")) if exec.get("exception") else None
                }
                serializable_mocks[tool].append(serializable_exec)
        
        json.dump(serializable_mocks, f, indent=2)
    print("Saved serialized mock executions to examples/generated_mocks.json")


if __name__ == "__main__":
    print("=== Tool Execution Recording Examples ===")
    print("This script demonstrates different ways to record tool executions for testing.")
    
    # Run the examples
    example_1_basic_recording()
    example_2_using_decorator()
    example_3_workflow_recording()
    example_4_generate_mocks_from_recording()
    
    print("\nAll examples completed successfully!")
    print("Check the generated recording files and the documentation for more information.")
    print("See docs/recording_tool_executions.md for detailed documentation.") 