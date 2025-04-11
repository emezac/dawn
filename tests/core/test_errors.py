"""Tests for the Dawn framework error handling system."""

import unittest

from dawn.core.errors import (
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
)


class TestErrorCode(unittest.TestCase):
    """Test the ErrorCode enum."""

    def test_error_code_values(self):
        """Test that error codes have unique values."""
        codes = [code.value for code in ErrorCode]
        self.assertEqual(len(codes), len(set(codes)), "Error codes should have unique values")

    def test_error_code_categories(self):
        """Test that error codes are organized by category."""
        input_validation_codes = [
            ErrorCode.INVALID_INPUT,
            ErrorCode.MISSING_REQUIRED_FIELD,
            ErrorCode.TYPE_ERROR,
            ErrorCode.VALUE_ERROR,
        ]
        for code in input_validation_codes:
            self.assertTrue(1000 <= code.value < 2000, f"Input validation code {code} should be in 1000-1999 range")

        resource_codes = [
            ErrorCode.RESOURCE_NOT_FOUND,
            ErrorCode.RESOURCE_ALREADY_EXISTS,
            ErrorCode.RESOURCE_UNAVAILABLE,
            ErrorCode.PERMISSION_DENIED,
        ]
        for code in resource_codes:
            self.assertTrue(2000 <= code.value < 3000, f"Resource code {code} should be in 2000-2999 range")


class TestErrorResponse(unittest.TestCase):
    """Test the error response creation functions."""

    def test_create_error_response(self):
        """Test creating an error response."""
        response = create_error_response(ErrorCode.INVALID_INPUT, "Invalid input", {"field": "name"}, "Traceback...")

        # Check basic structure
        self.assertEqual(response["status"], "error")
        self.assertFalse(response["success"])

        # Check error details
        self.assertEqual(response["error"]["code"], ErrorCode.INVALID_INPUT.value)
        self.assertEqual(response["error"]["type"], "INVALID_INPUT")
        self.assertEqual(response["error"]["message"], "Invalid input")
        self.assertEqual(response["error"]["details"], {"field": "name"})
        self.assertEqual(response["error"]["trace"], "Traceback...")

    def test_create_error_response_minimal(self):
        """Test creating a minimal error response."""
        response = create_error_response(ErrorCode.SERVICE_ERROR, "Service unavailable")

        self.assertEqual(response["status"], "error")
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], ErrorCode.SERVICE_ERROR.value)
        self.assertEqual(response["error"]["message"], "Service unavailable")
        self.assertNotIn("details", response["error"])
        self.assertNotIn("trace", response["error"])

    def test_create_success_response(self):
        """Test creating a success response."""
        response = create_success_response(
            {"result": "value"}, "Operation completed successfully", {"duration_ms": 150}
        )

        self.assertEqual(response["status"], "success")
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], {"result": "value"})
        self.assertEqual(response["message"], "Operation completed successfully")
        self.assertEqual(response["metadata"], {"duration_ms": 150})

    def test_create_success_response_minimal(self):
        """Test creating a minimal success response."""
        response = create_success_response()

        self.assertEqual(response["status"], "success")
        self.assertTrue(response["success"])
        self.assertNotIn("data", response)
        self.assertNotIn("message", response)
        self.assertNotIn("metadata", response)

    def test_is_success_response(self):
        """Test checking if a response is a success response."""
        success_response = create_success_response()
        error_response = create_error_response(ErrorCode.INVALID_INPUT, "Invalid input")

        self.assertTrue(is_success_response(success_response))
        self.assertFalse(is_success_response(error_response))
        self.assertFalse(is_success_response({}))
        self.assertFalse(is_success_response({"success": False}))

    def test_is_error_response(self):
        """Test checking if a response is an error response."""
        success_response = create_success_response()
        error_response = create_error_response(ErrorCode.INVALID_INPUT, "Invalid input")

        self.assertTrue(is_error_response(error_response))
        self.assertFalse(is_error_response(success_response))
        self.assertFalse(is_error_response({}))
        self.assertTrue(is_error_response({"success": False}))


class TestDawnError(unittest.TestCase):
    """Test the DawnError base class."""

    def test_dawn_error_init(self):
        """Test initializing a DawnError."""
        error = DawnError("Something went wrong", ErrorCode.SERVICE_ERROR, {"service": "database"})

        self.assertEqual(str(error), "Something went wrong")
        self.assertEqual(error.message, "Something went wrong")
        self.assertEqual(error.error_code, ErrorCode.SERVICE_ERROR)
        self.assertEqual(error.details, {"service": "database"})

    def test_dawn_error_to_response(self):
        """Test converting a DawnError to a response."""
        error = DawnError("Something went wrong", ErrorCode.SERVICE_ERROR, {"service": "database"})
        response = error.to_response(include_trace=False)

        self.assertEqual(response["status"], "error")
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], ErrorCode.SERVICE_ERROR.value)
        self.assertEqual(response["error"]["type"], "SERVICE_ERROR")
        self.assertEqual(response["error"]["message"], "Something went wrong")
        self.assertEqual(response["error"]["details"], {"service": "database"})
        self.assertNotIn("trace", response["error"])


class TestErrorSubclasses(unittest.TestCase):
    """Test the error subclasses."""

    def test_input_validation_error(self):
        """Test the InputValidationError class."""
        error = InputValidationError("Invalid value", {"field": "age"})

        self.assertEqual(error.message, "Invalid value")
        self.assertEqual(error.error_code, ErrorCode.INVALID_INPUT)
        self.assertEqual(error.details, {"field": "age"})

        # Test with custom error code
        error = InputValidationError("Missing field", {"field": "name"}, ErrorCode.MISSING_REQUIRED_FIELD)
        self.assertEqual(error.error_code, ErrorCode.MISSING_REQUIRED_FIELD)

    def test_resource_error(self):
        """Test the ResourceError class."""
        error = ResourceError("Resource not found", {"id": "123"})

        self.assertEqual(error.message, "Resource not found")
        self.assertEqual(error.error_code, ErrorCode.RESOURCE_NOT_FOUND)
        self.assertEqual(error.details, {"id": "123"})

        # Test with custom error code
        error = ResourceError("Resource already exists", {"id": "123"}, ErrorCode.RESOURCE_ALREADY_EXISTS)
        self.assertEqual(error.error_code, ErrorCode.RESOURCE_ALREADY_EXISTS)

    def test_service_error(self):
        """Test the ServiceError class."""
        error = ServiceError("Service unavailable", {"service": "database"})

        self.assertEqual(error.message, "Service unavailable")
        self.assertEqual(error.error_code, ErrorCode.SERVICE_ERROR)
        self.assertEqual(error.details, {"service": "database"})

    def test_tool_error(self):
        """Test the ToolError class."""
        error = ToolError("Tool execution failed", {"tool": "calculator"})

        self.assertEqual(error.message, "Tool execution failed")
        self.assertEqual(error.error_code, ErrorCode.TOOL_EXECUTION_ERROR)
        self.assertEqual(error.details, {"tool": "calculator"})

    def test_task_error(self):
        """Test the TaskError class."""
        error = TaskError("Task execution failed", {"task": "data_processing"})

        self.assertEqual(error.message, "Task execution failed")
        self.assertEqual(error.error_code, ErrorCode.TASK_EXECUTION_ERROR)
        self.assertEqual(error.details, {"task": "data_processing"})

    def test_workflow_error(self):
        """Test the WorkflowError class."""
        error = WorkflowError("Workflow execution failed", {"workflow": "analysis"})

        self.assertEqual(error.message, "Workflow execution failed")
        self.assertEqual(error.error_code, ErrorCode.WORKFLOW_EXECUTION_ERROR)
        self.assertEqual(error.details, {"workflow": "analysis"})


if __name__ == "__main__":
    unittest.main()
