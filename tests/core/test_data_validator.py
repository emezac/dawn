"""
Tests for the data validation functionality in the Dawn framework.

This module contains tests for data validation functions,
including type checking, schema validation, and error handling.
"""

import os
import sys
import unittest
from typing import Any, Dict, List, Optional, Union

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.utils.data_validator import (
    ValidationError, 
    create_schema_from_type_hints, 
    validate_type, 
    validate_data,
    validate_task_input,
    validate_task_output,
    format_validation_errors
)


class TestDataValidator(unittest.TestCase):
    """Test cases for data validation functionality."""  # noqa: D202

    def test_validation_error(self):
        """Test the ValidationError class."""
        # Simple error
        error = ValidationError("Value is invalid")
        self.assertEqual(str(error), "Value is invalid")
        
        # Error with field path
        error = ValidationError("Must be integer", "config.timeout")
        self.assertEqual(str(error), "config.timeout: Must be integer")
        
        # Error with field path and details
        error = ValidationError(
            "Invalid type", 
            "data.items[0]", 
            {"expected": "int", "got": "str"}
        )
        self.assertEqual(str(error), "data.items[0]: Invalid type")
        self.assertEqual(error.details, {"expected": "int", "got": "str"})
    
    def test_create_schema_from_type_hints(self):
        """Test creating a schema from function type hints."""
        def sample_func(name: str, age: int, tags: Optional[List[str]] = None) -> Dict[str, Any]:
            return {"name": name, "age": age, "tags": tags or []}
        
        schema = create_schema_from_type_hints(sample_func)
        
        # Check schema structure
        self.assertEqual(len(schema), 3)
        
        # Check name parameter
        self.assertEqual(schema["name"]["type"], str)
        self.assertTrue(schema["name"]["required"])
        
        # Check age parameter
        self.assertEqual(schema["age"]["type"], int)
        self.assertTrue(schema["age"]["required"])
        
        # Check tags parameter with default
        self.assertEqual(schema["tags"]["type"], Optional[List[str]])
        self.assertFalse(schema["tags"]["required"])
        self.assertIsNone(schema["tags"]["default"])
    
    def test_validate_type_basic(self):
        """Test validation of basic types."""
        # Valid cases
        validate_type(42, int)
        validate_type("hello", str)
        validate_type(True, bool)
        validate_type([1, 2, 3], list)
        validate_type({"a": 1}, dict)
        
        # Invalid cases
        with self.assertRaises(ValidationError):
            validate_type("42", int)
        
        with self.assertRaises(ValidationError):
            validate_type(42, str)
    
    def test_validate_type_nested(self):
        """Test validation of nested types."""
        # List of strings
        validate_type(["a", "b", "c"], List[str])
        
        # Dict with string keys and int values
        validate_type({"a": 1, "b": 2}, Dict[str, int])
        
        # Invalid nested types
        with self.assertRaises(ValidationError):
            validate_type([1, "2", 3], List[int])
        
        with self.assertRaises(ValidationError):
            validate_type({"a": "1", "b": 2}, Dict[str, int])
    
    def test_validate_type_union(self):
        """Test validation of union types."""
        # Union type
        validate_type(42, Union[int, str])
        validate_type("hello", Union[int, str])
        validate_type(None, Union[int, str, None])  # None is a valid type in this union
        
        # Optional type (Union[Type, None])
        validate_type(None, Optional[str])
        validate_type("hello", Optional[str])
        
        # Invalid union type - using dict instead of int/str
        with self.assertRaises(ValidationError):
            validate_type({"key": "value"}, Union[int, str])
    
    def test_validate_type_any(self):
        """Test validation with Any type."""
        # Any type should accept anything
        validate_type(42, Any)
        validate_type("hello", Any)
        validate_type([1, 2, 3], Any)
        validate_type({"a": 1}, Any)
        validate_type(None, Any)
    
    def test_validate_data(self):
        """Test validating data against a schema."""
        # Define a schema
        schema = {
            "name": {"type": str, "required": True},
            "age": {"type": int, "required": True},
            "tags": {"type": List[str], "required": False}
        }
        
        # Valid data
        valid_data = {"name": "Alice", "age": 30, "tags": ["user", "admin"]}
        errors = validate_data(valid_data, schema)
        self.assertEqual(len(errors), 0)
        
        # Data with missing required field
        missing_field_data = {"name": "Bob"}
        errors = validate_data(missing_field_data, schema)
        self.assertEqual(len(errors), 1)
        
        # Data with wrong type
        wrong_type_data = {"name": "Charlie", "age": "32", "tags": ["user"]}
        errors = validate_data(wrong_type_data, schema)
        self.assertEqual(len(errors), 1)
        
        # Data with multiple issues
        invalid_data = {"name": 123, "tags": "not-a-list"}
        errors = validate_data(invalid_data, schema)
        self.assertEqual(len(errors), 3)  # Missing age field, wrong name type, wrong tags type
    
    def test_validate_task_input(self):
        """Test validating task input against handler's type hints."""
        def handler(message: str, count: int, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            return {"success": True, "result": message * count}
        
        # Valid input
        valid_input = {"message": "hello", "count": 3, "options": {"capitalize": True}}
        errors = validate_task_input(handler, valid_input)
        self.assertEqual(len(errors), 0)
        
        # Invalid input
        invalid_input = {"message": 123, "count": "3"}
        errors = validate_task_input(handler, invalid_input)
        self.assertEqual(len(errors), 2)
    
    def test_validate_task_output(self):
        """Test validating task output against standard format."""
        # Valid success output with result
        valid_success_output = {"success": True, "result": "Operation completed"}
        errors = validate_task_output(valid_success_output)
        self.assertEqual(len(errors), 0)
        
        # Valid success output with response
        valid_response_output = {"success": True, "response": "Task response"}
        errors = validate_task_output(valid_response_output)
        self.assertEqual(len(errors), 0)
        
        # Valid failure output
        valid_failure_output = {"success": False, "error": "Something went wrong"}
        errors = validate_task_output(valid_failure_output)
        self.assertEqual(len(errors), 0)
        
        # Invalid: failure without error
        invalid_failure_output = {"success": False}
        errors = validate_task_output(invalid_failure_output)
        self.assertEqual(len(errors), 1)
        
        # Invalid: success without result or response
        invalid_success_output = {"success": True}
        errors = validate_task_output(invalid_success_output)
        self.assertEqual(len(errors), 1)
        
        # Invalid: wrong type for success field
        invalid_type_output = {"success": "yes", "result": "data"}
        errors = validate_task_output(invalid_type_output)
        self.assertEqual(len(errors), 1)
    
    def test_format_validation_errors(self):
        """Test formatting validation errors to a string."""
        errors = [
            ValidationError("Missing field", "config.api_key"),
            ValidationError("Must be integer", "config.timeout")
        ]
        
        formatted = format_validation_errors(errors)
        
        # Check that each error appears in the output
        self.assertIn("Field 'config.api_key': Missing field", formatted)
        self.assertIn("Field 'config.timeout': Must be integer", formatted)
        
        # Check empty errors case
        empty_formatted = format_validation_errors([])
        self.assertEqual(empty_formatted, "No validation errors")


if __name__ == "__main__":
    unittest.main() 