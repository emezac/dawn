#!/usr/bin/env python3

"""
Simple test for MockToolRegistry initialization.
"""  # noqa: D202

import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tools.mock_registry import MockToolRegistry
from core.utils.testing import create_mock_tool_execution

def test_mock_registry_initialization():
    """Test MockToolRegistry initialization with mock executions."""
    # Create mock executions
    mock_executions = {
        "test_tool": [
            create_mock_tool_execution(
                {"param": "value"},
                {"success": True, "result": "Test result"}
            )
        ]
    }
    
    # Create registry
    mock_registry = MockToolRegistry()
    
    # Configure mock executions
    for tool_name, executions in mock_executions.items():
        for execution in executions:
            if "exception" in execution and execution["exception"]:
                # Configure an exception to be raised
                mock_registry.mock_tool_as_failure(
                    tool_name, 
                    str(execution["exception"]), 
                )
            else:
                # Configure a success response
                try:
                    mock_registry.add_mock_response(
                        tool_name,
                        execution["input_pattern"],
                        execution["output"] or {}
                    )
                    print(f"Successfully added mock response for {tool_name}")
                except Exception as e:
                    print(f"Error adding mock response: {e}")
    
    print("MockToolRegistry initialized successfully with mock executions")
    
    # Try executing the tool
    try:
        result = mock_registry.execute_tool("test_tool", {"param": "value"})
        print(f"Tool execution result: {result}")
    except Exception as e:
        print(f"Error executing tool: {e}")
        

if __name__ == "__main__":
    print("Testing MockToolRegistry initialization...")
    test_mock_registry_initialization() 