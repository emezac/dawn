"""
Simple tests for variable resolver functionality.

This module contains basic tests for the variable resolver that don't depend on
workflow execution.
"""

import os
import sys
import unittest

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.utils.variable_resolver import resolve_variables


class TestVariableResolverSimple(unittest.TestCase):
    """Basic tests for variable resolution."""  # noqa: D202

    def test_simple_resolution(self):
        """Test resolving simple variables in a string."""
        # Create a simple context with task output
        context = {
            "task1": {
                "output_data": {
                    "value": 42,
                    "message": "Hello, World!"
                }
            }
        }
        
        # Test resolving a variable in a string
        template = "The answer is ${task1.output_data.value}"
        resolved = resolve_variables(template, context)
        self.assertEqual(resolved, "The answer is 42")
        
        # Test resolving a full variable (no surrounding text)
        template = "${task1.output_data.message}"
        resolved = resolve_variables(template, context)
        self.assertEqual(resolved, "Hello, World!")
    
    def test_nested_resolution(self):
        """Test resolving variables in nested data structures."""
        # Create a context with nested data
        context = {
            "task1": {
                "output_data": {
                    "user": {
                        "name": "Alice",
                        "age": 30
                    },
                    "items": ["apple", "banana", "cherry"]
                }
            }
        }
        
        # Test resolving variables in a dictionary
        template = {
            "user_name": "${task1.output_data.user.name}",
            "user_details": {
                "age": "${task1.output_data.user.age}",
                "favorite_fruit": "${task1.output_data.items[1]}"
            }
        }
        
        resolved = resolve_variables(template, context)
        
        # Check the resolved values
        self.assertEqual(resolved["user_name"], "Alice")
        self.assertEqual(resolved["user_details"]["age"], 30)
        self.assertEqual(resolved["user_details"]["favorite_fruit"], "banana")
    
    def test_list_resolution(self):
        """Test resolving variables in a list."""
        context = {
            "task1": {
                "output_data": {
                    "values": [10, 20, 30]
                }
            }
        }
        
        # Test resolving variables in a list
        template = [
            "${task1.output_data.values[0]}",
            "${task1.output_data.values[1]}",
            "${task1.output_data.values[2]}"
        ]
        
        resolved = resolve_variables(template, context)
        
        # Check the resolved values
        self.assertEqual(resolved[0], 10)
        self.assertEqual(resolved[1], 20)
        self.assertEqual(resolved[2], 30)
    
    def test_nonexistent_variable(self):
        """Test behavior when a variable doesn't exist."""
        context = {
            "task1": {
                "output_data": {
                    "value": 42
                }
            }
        }
        
        # Test with a nonexistent variable
        template = "Missing: ${task1.output_data.missing}"
        resolved = resolve_variables(template, context)
        
        # The original reference should remain
        self.assertEqual(resolved, "Missing: ${task1.output_data.missing}")
        
        # Test with a completely nonexistent task
        template = "Task: ${task2.output_data.value}"
        resolved = resolve_variables(template, context)
        self.assertEqual(resolved, "Task: ${task2.output_data.value}")
    
    def test_mixed_resolution(self):
        """Test resolving a mix of existing and nonexistent variables."""
        context = {
            "task1": {
                "output_data": {
                    "value": 42
                }
            }
        }
        
        # Test with both existing and nonexistent variables
        template = "Found: ${task1.output_data.value}, Missing: ${task1.output_data.missing}"
        resolved = resolve_variables(template, context)
        
        # The existing variable should be resolved, the nonexistent one should remain
        self.assertEqual(resolved, "Found: 42, Missing: ${task1.output_data.missing}")


if __name__ == "__main__":
    unittest.main() 