"""
Tests for the task output functionality in the Dawn framework.

This module contains tests for task output handling, 
including the Task and DirectHandlerTask classes.
"""

import os
import sys
import unittest
from typing import Any, Dict, Optional, List

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.task import Task, DirectHandlerTask, TaskOutput


class TestTaskOutput(unittest.TestCase):
    """Test cases for task output functionality."""  # noqa: D202

    def test_task_output_typeddict(self):
        """Test the TaskOutput TypedDict structure."""
        # Create a valid TaskOutput dict
        output: TaskOutput = {
            "response": "Task completed successfully",
            "result": {"status": "done", "count": 42},
            "metadata": {"duration_ms": 150}
        }
        
        # Ensure we can access fields
        self.assertEqual(output["response"], "Task completed successfully")
        self.assertEqual(output["result"]["count"], 42)

        # Create an output with error information
        error_output: TaskOutput = {
            "error": "Something went wrong",
            "error_type": "RuntimeError",
            "error_details": {"line": 42, "function": "process_data"}
        }
        
        self.assertEqual(error_output["error"], "Something went wrong")
        self.assertEqual(error_output["error_type"], "RuntimeError")
    
    def test_set_output(self):
        """Test setting task output with different structures."""
        task = Task(task_id="test_task", name="Test Task", is_llm_task=True)
        
        # Test setting output with response
        task.set_output({"response": "Task result"})
        self.assertEqual(task.output_data["response"], "Task result")
        
        # Test setting output with result
        task.set_output({"result": {"value": 42}})
        self.assertEqual(task.output_data["result"]["value"], 42)
        self.assertEqual(task.output_data["response"]["value"], 42)  # response should mirror result
        
        # Test setting output with error
        task.set_output({"error": "Task failed", "error_type": "ValidationError"})
        self.assertEqual(task.output_data["error"], "Task failed")
        self.assertEqual(task.output_data["error_type"], "ValidationError")
        self.assertEqual(task.error, "Task failed")
        
        # Test setting output with additional fields
        task.set_output({
            "response": "Data processed",
            "count": 5,
            "timing": {"start": 100, "end": 200}
        })
        self.assertEqual(task.output_data["response"], "Data processed")
        self.assertEqual(task.output_data["count"], 5)
        self.assertEqual(task.output_data["timing"]["end"], 200)
    
    def test_get_output_value(self):
        """Test getting output values with various paths."""
        task = Task(task_id="output_task", name="Output Test Task", is_llm_task=True)
        
        # Set up complex output data
        task.set_output({
            "response": {
                "status": "success",
                "data": {
                    "items": [
                        {"id": 1, "name": "Item 1"},
                        {"id": 2, "name": "Item 2"}
                    ],
                    "metadata": {
                        "total_count": 2,
                        "page": 1
                    }
                }
            },
            "processed": True,
            "timestamp": 1234567890
        })
        
        # Test getting entire output when no path is provided
        self.assertEqual(task.get_output_value(), task.output_data["response"])
        
        # Test simple paths
        self.assertEqual(task.get_output_value("status"), "success")
        
        # Test nested paths
        self.assertEqual(task.get_output_value("data.metadata.total_count"), 2)
        
        # Test array indexing
        self.assertEqual(task.get_output_value("data.items[0].name"), "Item 1")
        self.assertEqual(task.get_output_value("data.items[1].id"), 2)
        
        # Test explicit response prefix
        self.assertEqual(task.get_output_value("response.data.metadata.page"), 1)
        
        # Test non-existent path with default
        self.assertEqual(task.get_output_value("data.nonexistent", "default"), "default")
        self.assertEqual(task.get_output_value("response.data.items[5]", None), None)
    
    def test_get_output_value_with_result(self):
        """Test getting output values from result field."""
        task = Task(task_id="result_task", name="Result Test Task", is_llm_task=True)
        
        # Set up output with result field
        task.set_output({
            "result": {
                "count": 42,
                "items": ["a", "b", "c"]
            }
        })
        
        # Test accessing result fields
        self.assertEqual(task.get_output_value("count"), 42)
        self.assertEqual(task.get_output_value("items[1]"), "b")
        
        # Test with explicit result prefix
        self.assertEqual(task.get_output_value("result.count"), 42)
    
    def test_direct_handler_task_output(self):
        """Test output handling in DirectHandlerTask."""
        def handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "success": True,
                "result": f"Processed: {input_data.get('value', 'unknown')}"
            }
        
        task = DirectHandlerTask(
            task_id="direct_handler_task",
            name="Direct Handler Task",
            handler=handler,
            input_data={"value": "test_data"}
        )
        
        # Execute the task
        result = task.execute()
        
        # Test that the handler's result is returned correctly
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "Processed: test_data")
        
        # Set the output based on the result
        task.set_output(result)
        
        # Test that output_data contains the handler's result
        self.assertEqual(task.output_data["result"], "Processed: test_data")
    
    def test_direct_handler_error_handling(self):
        """Test error handling in DirectHandlerTask."""
        def error_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            # Handler that always raises an exception
            raise ValueError("Invalid input provided")
        
        task = DirectHandlerTask(
            task_id="error_handler_task",
            name="Error Handler Task",
            handler=error_handler,
            input_data={}
        )
        
        # Execute the task (should catch the exception)
        result = task.execute()
        
        # Test that an error result is returned
        self.assertFalse(result["success"])
        self.assertIn("Handler execution failed: Invalid input provided", result["error"])
        self.assertEqual(result["error_type"], "ValueError")
        self.assertIn("traceback", result)
    
    def test_validation_in_direct_handler(self):
        """Test input and output validation in DirectHandlerTask."""
        # Simple dictionary-based handler (not using named parameters)
        def dict_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
            message = input_data.get("message", "")
            count = input_data.get("count", 0)
            
            return {
                "success": True,
                "result": message * count
            }
        
        # Create a task without validation
        task = DirectHandlerTask(
            task_id="validation_task",
            name="Validation Task",
            handler=dict_handler,
            input_data={"message": "test", "count": 3},
            validate_input=False  # No validation, since our handler uses dict input
        )
        
        # Execute directly without validation
        result = task.execute()
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "testtesttest")
        
        # Also test with specific input
        specific_result = task.execute({"message": "a", "count": 5})
        self.assertTrue(specific_result["success"])
        self.assertEqual(specific_result["result"], "aaaaa")
    
    def test_skipped_task_status(self):
        """Test the 'skipped' task status."""
        task = Task(task_id="skipped_task", name="Skipped Task", is_llm_task=True)
        
        # Set task status to skipped
        task.set_status("skipped")
        self.assertEqual(task.status, "skipped")
        
        # Ensure skipped status appears in to_dict()
        task_dict = task.to_dict()
        self.assertEqual(task_dict["status"], "skipped")


if __name__ == "__main__":
    unittest.main() 