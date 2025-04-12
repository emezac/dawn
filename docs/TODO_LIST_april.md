# Dawn Framework - April 2025 TODO List

## Core Improvements Based on Smart Compliance Workflow Experience

### 1. Task Subsystem Enhancements

- [x] **Implement proper DirectHandlerTask as a core feature**
  - Create a proper `DirectHandlerTask` class in `core/task.py` that inherits from `Task`
  - Document the API and usage patterns
  - Add unit tests to verify behavior
  - Eliminate the need for monkey patching the `WorkflowEngine`

- [x] **Add plugin system for tool execution**
  - Create a plugin architecture to allow registering custom task executors
  - Enable providing custom execution strategies without modifying core classes
  - Support middleware-style wrapping of task execution

- [x] **Improve task output and variable resolution**
  - Fix variable interpolation in task inputs (${task_name.output_data[field]} → ${task_name.output_data.field}) ✅
  - Support for complex nested data structures in task outputs ✅
  - Add proper error handling for missing fields with fallbacks (${field | 'default'}) ✅
  - Implement extract_task_output utility for consistent output processing ✅
  - Add JSON parsing tasks between LLM tasks and decision tasks ✅
  - Standardize output structure for all task types ✅
  - Fix DirectHandlerTask dependencies parameter handling ✅
  - Update multiple workflows to use the new patterns: ✅
    - smart_compliance_workflow.py ✅
    - context_aware_legal_review_workflow.py ✅
    - complex_parallel_workflow_example.py ✅
    - simplified_compliance_workflow.py ✅
    - complex_conditional_workflow.py ✅
  - Add comprehensive documentation on task output and variable resolution best practices ✅

### 2. Registry Improvements

- [x] **Standardize tool registry access**
  - Created a registry_access.py module implementing the singleton pattern for registry access
  - Provided standardized utility functions for common registry operations
  - Updated key workflow examples to use the standardized access methods
  - Added comprehensive unit tests for registry access utilities
  - Documented best practices for registry access in the codebase

- [x] **Implement singleton patterns correctly**
  - Fixed tool registry instantiation to ensure consistent instance usage
  - Added proper dependency injection for registry access
  - Created a services container for framework-wide dependencies
  - Updated tests and examples to use the services container pattern

### 3. Error Handling and Reporting

- [x] **Standardize error reporting**
  - Create consistent error response format for all tools
  - Implement error codes and standardized error messages
  - [x] Add proper error propagation between tasks

- [x] **Improve exit code handling**
  - [x] Standardize exit code usage across all framework code
  - [x] Add wrapper for main functions to ensure consistent exit code behavior
  - [x] Create exit code documentation for framework users

### 4. Testing Infrastructure

- [x] **Create mock registry for testing**
  - [x] Implement a testing-specific registry that doesn't require real services
  - [X] Add testing utilities for workflows and tasks
  - [X] Support recording and replaying of tool execution for tests

- [x] **Add integration test suite for workflows**
  - [x] Create integration tests for core workflow features
    - Comprehensive test suite for error handling (test_error_handling.py)
    - Comprehensive test suite for variable resolution (test_variable_resolution.py)
    - Comprehensive test suite for parallel execution (test_parallel_execution.py)
    - Comprehensive test suite for conditional execution (test_conditional_execution.py)
    - Comprehensive test suite for retry mechanisms (test_retry_mechanism.py)
    - Comprehensive test suite for vector store workflows (test_vector_store_workflow.py)
  - [x] Test workflow engine with various task configurations
  - [x] Verify error handling and recovery mechanisms

### 5. Documentation Updates

- [x] **Update all examples to use the new patterns**
  - [x] Revise all example files to use the new DirectHandlerTask pattern
    - smart_compliance_workflow.py ✅
    - context_aware_legal_review_workflow.py ✅
    - complex_parallel_workflow_example.py ✅
  - [x] Ensure all examples use proper error handling
  - [x] Add comments explaining key design patterns

- [x] **Add developer guide section on task creation**
  - [x] Document best practices for task creation (docs/task_creation_guide.md)
  - [x] Provide examples of different task types
  - [x] Include troubleshooting information for common issues
  - [x] Create detailed guide on DirectHandlerTask pattern (docs/directhandler_pattern.md)

### 6. Workflow Engine Improvements

- [x] **Refactor WorkflowEngine to support pluggable task execution**
  - Modify execute_task method to use strategy pattern
  - Support custom task types with their own execution logic
  - [x] Improve condition evaluation with proper variable scoping
    - Updated Workflow.get_task to safely return None instead of raising exceptions
    - Enhanced DirectHandlerTask to support both old and new handler function signatures
    - Fixed variable resolution by improving Task.to_dict() method

- [x] **Add native support for direct handler execution**
  - Remove the need for monkey patching by supporting direct handlers natively
  - Create a registry for tool handler functions
  - Support both registry-based and direct handler execution

### 7. Framework Configuration

- [x] **Implement unified configuration system**
  - Create a configuration module for framework-wide settings
  - Support environment-based configuration overrides
  - Add validation for configuration values

- [x] **Add debug mode for development**
  - Implement debug flags for verbose logging
  - Add developer tools for inspecting workflow state
  - Create debugging utilities for common issues

## Implementation Priority

### High Priority (April 15-30)
1. Implement proper DirectHandlerTask as core feature
2. Standardize error reporting
3. Fix variable interpolation in task inputs

### Medium Priority (May 1-15)
1. Add native support for direct handler execution 
2. ~~Implement unified configuration system~~ (Completed)
3. Update all examples to use new patterns

### Lower Priority (May 16-31)
1. Create mock registry for testing
2. Add plugin system for tool execution
3. Implement standardized registry access

### Completed Initial Tasks (as of April 30)
1. Implement proper DirectHandlerTask as core feature ✅
2. Fix variable interpolation in task inputs ✅ 
3. Add proper error propagation between tasks ✅
4. Standardize exit code usage across framework code ✅
5. Add wrapper for main functions to ensure consistent exit code behavior ✅
6. Create exit code documentation for framework users ✅
7. Implement a testing-specific registry that doesn't require real services ✅
8. Add testing utilities for workflows and tasks ✅
9. Create comprehensive integration test suites for workflow features ✅
10. Develop comprehensive developer guides for task creation ✅
11. Create detailed documentation for DirectHandlerTask pattern ✅
12. Implement unified configuration system with validation ✅
13. Add debug mode for development environments ✅

## DirectHandlerTask Implementation Proposal

Based on our experience with the smart compliance workflow fix, here is a detailed proposal for implementing `DirectHandlerTask` as a core feature:

### 1. Core Class Definition in `core/task.py`

```python
from typing import Any, Callable, Dict, Optional

class DirectHandlerTask(Task):
    """
    A Task subclass that directly executes a handler function without using the tool registry.
    
    This provides a way to integrate custom task handling directly into workflows without
    needing to register tools in the global registry.
    """
    
    def __init__(
        self,
        task_id: str,
        name: str,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
        input_data: Optional[Dict[str, Any]] = None,
        condition: Optional[str] = None,
        next_task_id_on_success: Optional[str] = None,
        next_task_id_on_failure: Optional[str] = None,
        max_retries: int = 0,
    ):
        """
        Initialize a new DirectHandlerTask.
        
        Args:
            task_id: Unique identifier for the task
            name: Human-readable name for the task
            handler: Function that will be called with the task's input_data
            input_data: Initial input data for the task
            condition: Optional condition for task execution
            next_task_id_on_success: ID of the next task to execute on success
            next_task_id_on_failure: ID of the next task to execute on failure
            max_retries: Maximum number of times to retry the task if it fails
        """
        # Initialize with Task constructor, using special tool_name format
        super().__init__(
            task_id=task_id,
            name=name,
            tool_name="__direct_handler__",  # Special placeholder value
            is_llm_task=False,
            input_data=input_data,
            condition=condition,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            max_retries=max_retries,
        )
        
        # Store the handler function
        self.handler = handler
        # Add a flag to identify this as a direct handler task
        self.is_direct_handler = True
```

### 2. WorkflowEngine Integration in `core/engine.py`

```python
def execute_task(self, task: Task) -> bool:
    """Execute a task and return whether it was successful."""
    log_task_start(task.id, task.name, self.workflow.id)
    task.set_status("running")
    
    # Check if this is a DirectHandlerTask
    if hasattr(task, 'is_direct_handler') and task.is_direct_handler:
        # Execute DirectHandlerTask directly
        try:
            # Process inputs (resolve variables, etc.)
            processed_input = self.process_task_input(task)
            log_task_input(task.id, processed_input)
            
            # Execute the handler function
            result = task.handler(processed_input)
            
            # Process the result
            if result.get("success", False) or result.get("status", "") == "success":
                task.set_status("completed")
                task.set_output({"response": result.get("response", result.get("result", {}))})
                log_task_end(task.id, task.name, "completed", self.workflow.id)
                return True
            else:
                return self.handle_task_failure(task, result)
        except Exception as e:
            error_result = {"success": False, "error": f"Error executing direct handler: {str(e)}"}
            return self.handle_task_failure(task, error_result)
    elif task.is_llm_task:
        # Existing LLM task execution
        result = self.execute_llm_task(task)
        if result.get("success", False):
            task.set_status("completed")
            task.set_output({"response": result.get("response", {})})
            log_task_end(task.id, task.name, "completed", self.workflow.id)
            return True
        else:
            return self.handle_task_failure(task, result)
    else:
        # Existing tool task execution
        result = self.execute_tool_task(task)
        if result.get("success", False):
            task.set_status("completed")
            task.set_output({"response": result.get("response", result.get("result", {}))})
            log_task_end(task.id, task.name, "completed", self.workflow.id)
            return True
        else:
            return self.handle_task_failure(task, result)
```

### 3. Factory Method for Task Creation

Add a factory method to simplify task creation:

```python
# In core/workflow.py or a new utility module

def create_direct_handler_task(
    task_id: str,
    name: str,
    handler: Callable,
    input_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> DirectHandlerTask:
    """
    Factory function to create a DirectHandlerTask with the given parameters.
    
    Args:
        task_id: Unique identifier for the task
        name: Human-readable name for the task
        handler: Function to execute when the task runs
        input_data: Initial input data for the task
        **kwargs: Additional arguments to pass to DirectHandlerTask constructor
        
    Returns:
        A new DirectHandlerTask instance
    """
    return DirectHandlerTask(
        task_id=task_id,
        name=name,
        handler=handler,
        input_data=input_data,
        **kwargs
    )
```

### 4. Usage Example

```python
# Example usage in a workflow creation function

def build_workflow():
    workflow = Workflow("example_workflow", "Example Workflow")
    
    # Create a standard task
    task1 = Task(
        task_id="task1",
        name="Standard Task",
        is_llm_task=True,
        input_data={"prompt": "Example prompt"}
    )
    
    # Create a direct handler task
    def custom_handler(input_data):
        # Custom processing
        return {
            "status": "success", 
            "success": True,
            "result": {"processed": True, "data": input_data.get("value", None)}
        }
    
    task2 = create_direct_handler_task(
        task_id="task2",
        name="Custom Processing Task",
        handler=custom_handler,
        input_data={"value": "example"},
        next_task_id_on_success="task3"
    )
    
    # Add tasks to workflow
    workflow.add_task(task1)
    workflow.add_task(task2)
    
    return workflow
```

### 5. Unit Tests

Add comprehensive unit tests for the DirectHandlerTask class:

```python
# In tests/test_direct_handler_task.py

import unittest
from unittest.mock import MagicMock, patch

from core.task import DirectHandlerTask

class TestDirectHandlerTask(unittest.TestCase):
    def test_initialization(self):
        """Test that DirectHandlerTask initializes correctly."""
        handler = MagicMock(return_value={"success": True})
        task = DirectHandlerTask(
            task_id="test_task",
            name="Test Task",
            handler=handler,
            input_data={"key": "value"}
        )
        
        self.assertEqual(task.id, "test_task")
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.input_data, {"key": "value"})
        self.assertTrue(task.is_direct_handler)
        self.assertEqual(task.tool_name, "__direct_handler__")
        
    def test_execute_success(self):
        """Test successful execution of a DirectHandlerTask."""
        handler = MagicMock(return_value={"success": True, "result": {"data": "output"}})
        task = DirectHandlerTask(
            task_id="test_task",
            name="Test Task",
            handler=handler
        )
        
        # Execute the task
        result = task.execute()
        
        # Check that the handler was called
        handler.assert_called_once_with({})
        
        # Check the result
        self.assertTrue(result)
        self.assertEqual(task.status, "completed")
        
    def test_execute_failure(self):
        """Test failed execution of a DirectHandlerTask."""
        handler = MagicMock(return_value={"success": False, "error": "Test error"})
        task = DirectHandlerTask(
            task_id="test_task",
            name="Test Task",
            handler=handler
        )
        
        # Execute the task
        result = task.execute()
        
        # Check the result
        self.assertFalse(result)
        self.assertEqual(task.status, "failed")
```

## Standardized Error Reporting Proposal

Based on our experience with the smart compliance workflow and other examples, here is a proposal for standardizing error reporting across the framework:

### 1. Standardized Response Format

All tools, tasks, and workflows should return responses in a consistent format:

```python
{
    # Required fields for all responses
    "status": str,         # "success", "error", or "warning"
    "success": bool,       # True for successful operations, False otherwise
    
    # For successful responses (mutually exclusive with "error")
    "result": Any,         # The actual result data (for backward compatibility)
    "response": Any,       # Alternative name for result data (for consistent access)
    
    # For error responses (mutually exclusive with "result"/"response")
    "error": str,          # Human-readable error message
    "error_code": str,     # Optional machine-readable error code (e.g., "INVALID_INPUT")
    "error_details": dict, # Optional detailed error information
    
    # Optional metadata fields
    "metadata": {
        "execution_time": float,  # Time taken to execute the operation (in seconds)
        "timestamp": str,         # ISO format timestamp of when the operation completed
        "version": str,           # Version of the component that produced the response
    }
}
```

### 2. Error Code System

Implement a standardized error code system:

```python
# In core/errors.py

class ErrorCode:
    """Standardized error codes for the Dawn framework."""
    
    # Input validation errors (100-199)
    INVALID_INPUT = "INVALID_INPUT_100"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD_101"
    INVALID_TYPE = "INVALID_TYPE_102"
    INVALID_FORMAT = "INVALID_FORMAT_103"
    
    # Resource errors (200-299)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND_200"
    RESOURCE_ACCESS_DENIED = "RESOURCE_ACCESS_DENIED_201"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS_202"
    
    # Service errors (300-399)
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE_300"
    SERVICE_TIMEOUT = "SERVICE_TIMEOUT_301"
    SERVICE_ERROR = "SERVICE_ERROR_302"
    
    # Tool errors (400-499)
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND_400"
    TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED_401"
    
    # Task errors (500-599)
    TASK_NOT_FOUND = "TASK_NOT_FOUND_500"
    TASK_EXECUTION_FAILED = "TASK_EXECUTION_FAILED_501"
    
    # Workflow errors (600-699)
    WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND_600"
    WORKFLOW_EXECUTION_FAILED = "WORKFLOW_EXECUTION_FAILED_601"
```

### 3. Error Handling Utilities

Add utility functions for consistent error handling:

```python
# In core/errors.py

def create_error_response(error_message, error_code=None, error_details=None):
    """
    Create a standardized error response.
    
    Args:
        error_message: Human-readable error message
        error_code: Optional error code from ErrorCode class
        error_details: Optional dictionary with detailed error information
        
    Returns:
        Dictionary with standardized error response format
    """
    response = {
        "status": "error",
        "success": False,
        "error": error_message
    }
    
    if error_code:
        response["error_code"] = error_code
        
    if error_details:
        response["error_details"] = error_details
        
    return response

def create_success_response(result):
    """
    Create a standardized success response.
    
    Args:
        result: The result data to include in the response
        
    Returns:
        Dictionary with standardized success response format
    """
    return {
        "status": "success",
        "success": True,
        "result": result,
        "response": result
    }
```

### 4. Tool Registry Error Standardization

Update the tool registry to enforce standardized error responses:

```python
# In core/tools/registry.py

def execute_tool(self, tool_name, input_data):
    """
    Execute a tool by name with the given input data.
    
    Args:
        tool_name: Name of the tool to execute
        input_data: Input data for the tool
        
    Returns:
        Standardized response dictionary
    """
    try:
        if tool_name not in self.tools:
            return create_error_response(
                f"Tool '{tool_name}' not found in registry",
                ErrorCode.TOOL_NOT_FOUND
            )
            
        tool_handler = self.tools[tool_name]
        result = tool_handler(input_data)
        
        # Ensure result is in the standardized format
        if isinstance(result, dict):
            # Check if it already has the required fields
            if "status" not in result:
                if result.get("success", False):
                    result["status"] = "success"
                else:
                    result["status"] = "error"
                    
            # Ensure both result and response fields for successful responses
            if result.get("success", False):
                if "result" in result and "response" not in result:
                    result["response"] = result["result"]
                elif "response" in result and "result" not in result:
                    result["result"] = result["response"]
                    
            return result
        else:
            # Non-dict results are wrapped in a standardized format
            return create_success_response(result)
            
    except Exception as e:
        return create_error_response(
            f"Error executing tool '{tool_name}': {str(e)}",
            ErrorCode.TOOL_EXECUTION_FAILED,
            {"exception_type": type(e).__name__}
        )
```

### 5. Integration with Workflow Engine

Ensure the workflow engine properly handles standardized errors:

```python
# In core/engine.py

def handle_task_failure(self, task, result):
    """
    Handle a task failure with standardized error reporting.
    
    Args:
        task: The task that failed
        result: The result from the task execution
        
    Returns:
        Boolean indicating whether the task should be considered successful
    """
    # Extract error information from the result
    error_message = result.get("error", "Unknown error")
    error_code = result.get("error_code", "UNKNOWN_ERROR")
    error_details = result.get("error_details", {})
    
    # Log detailed error information
    log_error(
        f"Task {task.id} failed: {error_message} (Code: {error_code})",
        details=error_details
    )
    
    # Check for retry
    if task.can_retry():
        task.increment_retry()
        log_task_retry(task.id, task.name, task.retry_count, task.max_retries)
        task.set_status("pending")
        return self.execute_task(task)
    else:
        # Set standardized output with error information
        task.set_status("failed")
        task.set_output({
            "error": error_message,
            "error_code": error_code,
            "error_details": error_details
        })
        log_task_end(task.id, task.name, "failed", self.workflow.id)
        return False
```

### 6. Example Usage

Example of using the standardized error reporting in a tool:

```python
def my_tool_handler(input_data):
    try:
        # Validate inputs
        if "required_field" not in input_data:
            return create_error_response(
                "Missing required field 'required_field'",
                ErrorCode.MISSING_REQUIRED_FIELD,
                {"field_name": "required_field"}
            )
            
        # Process input
        result = process_data(input_data["required_field"])
        
        # Return standardized success response
        return create_success_response(result)
        
    except ValueError as e:
        return create_error_response(
            f"Invalid input value: {str(e)}",
            ErrorCode.INVALID_INPUT
        )
    except Exception as e:
        return create_error_response(
            f"Unexpected error: {str(e)}",
            ErrorCode.SERVICE_ERROR
        )
```

## Exit Code Standardization Implementation

We've implemented a standardized approach to exit codes across the framework:

### 1. Exit Code Conventions

The following exit code conventions have been established:

```
0: Success - Workflow completed without critical errors
1: General error - Workflow failed due to a general error condition
2: Configuration error - Required configuration is missing or invalid
3: Resource error - Required resources are unavailable or inaccessible
4: Execution error - Error during execution of specific workflow tasks
5: Input error - Invalid input data provided to the workflow
```

### 2. Implementation Details

The standardized exit codes have been implemented in these key areas:

- All workflow scripts use `sys.exit(0)` for successful execution
- Error conditions are properly differentiated with specific exit codes
- Framework initialization failures (missing API keys, etc.) use code 2
- Resource failures (vector store creation, etc.) use code 3
- Task execution failures use code 4
- Input validation failures use code 5

### 3. Examples

From smart_compliance_workflow.py:
```python
# Configuration error
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY environment variable is required for LLM tasks.")
    sys.exit(2)  # Exit with configuration error code

# Resource error
if missing_tools:
    logger.error(f"Missing required Vector Store tools in registry: {missing_tools}")
    sys.exit(3)  # Exit with resource error code
    
# Resource error
if not compliance_vs_id:
    logger.error("Failed to ensure compliance vector store is ready. Exiting.")
    sys.exit(3)  # Exit with resource error code

# Success case
if result_status and failed_tasks == 0:
    logger.info("\nWorkflow marked as successful overall.")
    sys.exit(0)  # Explicit successful exit
else:
    logger.warning("\nWorkflow marked as failed or incomplete overall.")
    sys.exit(4)  # Exit with execution error code
```

This standardization ensures consistent behavior across the framework and makes automated error handling more reliable.

## Implementation Timeline and Release Plan

### Phase 1: Core Stability (April 15-30)
1. Implement `DirectHandlerTask` class in core framework (**April 18**)
2. Add standardized error reporting system (**April 22**)
3. Fix variable interpolation in task inputs (**April 25**)
4. Run all tests and fix critical issues (**April 29**)
5. **Release v0.1.0** - First stable development version (**April 30**)

### Phase 2: Framework Robustness (May 1-15)
1. Add native support for direct handler execution in WorkflowEngine (**May 5**)
2. Implement unified configuration system (**May 8**)
3. Update all examples to use new patterns (**May 12**)
4. End-to-end integration testing (**May 14**)
5. **Release v0.2.0** - Improved stability version (**May 15**)

### Phase 3: Developer Experience (May 16-31)
1. Create mock registry for testing (**May 20**)
2. Add plugin system for tool execution (**May 24**)
3. Implement standardized registry access (**May 27**)
4. Complete documentation updates (**May 30**)
5. **Release v0.3.0** - Developer-friendly version (**May 31**)

### Phase 4: Full Production Release (June 2025)
1. Performance optimizations (**June 5**)
2. Security review and enhancements (**June 10**)
3. Compatibility testing across environments (**June 15**)
4. Final documentation and examples (**June 20**)
5. **Release v1.0.0** - First production-ready version (**June 30**)

## Package Structure for v1.0.0

```
dawn/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── agent.py
│   ├── engine.py
│   ├── errors.py         # New: Standardized error system
│   ├── task.py           # Updated: With DirectHandlerTask
│   ├── workflow.py
│   └── config.py         # New: Configuration system
├── tools/
│   ├── __init__.py
│   ├── registry.py       # Updated: With improved handler support
│   ├── base.py           # New: Base classes for tools
│   └── standard/         # Standard tool implementations
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── testing.py        # New: Testing utilities
├── testing/
│   ├── __init__.py
│   ├── mocks.py          # New: Mock implementations for testing
│   └── fixtures.py       # New: Pytest fixtures
└── examples/
    ├── basic_workflow.py
    ├── smart_compliance_workflow.py
    └── developer_guide.py
```

## Deployment Checklist

Before each release, ensure the following steps are completed:

1. All tests pass
2. Documentation is updated
3. Examples are working
4. Version numbers are updated
5. CHANGELOG.md is updated
6. PyPI package is built and tested
7. GitHub release is created
8. Release announcement is prepared

This structured approach will ensure we can maintain a steady pace of improvements while delivering reliable releases to users. 