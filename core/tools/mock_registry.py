"""
Mock Tool Registry for testing.

This module provides a MockToolRegistry class that can be used in tests
without requiring real service connections. It allows defining mock responses
for tools and recording/replaying tool executions.
"""

import json
import os
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast
from unittest.mock import MagicMock
import inspect

from core.errors import ErrorCode, create_error_response, create_success_response
from core.tools.registry import ToolRegistry
from core.tools.response_format import format_tool_response
from core.services import get_services, reset_services
from core.tools.registry_access import reset_registry

logger = logging.getLogger(__name__)


class MockToolRegistry(ToolRegistry):
    """
    Mock implementation of ToolRegistry for testing without real services.
    
    Allows defining mock responses for tools, recording tool executions,
    and replaying recorded executions. This enables testing workflows
    without requiring connection to real services.
    """  # noqa: D202
    
    def __init__(self):
        """Initialize the mock registry."""
        super().__init__()
        # Mock responses by tool name and input hash
        self.mock_responses: Dict[str, Dict[str, Any]] = {}
        # Direct response overrides by tool name
        self.response_overrides: Dict[str, Any] = {}
        # Recording of tool executions
        self.recorded_executions: List[Dict[str, Any]] = []
        # Whether to record executions
        self.recording_enabled = False
        # Whether to raise exceptions for unmocked tools
        self.strict_mode = False
        # Default response for unmocked tools
        self.default_response = create_success_response({"mock_default": True})

    def add_mock_response(self, tool_name: str, input_data: Dict[str, Any], response: Dict[str, Any]) -> None:
        """
        Add a mock response for a specific tool and input data.
        
        Args:
            tool_name: Name of the tool to mock
            input_data: Expected input data that should trigger this response
            response: The response to return
        """
        input_hash = self._hash_input(input_data)
        if tool_name not in self.mock_responses:
            self.mock_responses[tool_name] = {}
        self.mock_responses[tool_name][input_hash] = response
        logger.debug(f"Added mock response for {tool_name} with input hash {input_hash}")

    def override_response(self, tool_name: str, response: Any) -> None:
        """
        Override all responses for a tool regardless of input.
        
        Args:
            tool_name: Name of the tool to override
            response: Response to return for any input to this tool
        """
        self.response_overrides[tool_name] = response
        logger.debug(f"Added response override for {tool_name}")
    
    def remove_override(self, tool_name: str) -> None:
        """
        Remove a response override for a tool.
        
        Args:
            tool_name: Name of the tool to remove override for
        """
        if tool_name in self.response_overrides:
            del self.response_overrides[tool_name]
            logger.debug(f"Removed response override for {tool_name}")
    
    def clear_mocks(self) -> None:
        """Clear all mock responses and overrides."""
        self.mock_responses.clear()
        self.response_overrides.clear()
        logger.debug("Cleared all mock responses and overrides")
    
    def mock_tool_as_success(self, tool_name: str, result: Any = None) -> None:
        """
        Set a tool to always return success with an optional result.
        
        Args:
            tool_name: Name of the tool to mock
            result: Result data to include in the response (default: empty dict)
        """
        result_data = {} if result is None else result
        self.override_response(tool_name, create_success_response(result_data))
        logger.debug(f"Set {tool_name} to always return success with result: {result_data}")
    
    def mock_tool_as_failure(self, tool_name: str, error_message: str, 
                            error_code: ErrorCode = ErrorCode.EXECUTION_TOOL_FAILED) -> None:
        """
        Set a tool to always return failure with the given error.
        
        Args:
            tool_name: Name of the tool to mock
            error_message: Error message to include
            error_code: Optional error code to use
        """
        self.override_response(
            tool_name, 
            create_error_response(error_message=error_message, error_code=error_code, tool_name=tool_name)
        )
        logger.debug(f"Set {tool_name} to always return failure with error: {error_message}")
    
    def start_recording(self) -> None:
        """Start recording tool executions."""
        self.recording_enabled = True
        self.recorded_executions.clear()
        logger.debug("Started recording tool executions")
    
    def stop_recording(self) -> None:
        """Stop recording tool executions."""
        self.recording_enabled = False
        logger.debug(f"Stopped recording tool executions. Recorded {len(self.recorded_executions)} executions.")
    
    def get_recorded_executions(self) -> List[Dict[str, Any]]:
        """
        Get the list of recorded tool executions.
        
        Returns:
            List of dictionaries containing tool name, input data, and response
        """
        return self.recorded_executions
    
    def save_recordings(self, file_path: str) -> None:
        """
        Save recorded executions to a JSON file.
        
        Args:
            file_path: Path to the file where recordings should be saved
        """
        with open(file_path, 'w') as f:
            json.dump(self.recorded_executions, f, indent=2)
        logger.debug(f"Saved {len(self.recorded_executions)} recorded executions to {file_path}")
    
    def load_recordings(self, file_path: str) -> None:
        """
        Load recorded executions from a JSON file.
        
        Args:
            file_path: Path to the file containing previously saved recordings
        """
        if not os.path.exists(file_path):
            logger.warning(f"Recordings file {file_path} not found")
            return
            
        with open(file_path, 'r') as f:
            self.recorded_executions = json.load(f)
        logger.debug(f"Loaded {len(self.recorded_executions)} recorded executions from {file_path}")
    
    def set_strict_mode(self, strict: bool) -> None:
        """
        Set whether to raise exceptions for unmocked tools.
        
        Args:
            strict: If True, raises an exception for unmocked tools
        """
        self.strict_mode = strict
        logger.debug(f"Set strict mode to {strict}")
    
    def set_default_response(self, response: Dict[str, Any]) -> None:
        """
        Set the default response for unmocked tools.
        
        Args:
            response: Response to return for unmocked tools
        """
        self.default_response = response
        logger.debug(f"Set default response to {response}")
    
    def execute_tool(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with the given input data.
        
        This override checks for mock responses before attempting real execution.
        
        Args:
            name: The name of the tool to execute
            data: The input data for the tool
            
        Returns:
            The tool execution result
        """
        # Record this execution if recording is enabled
        if self.recording_enabled:
            execution_record = {
                "tool_name": name,
                "input_data": data,
                "timestamp": "recorded" # Could add actual timestamp if needed
            }
            
        # Check for a response override first
        if name in self.response_overrides:
            response = self.response_overrides[name]
            logger.debug(f"Using response override for {name}")
            
            # Record the response if we're recording
            if self.recording_enabled:
                execution_record["response"] = response
                self.recorded_executions.append(execution_record)
                
            return response
        
        # Check for a mock response based on input data
        input_hash = self._hash_input(data)
        if name in self.mock_responses and input_hash in self.mock_responses[name]:
            response = self.mock_responses[name][input_hash]
            logger.debug(f"Using mock response for {name} with input hash {input_hash}")
            
            # Record the response if we're recording
            if self.recording_enabled:
                execution_record["response"] = response
                self.recorded_executions.append(execution_record)
                
            return response
        
        # Check if the tool is registered with the parent class
        if name in self.tools:
            try:
                # Execute the tool normally
                response = super().execute_tool(name, data)
                
                # Record the response if we're recording
                if self.recording_enabled:
                    execution_record["response"] = response
                    self.recorded_executions.append(execution_record)
                    
                return response
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                
                # In strict mode, re-raise the exception
                if self.strict_mode:
                    raise
                    
                # Use default response for error
                response = create_error_response(
                    error_message=f"Error executing tool {name}: {str(e)}",
                    error_code=ErrorCode.EXECUTION_TOOL_FAILED,
                    tool_name=name
                )
                
                # Record the response if we're recording
                if self.recording_enabled:
                    execution_record["response"] = response
                    self.recorded_executions.append(execution_record)
                    
                return response
        
        # Tool not found and not mocked
        if self.strict_mode:
            raise ValueError(f"Tool '{name}' not found and not mocked")
            
        # Use default response
        logger.warning(f"Using default response for unmocked tool: {name}")
        
        # Record the default response if we're recording
        if self.recording_enabled:
            execution_record["response"] = self.default_response
            self.recorded_executions.append(execution_record)
            
        return self.default_response
    
    def _hash_input(self, input_data: Dict[str, Any]) -> str:
        """
        Create a string hash of input data for lookup.
        
        Args:
            input_data: The input data to hash
            
        Returns:
            A string hash of the input data
        """
        # Simple string representation - could be improved with more robust hashing
        return json.dumps(input_data, sort_keys=True)
    
    def create_mock_from_recordings(self) -> None:
        """
        Create mock responses based on recorded executions.
        
        This allows recording a session with real services and then
        creating mocks that will replay the same responses.
        """
        for execution in self.recorded_executions:
            tool_name = execution.get("tool_name")
            input_data = execution.get("input_data", {})
            response = execution.get("response", {})
            
            if tool_name and response:
                self.add_mock_response(tool_name, input_data, response)
                
        logger.debug(f"Created mock responses from {len(self.recorded_executions)} recorded executions")


# --- Helper functions for testing ---

def create_mock_registry() -> MockToolRegistry:
    """
    Create a new MockToolRegistry instance.
    
    Returns:
        A new MockToolRegistry instance
    """
    return MockToolRegistry()


def setup_mock_registry_for_test() -> MockToolRegistry:
    """
    Set up a MockToolRegistry for use in tests.
    
    This function:
    1. Creates a new MockToolRegistry
    2. Registers common mock responses
    3. Returns the registry for test use
    
    Returns:
        A configured MockToolRegistry instance
    """
    registry = create_mock_registry()
    
    # Set up common mock responses
    registry.mock_tool_as_success("list_vector_stores", [
        {"id": "vs_mock_1", "name": "Mock Vector Store 1"},
        {"id": "vs_mock_2", "name": "Mock Vector Store 2"}
    ])
    
    registry.mock_tool_as_success("create_vector_store", "vs_mock_new")
    
    registry.mock_tool_as_success("upload_file_to_vector_store", {
        "file_id": "file_mock_1",
        "status": "uploaded"
    })
    
    registry.mock_tool_as_success("file_read", {
        "content": "This is mock content from the file read tool.",
        "metadata": {"source": "mock_file.txt"}
    })
    
    return registry 

# --- Service integration functions ---

def register_mock_registry_with_services() -> MockToolRegistry:
    """
    Register a MockToolRegistry with the services container.
    
    This function:
    1. Resets the existing registry and services
    2. Creates a new MockToolRegistry
    3. Registers it with the services container
    4. Returns the registry for further configuration
    
    Returns:
        The registered MockToolRegistry instance
    """
    # Reset existing services and registry
    reset_services()
    reset_registry()
    
    # Create and set up the mock registry
    mock_registry = setup_mock_registry_for_test()
    
    # Get the services container and register the mock registry
    services = get_services()
    services.register_service(mock_registry, ToolRegistry, "tool_registry")
    
    logger.info("Registered MockToolRegistry with services container")
    return mock_registry

def with_mock_registry(func: Callable) -> Callable:
    """
    Decorator to use a MockToolRegistry for a test function.
    
    This decorator:
    1. Sets up a MockToolRegistry before the test
    2. Registers it with the services container
    3. Passes the registry to the test function
    4. Cleans up after the test
    
    Args:
        func: The test function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        # Set up the mock registry
        mock_registry = register_mock_registry_with_services()
        
        try:
            # Call the test function with the mock registry
            if "mock_registry" in inspect.signature(func).parameters:
                return func(*args, mock_registry=mock_registry, **kwargs)
            else:
                return func(*args, **kwargs)
        finally:
            # Clean up
            reset_services()
            reset_registry()
    
    return wrapper 