#!/usr/bin/env python3
"""
Test Compliance Workflow with Recordings

This script demonstrates how to test a compliance workflow using recorded tool executions.
The test approach uses a combination of recordings and manual mocks to validate
the workflow behavior in various scenarios.

Usage:
  python examples/test_with_recordings.py

The script will run three test cases:
1. Testing with previously recorded tool executions
2. Testing with manual mocks (no recordings)
3. Testing error handling in the workflow
"""  # noqa: D202

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Union

# Add parent directory to path to allow importing from examples
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the mock compliance workflow module
from examples.mock_compliance_workflow import (
    MockToolRegistry,
    compliance_workflow,
    list_vector_stores,
    search_vector_store,
    compliance_check
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define constants
RECORDINGS_DIR = Path("tests/recordings")
RECORDING_FILE = RECORDINGS_DIR / "compliance_workflow_recording.json"

# Helper functions
def create_mock_tool_registry() -> MockToolRegistry:
    """
    Create and configure a mock tool registry with default tools.
    
    Returns:
        Configured MockToolRegistry
    """
    registry = MockToolRegistry()
    registry.register_tool("list_vector_stores", list_vector_stores)
    registry.register_tool("search_vector_store", search_vector_store)
    registry.register_tool("compliance_check", compliance_check)
    return registry

def load_tool_recordings(recording_file: Path) -> List[Dict[str, Any]]:
    """
    Load tool execution recordings from a JSON file.
    
    Args:
        recording_file: Path to the recording file
        
    Returns:
        List of tool execution recordings
    """
    if not recording_file.exists():
        logger.warning(f"Recording file not found: {recording_file}")
        return []
    
    try:
        with open(recording_file, 'r') as f:
            recordings = json.load(f)
        
        logger.info(f"Loaded {len(recordings)} tool execution recordings from {recording_file}")
        return recordings
    except Exception as e:
        logger.error(f"Error loading recordings: {str(e)}")
        return []

def create_mock_tool_from_recording(recordings: List[Dict[str, Any]]) -> Dict[str, Callable]:
    """
    Create tool functions from recorded tool executions.
    
    Args:
        recordings: List of tool execution recordings
        
    Returns:
        Dictionary mapping tool names to mock functions
    """
    tool_functions = {}
    
    for tool_name in set(r["tool_name"] for r in recordings):
        tool_recordings = [r for r in recordings if r["tool_name"] == tool_name]
        
        def create_tool_func(recordings):
            def mock_tool(**kwargs):
                # Find a matching recording based on parameters
                for recording in recordings:
                    recording_params = recording["parameters"]
                    
                    # Check if parameters match
                    if all(k in recording_params and recording_params[k] == v 
                           for k, v in kwargs.items()):
                        logger.info(f"Using recorded response for {recording['tool_name']}")
                        return recording["result"]
                
                # If no matching recording found, log warning
                logger.warning(f"No matching recording found for {recordings[0]['tool_name']} with params: {kwargs}")
                return {
                    "success": False,
                    "error": f"No matching recording for {recordings[0]['tool_name']} with params: {kwargs}",
                    "status": "error"
                }
            
            return mock_tool
        
        tool_functions[tool_name] = create_tool_func(tool_recordings)
    
    return tool_functions

def patch_tool_registry_with_recordings(registry: MockToolRegistry, recordings: List[Dict[str, Any]]) -> None:
    """
    Patch a tool registry with mock functions created from recordings.
    
    Args:
        registry: The tool registry to patch
        recordings: List of tool execution recordings
    """
    mock_tools = create_mock_tool_from_recording(recordings)
    
    for tool_name, tool_func in mock_tools.items():
        registry.register_tool(tool_name, tool_func)
        logger.info(f"Registered mock tool from recording: {tool_name}")

def assert_risk_level(result: Dict[str, Any], expected_level: str) -> bool:
    """
    Assert that the workflow result has the expected risk level.
    
    Args:
        result: Workflow result
        expected_level: Expected risk level
        
    Returns:
        True if assertion passes, False otherwise
    """
    if not result["success"]:
        logger.error(f"Workflow failed: {result.get('error', 'Unknown error')}")
        return False
    
    actual_level = result["result"].get("risk_level")
    if actual_level != expected_level:
        logger.error(f"Expected risk level '{expected_level}', got '{actual_level}'")
        return False
    
    logger.info(f"Risk level assertion passed: {actual_level}")
    return True

# Test functions
def test_compliance_workflow_with_recordings() -> bool:
    """
    Test the compliance workflow using recorded tool executions.
    
    Returns:
        True if the test passes, False otherwise
    """
    logger.info("Running test_compliance_workflow_with_recordings")
    
    # Load recordings
    recordings = load_tool_recordings(RECORDING_FILE)
    if not recordings:
        logger.error("No recordings available for testing")
        return False
    
    # Create registry with recording-based mocks
    registry = create_mock_tool_registry()
    patch_tool_registry_with_recordings(registry, recordings)
    
    # Monkey patch the execute_tool method
    original_execute_tool = MockToolRegistry.execute_tool
    MockToolRegistry.execute_tool = registry.execute_tool
    
    try:
        # Run the compliance workflow
        result = compliance_workflow(
            data_type="user_emails",
            query="Find emails containing sensitive information"
        )
        
        # Verify the result
        success = assert_risk_level(result, "high")
        
        # Check for specific compliance issues
        if success and result["success"]:
            issues = result["result"].get("compliance_issues", [])
            if not any("SSN" in issue for issue in issues):
                logger.error("Expected to find SSN-related compliance issue")
                success = False
        
        return success
    
    finally:
        # Restore original method
        MockToolRegistry.execute_tool = original_execute_tool

def test_workflow_without_recordings() -> bool:
    """
    Test the compliance workflow using manually defined mock tools.
    
    Returns:
        True if the test passes, False otherwise
    """
    logger.info("Running test_workflow_without_recordings")
    
    # Create a registry with custom mock tools
    registry = MockToolRegistry()
    
    # Define custom mock tools
    def mock_list_vector_stores(**kwargs):
        return {
            "success": True,
            "result": ["medical_records"],
            "status": "success"
        }
    
    def mock_search_vector_store(store_name, query, **kwargs):
        if store_name != "medical_records":
            return {
                "success": False,
                "error": f"Unknown store: {store_name}",
                "status": "error"
            }
        
        return {
            "success": True,
            "result": {
                "matches": [
                    {
                        "id": "test-patient",
                        "metadata": {
                            "content": "Patient: Test Patient, DOB: 01/01/1990, Diagnosis: Test Condition"
                        }
                    }
                ]
            },
            "status": "success"
        }
    
    def mock_compliance_check(content, **kwargs):
        if "patient" in content.lower():
            return {
                "success": True,
                "result": {
                    "risk_level": "high",
                    "compliance_issues": ["Medical information found"],
                    "recommended_actions": ["Apply HIPAA controls"]
                },
                "status": "success"
            }
        else:
            return {
                "success": True,
                "result": {
                    "risk_level": "low",
                    "compliance_issues": [],
                    "recommended_actions": []
                },
                "status": "success"
            }
    
    # Register mock tools
    registry.register_tool("list_vector_stores", mock_list_vector_stores)
    registry.register_tool("search_vector_store", mock_search_vector_store)
    registry.register_tool("compliance_check", mock_compliance_check)
    
    # Monkey patch the execute_tool method
    original_execute_tool = MockToolRegistry.execute_tool
    MockToolRegistry.execute_tool = registry.execute_tool
    
    try:
        # Run the compliance workflow
        result = compliance_workflow(
            data_type="medical_records",
            query="Find patient records"
        )
        
        # Verify the result
        success = assert_risk_level(result, "high")
        
        # Check for specific compliance issues
        if success and result["success"]:
            issues = result["result"].get("compliance_issues", [])
            if not any("Medical" in issue for issue in issues):
                logger.error("Expected to find medical-related compliance issue")
                success = False
        
        return success
    
    finally:
        # Restore original method
        MockToolRegistry.execute_tool = original_execute_tool

def test_workflow_error_handling() -> bool:
    """
    Test that the compliance workflow handles errors properly.
    
    Returns:
        True if the test passes, False otherwise
    """
    logger.info("Running test_workflow_error_handling")
    
    # Create a registry with failing mock tools
    registry = MockToolRegistry()
    
    # Define a tool that fails
    def mock_failing_search(**kwargs):
        return {
            "success": False,
            "error": "Simulated search failure",
            "status": "error"
        }
    
    # Register tools (list_vector_stores succeeds, search_vector_store fails)
    registry.register_tool("list_vector_stores", list_vector_stores)
    registry.register_tool("search_vector_store", mock_failing_search)
    registry.register_tool("compliance_check", compliance_check)
    
    # Monkey patch the execute_tool method
    original_execute_tool = MockToolRegistry.execute_tool
    MockToolRegistry.execute_tool = registry.execute_tool
    
    try:
        # Run the compliance workflow
        result = compliance_workflow(
            data_type="user_emails",
            query="Find sensitive emails"
        )
        
        # Verify the result - should not succeed
        if result["success"]:
            logger.error("Workflow should have failed but succeeded")
            return False
        
        # Verify error message contains the simulated failure
        error_msg = result.get("error", "")
        if "Simulated search failure" not in error_msg:
            logger.error(f"Expected error message to contain 'Simulated search failure', got: {error_msg}")
            return False
        
        logger.info("Error handling test passed")
        return True
    
    finally:
        # Restore original method
        MockToolRegistry.execute_tool = original_execute_tool

def main():
    """
    Run all test cases and summarize results.
    """
    # Ensure recordings directory exists
    RECORDINGS_DIR.mkdir(exist_ok=True, parents=True)
    
    # Run test cases
    test_cases = [
        ("Test with recordings", test_compliance_workflow_with_recordings),
        ("Test without recordings", test_workflow_without_recordings),
        ("Test error handling", test_workflow_error_handling)
    ]
    
    results = []
    for name, test_func in test_cases:
        logger.info(f"Running test case: {name}")
        success = test_func()
        results.append((name, success))
        logger.info(f"Test case '{name}': {'PASSED' if success else 'FAILED'}")
    
    # Print summary
    logger.info("Test Summary:")
    for name, success in results:
        logger.info(f"  {name}: {'PASSED' if success else 'FAILED'}")
    
    # Return exit code based on success
    return 0 if all(success for _, success in results) else 1

if __name__ == "__main__":
    sys.exit(main()) 