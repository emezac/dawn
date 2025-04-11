"""
Tests for the core error handling system.
"""

import json
import unittest
from unittest.mock import patch

from core.errors import (
    DawnError,
    ErrorCode,
    InputValidationError,
    ResourceError,
    ServiceError,
    TaskError,
    ToolError,
    WorkflowError,
    create_error_response,
    create_success_response,
    is_error_response,
    is_success_response,
    safe_execute,
)


class TestErrorCode(unittest.TestCase):
    """Test cases for ErrorCode enum."""

    def test_error_code_values(self):
        """Test that error codes have unique values."""
        codes = [e.value for e in ErrorCode]
        self.assertEqual(len(codes), len(set(codes)), "Error codes must have unique values")

    def test_error_code_categories(self):
        """Test that error codes follow the specified ranges."""
        for error in ErrorCode:
            code = error.value

            if 1000 <= code < 2000:
                self.assertTrue(
                    error.name.startswith("INVALID") or "FIELD" in error.name,
                    f"Error code {error.name} doesn't follow input validation naming pattern",
                )
            elif 2000 <= code < 3000:
                self.assertTrue(
                    "RESOURCE" in error.name, f"Error code {error.name} doesn't follow resource naming pattern"
                )
            elif 3000 <= code < 4000:
                self.assertTrue(
                    "SERVICE" in error.name or "LIMIT" in error.name,
                    f"Error code {error.name} doesn't follow service naming pattern",
                )
            # ... and so on for other categories


class TestDawnError(unittest.TestCase):
    """Test cases for DawnError class."""

    def test_init(self):
        """Test error initialization with various parameters."""
        # Basic initialization
        error = DawnError("An error occurred")
        self.assertEqual(error.message, "An error occurred")
        self.assertEqual(error.error_code, ErrorCode.UNEXPECTED_ERROR)
        self.assertEqual(error.details, {})

        # With details and code
        details = {"param": "value"}
        error = DawnError("Invalid input", details, ErrorCode.INVALID_INPUT)
        self.assertEqual(error.message, "Invalid input")
        self.assertEqual(error.error_code, ErrorCode.INVALID_INPUT)
        self.assertEqual(error.details, details)

    def test_to_response(self):
        """Test conversion to response format."""
        error = DawnError("An error occurred", {"context": "test"}, ErrorCode.VALUE_ERROR)
        response = error.to_response()

        self.assertTrue(is_error_response(response))
        self.assertEqual(response["error"]["code"], ErrorCode.VALUE_ERROR.value)
        self.assertEqual(response["error"]["type"], "VALUE_ERROR")
        self.assertEqual(response["error"]["message"], "An error occurred")
        self.assertEqual(response["error"]["details"], {"context": "test"})


class TestErrorSubclasses(unittest.TestCase):
    """Test cases for error subclasses."""

    def test_input_validation_error(self):
        """Test InputValidationError initialization and defaults."""
        error = InputValidationError("Invalid input")
        self.assertEqual(error.error_code, ErrorCode.INVALID_INPUT)

        # Override error code
        error = InputValidationError("Missing field", error_code=ErrorCode.MISSING_REQUIRED_FIELD)
        self.assertEqual(error.error_code, ErrorCode.MISSING_REQUIRED_FIELD)

    def test_resource_error(self):
        """Test ResourceError initialization and defaults."""
        error = ResourceError("Resource not found")
        self.assertEqual(error.error_code, ErrorCode.RESOURCE_NOT_FOUND)

    def test_service_error(self):
        """Test ServiceError initialization and defaults."""
        error = ServiceError("Service unavailable")
        self.assertEqual(error.error_code, ErrorCode.SERVICE_ERROR)

    def test_tool_error(self):
        """Test ToolError initialization and defaults."""
        error = ToolError("Tool execution failed")
        self.assertEqual(error.error_code, ErrorCode.TOOL_EXECUTION_ERROR)

    def test_task_error(self):
        """Test TaskError initialization and defaults."""
        error = TaskError("Task execution failed")
        self.assertEqual(error.error_code, ErrorCode.TASK_EXECUTION_ERROR)

    def test_workflow_error(self):
        """Test WorkflowError initialization and defaults."""
        error = WorkflowError("Workflow execution failed")
        self.assertEqual(error.error_code, ErrorCode.WORKFLOW_EXECUTION_ERROR)


class TestResponseFunctions(unittest.TestCase):
    """Test cases for response creation functions."""

    def test_create_error_response(self):
        """Test creating error responses."""
        # Basic error
        response = create_error_response(ErrorCode.INVALID_INPUT, "Invalid input")
        self.assertEqual(response["error"]["code"], ErrorCode.INVALID_INPUT.value)
        self.assertEqual(response["error"]["type"], "INVALID_INPUT")
        self.assertEqual(response["error"]["message"], "Invalid input")
        self.assertNotIn("details", response["error"])
        self.assertNotIn("trace", response["error"])

        # With details and trace
        response = create_error_response(
            ErrorCode.SERVICE_ERROR, "Service unavailable", details={"service": "api"}, trace="Error\n  at line 1"
        )
        self.assertEqual(response["error"]["details"], {"service": "api"})
        self.assertEqual(response["error"]["trace"], "Error\n  at line 1")

    def test_create_success_response(self):
        """Test creating success responses."""
        # Basic success
        data = {"result": "value"}
        response = create_success_response(data)
        self.assertEqual(response["data"], data)
        self.assertNotIn("message", response)
        self.assertNotIn("metadata", response)

        # With message and metadata
        response = create_success_response(data, message="Operation successful", metadata={"timestamp": "2023-01-01"})
        self.assertEqual(response["data"], data)
        self.assertEqual(response["message"], "Operation successful")
        self.assertEqual(response["metadata"], {"timestamp": "2023-01-01"})

    def test_is_error_response(self):
        """Test error response detection."""
        self.assertTrue(is_error_response({"error": {"message": "Error"}}))
        self.assertFalse(is_error_response({"data": "value"}))
        self.assertFalse(is_error_response({}))

    def test_is_success_response(self):
        """Test success response detection."""
        self.assertTrue(is_success_response({"data": "value"}))
        self.assertFalse(is_success_response({"error": {"message": "Error"}}))
        self.assertFalse(is_success_response({}))


class TestSafeExecute(unittest.TestCase):
    """Test cases for safe_execute function."""

    def test_successful_execution(self):
        """Test successful function execution."""

        def example_func(a, b):
            return a + b

        result = safe_execute(example_func, 1, 2)
        self.assertEqual(result, 3)

    def test_dawn_error_handling(self):
        """Test handling of DawnError."""

        def example_func():
            raise InputValidationError("Invalid input", {"field": "name"})

        result = safe_execute(example_func)
        self.assertTrue(is_error_response(result))
        self.assertEqual(result["error"]["code"], ErrorCode.INVALID_INPUT.value)
        self.assertEqual(result["error"]["details"], {"field": "name"})

    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors."""

        def example_func():
            raise ValueError("Something went wrong")

        result = safe_execute(example_func)
        self.assertTrue(is_error_response(result))
        self.assertEqual(result["error"]["code"], ErrorCode.UNEXPECTED_ERROR.value)
        self.assertEqual(result["error"]["details"]["exception_type"], "ValueError")


if __name__ == "__main__":
    unittest.main()
