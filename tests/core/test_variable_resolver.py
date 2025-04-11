"""
Tests for the variable resolver functionality in the Dawn framework.

This module contains tests for the variable resolver functions,
including path resolution and context building.
"""

import os
import sys
import unittest

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.utils.variable_resolver import (
    resolve_path, 
    resolve_variables, 
    get_variable_value, 
    build_context_from_workflow
)


class TestVariableResolver(unittest.TestCase):
    """Test cases for variable resolver functionality."""  # noqa: D202

    def test_resolve_path_simple(self):
        """Test simple path resolution in a nested dictionary."""
        data = {
            "field1": "value1",
            "nested": {
                "field2": "value2",
                "list": [1, 2, 3]
            }
        }
        
        # Test simple field access
        self.assertEqual(resolve_path(data, "field1"), "value1")
        
        # Test nested field access
        self.assertEqual(resolve_path(data, "nested.field2"), "value2")
        
        # Test list access
        self.assertEqual(resolve_path(data, "nested.list[1]"), 2)
        
    def test_resolve_path_complex(self):
        """Test complex path resolution with nested lists and dictionaries."""
        data = {
            "users": [
                {"name": "Alice", "roles": ["admin", "user"]},
                {"name": "Bob", "roles": ["user"]}
            ],
            "settings": {
                "theme": {
                    "colors": ["red", "green", "blue"]
                }
            }
        }
        
        # Test nested list+dict access
        self.assertEqual(resolve_path(data, "users[0].name"), "Alice")
        self.assertEqual(resolve_path(data, "users[1].roles[0]"), "user")
        
        # Test deeply nested path
        self.assertEqual(resolve_path(data, "settings.theme.colors[1]"), "green")
    
    def test_resolve_path_error_handling(self):
        """Test error handling in path resolution."""
        data = {"field1": "value1", "list": [1, 2, 3]}
        
        # Test key error
        with self.assertRaises(KeyError):
            resolve_path(data, "nonexistent")
        
        # Test index error
        with self.assertRaises(IndexError):
            resolve_path(data, "list[10]")
        
        # Test type error (trying to index a non-list/dict)
        with self.assertRaises(ValueError):
            resolve_path(data, "field1[0]")
    
    def test_resolve_variables_simple(self):
        """Test simple variable resolution."""
        context = {
            "task1": {
                "output_data": {"result": "success"}
            }
        }
        
        # Test simple variable
        input_str = "Result: ${task1.output_data.result}"
        self.assertEqual(resolve_variables(input_str, context), "Result: success")
        
        # Test full variable replacement
        input_str = "${task1.output_data.result}"
        self.assertEqual(resolve_variables(input_str, context), "success")
    
    def test_resolve_variables_nested(self):
        """Test variable resolution in nested data structures."""
        context = {
            "task1": {
                "output_data": {"value": 42, "message": "hello"}
            },
            "task2": {
                "output_data": {"items": ["a", "b", "c"]}
            }
        }
        
        # Test variable in dictionary
        input_data = {
            "value": "${task1.output_data.value}",
            "text": "Message: ${task1.output_data.message}",
            "list": ["${task2.output_data.items[0]}", "${task2.output_data.items[1]}"]
        }
        
        expected = {
            "value": 42,  # Full replacement returns the actual value
            "text": "Message: hello",  # String interpolation
            "list": ["a", "b"]  # List with resolved values
        }
        
        self.assertEqual(resolve_variables(input_data, context), expected)
    
    def test_resolve_variables_nonexistent(self):
        """Test handling of nonexistent variables."""
        context = {"task1": {"output_data": {"result": "success"}}}
        
        # Test nonexistent variable - should leave the original reference
        input_str = "Value: ${task2.output_data.result}"
        self.assertEqual(resolve_variables(input_str, context), input_str)
        
        # Test mixed existing and nonexistent
        input_str = "Values: ${task1.output_data.result} and ${task2.output_data.result}"
        self.assertEqual(resolve_variables(input_str, context), "Values: success and ${task2.output_data.result}")
    
    def test_resolve_variables_recursion_limit(self):
        """Test that resolve_variables enforces a recursion limit."""
        context = {"task1": {"output_data": {"result": "value"}}}
        
        # Create a recursive structure that would cause infinite recursion
        with self.assertRaises(RecursionError):
            resolve_variables("${task1.output_data.result}", context, max_depth=0)
    
    def test_get_variable_value(self):
        """Test getting variable values from context."""
        context = {
            "task1": {
                "status": "completed",
                "output_data": {
                    "result": "success",
                    "data": {
                        "count": 42
                    }
                }
            }
        }
        
        # Test basic output_data access
        self.assertEqual(get_variable_value("task1.output_data", context), 
                        {"result": "success", "data": {"count": 42}})
        
        # Test accessing nested field
        self.assertEqual(get_variable_value("task1.output_data.data.count", context), 42)
        
        # Test accessing non-output field
        self.assertEqual(get_variable_value("task1.status", context), "completed")
        
        # Test nonexistent task
        with self.assertRaises(KeyError):
            get_variable_value("task2.output_data", context)
        
        # Test nonexistent field
        with self.assertRaises(ValueError):
            get_variable_value("task1.output_data.nonexistent", context)
        
        # Test invalid variable path
        with self.assertRaises(ValueError):
            get_variable_value("task1", context)  # Missing field path
    
    def test_build_context_from_workflow(self):
        """Test building context from workflow tasks."""
        workflow_tasks = {
            "task1": {
                "status": "completed",
                "output_data": {"result": "success"}
            },
            "task2": {
                "status": "failed",
                "output_data": {"error": "something went wrong"}
            }
        }
        
        context = build_context_from_workflow(workflow_tasks)
        
        # Check task1 context
        self.assertEqual(context["task1"]["id"], "task1")
        self.assertEqual(context["task1"]["status"], "completed")
        self.assertEqual(context["task1"]["output_data"], {"result": "success"})
        
        # Check task2 context
        self.assertEqual(context["task2"]["id"], "task2")
        self.assertEqual(context["task2"]["status"], "failed")
        self.assertEqual(context["task2"]["output_data"], {"error": "something went wrong"})


if __name__ == "__main__":
    unittest.main() 