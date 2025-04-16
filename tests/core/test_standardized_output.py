#!/usr/bin/env python3
"""
Test cases for standardized task output format in the Dawn framework.

These tests verify that task outputs conform to the standardized output schema
and that tools for creating standardized outputs work as expected.
"""  # noqa: D202

import os
import sys
import unittest
from typing import Any, Dict, List, Optional

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.task import Task, DirectHandlerTask, TaskOutput, validate_output_format
from core.errors import ErrorCode, create_error_response, create_success_response, create_warning_response


class TestStandardizedOutput(unittest.TestCase):
    """Test cases for standardized task output format."""  # noqa: D202

    def test_validate_output_format_success(self):
        """Test that valid success output data is properly formatted."""
        # Simple success output with just a result
        input_data = {"result": "test result"}
        output = validate_output_format(input_data)
        
        # Check required fields
        self.assertTrue(output["success"])
        self.assertEqual(output["status"], "completed")
        self.assertEqual(output["result"], "test result")
        self.assertEqual(output["response"], "test result")
        self.assertIn("metadata", output)
        
        # More complex output with existing fields
        input_data = {
            "success": True,
            "result": {"value": 42, "items": ["a", "b"]},
            "metadata": {"duration_ms": 150}
        }
        output = validate_output_format(input_data)
        
        self.assertTrue(output["success"])
        self.assertEqual(output["status"], "completed")
        self.assertEqual(output["result"]["value"], 42)
        self.assertEqual(output["response"]["value"], 42)
        self.assertEqual(output["metadata"]["duration_ms"], 150)
    
    def test_validate_output_format_error(self):
        """Test that error output data is properly formatted."""
        # Simple error output with just an error message
        input_data = {"error": "Something went wrong"}
        output = validate_output_format(input_data)
        
        self.assertFalse(output["success"])
        self.assertEqual(output["status"], "failed")
        self.assertEqual(output["error"], "Something went wrong")
        self.assertIn("metadata", output)
        
        # More complex error output with details
        input_data = {
            "success": False,
            "error": "Execution failed",
            "error_type": "ValueError",
            "error_details": {"line": 42, "function": "process_data"}
        }
        output = validate_output_format(input_data)
        
        self.assertFalse(output["success"])
        self.assertEqual(output["status"], "failed")
        self.assertEqual(output["error"], "Execution failed")
        self.assertEqual(output["error_type"], "ValueError")
        self.assertEqual(output["error_details"]["line"], 42)
    
    def test_validate_output_format_warning(self):
        """Test that warning output data is properly formatted."""
        # Warning output
        input_data = {
            "success": True,
            "status": "warning",
            "result": "partial result",
            "warning": "Some data might be incomplete"
        }
        output = validate_output_format(input_data)
        
        self.assertTrue(output["success"])
        self.assertEqual(output["status"], "warning")
        self.assertEqual(output["result"], "partial result")
        self.assertEqual(output["response"], "partial result")
        self.assertEqual(output["warning"], "Some data might be incomplete")
    
    def test_validate_output_format_non_standard_fields(self):
        """Test that non-standard fields are moved to metadata."""
        input_data = {
            "success": True,
            "result": "test result",
            "custom_field1": "value1",
            "custom_field2": {"nested": "value2"}
        }
        output = validate_output_format(input_data)
        
        self.assertTrue(output["success"])
        self.assertEqual(output["result"], "test result")
        self.assertEqual(output["metadata"]["custom_field1"], "value1")
        self.assertEqual(output["metadata"]["custom_field2"]["nested"], "value2")
    
    def test_validate_output_format_non_dict_input(self):
        """Test standardizing non-dictionary inputs."""
        # String input
        input_data = "test string"
        output = validate_output_format({"success": True, "result": input_data})
        
        self.assertTrue(output["success"])
        self.assertEqual(output["result"], "test string")
        self.assertEqual(output["response"], "test string")
        
        # Number input
        input_data = 42
        output = validate_output_format({"success": True, "result": input_data})
        
        self.assertTrue(output["success"])
        self.assertEqual(output["result"], 42)
        self.assertEqual(output["response"], 42)
        
        # List input
        input_data = ["a", "b", "c"]
        output = validate_output_format({"success": True, "result": input_data})
        
        self.assertTrue(output["success"])
        self.assertEqual(output["result"], ["a", "b", "c"])
        self.assertEqual(output["response"], ["a", "b", "c"])
    
    def test_task_set_output(self):
        """Test that Task.set_output correctly standardizes output."""
        task = Task(task_id="test_task", name="Test Task")
        
        # Set success output
        task.set_output({"result": "test result"})
        self.assertTrue(task.output_data["success"])
        self.assertEqual(task.output_data["status"], "completed")
        self.assertEqual(task.output_data["result"], "test result")
        self.assertEqual(task.output_data["response"], "test result")
        self.assertEqual(task.status, "completed")
        
        # Set error output
        task.set_output({"error": "Something went wrong"})
        self.assertFalse(task.output_data["success"])
        self.assertEqual(task.output_data["status"], "failed")
        self.assertEqual(task.output_data["error"], "Something went wrong")
        self.assertEqual(task.status, "failed")
        self.assertEqual(task.error, "Something went wrong")
    
    def test_create_error_response(self):
        """Test the create_error_response function."""
        error_response = create_error_response(
            message="Failed to process data",
            error_code=ErrorCode.DATA_VALIDATION_ERROR,
            source_task_id="task1",
            additional_info="Extra details"
        )
        
        self.assertFalse(error_response["success"])
        self.assertEqual(error_response["status"], "failed")
        self.assertEqual(error_response["error"], "Failed to process data")
        self.assertEqual(error_response["error_code"], ErrorCode.DATA_VALIDATION_ERROR)
        self.assertEqual(error_response["error_details"]["source_task_id"], "task1")
        self.assertEqual(error_response["error_details"]["additional_info"], "Extra details")
    
    def test_create_success_response(self):
        """Test the create_success_response function."""
        success_response = create_success_response(
            result={"key": "value"},
            metadata={"duration_ms": 150}
        )
        
        self.assertTrue(success_response["success"])
        self.assertEqual(success_response["status"], "completed")
        self.assertEqual(success_response["result"]["key"], "value")
        self.assertEqual(success_response["response"]["key"], "value")
        self.assertEqual(success_response["metadata"]["duration_ms"], 150)
    
    def test_create_warning_response(self):
        """Test the create_warning_response function."""
        warning_response = create_warning_response(
            result="partial result",
            warning="Some data might be incomplete",
            warning_code="PARTIAL_DATA",
            metadata={"processed_count": 42}
        )
        
        self.assertTrue(warning_response["success"])
        self.assertEqual(warning_response["status"], "warning")
        self.assertEqual(warning_response["result"], "partial result")
        self.assertEqual(warning_response["response"], "partial result")
        self.assertEqual(warning_response["warning"], "Some data might be incomplete")
        self.assertEqual(warning_response["warning_code"], "PARTIAL_DATA")
        self.assertEqual(warning_response["metadata"]["processed_count"], 42)
    
    def test_direct_handler_standardized_output(self):
        """Test that DirectHandlerTask output is properly standardized."""
        # Define handler functions with different output formats
        def success_handler(task, input_data):
            """Return a simple result."""
            return {"result": "success result"}
        
        def error_handler(task, input_data):
            """Return an error."""
            return {"error": "Something went wrong"}
        
        def non_dict_handler(task, input_data):
            """Return a non-dictionary value."""
            return "raw string result"
        
        # Test success handler
        task = DirectHandlerTask(task_id="success_task", name="Success Task", handler=success_handler)
        output = task.execute()
        
        self.assertTrue(output["success"])
        self.assertEqual(output["status"], "completed")
        self.assertEqual(output["result"], "success result")
        self.assertEqual(output["response"], "success result")
        
        # Test error handler
        task = DirectHandlerTask(task_id="error_task", name="Error Task", handler=error_handler)
        output = task.execute()
        
        self.assertFalse(output["success"])
        self.assertEqual(output["status"], "failed")
        self.assertEqual(output["error"], "Something went wrong")
        
        # Test non-dict handler
        task = DirectHandlerTask(task_id="non_dict_task", name="Non-Dict Task", handler=non_dict_handler)
        output = task.execute()
        
        self.assertTrue(output["success"])
        self.assertEqual(output["status"], "completed")
        self.assertEqual(output["result"], "raw string result")
        self.assertEqual(output["response"], "raw string result")


if __name__ == "__main__":
    unittest.main() 