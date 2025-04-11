"""
Integration tests for task variable resolution within a workflow.

This module tests how task outputs are used as inputs for downstream tasks,
with variable resolution and validation.
"""

import os
import sys
import unittest
from typing import Dict, Any, List
from unittest.mock import MagicMock

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task import Task, DirectHandlerTask
from core.workflow import Workflow
from core.engine import WorkflowEngine
from core.utils.variable_resolver import resolve_variables, build_context_from_workflow


# Helper functions to use in DirectHandlerTasks
def process_data_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process input data and return a result."""
    value = input_data.get("value", 0)
    multiplier = input_data.get("multiplier", 1)
    result = value * multiplier
    
    return {
        "success": True,
        "result": {
            "processed_value": result,
            "original_value": value,
            "multiplier": multiplier
        }
    }


def format_result_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format the result from a previous task."""
    value = input_data.get("value", 0)
    label = input_data.get("label", "Result")
    
    return {
        "success": True,
        "result": {
            "formatted": f"{label}: {value}",
            "raw_value": value
        }
    }


def validate_result_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a result against a threshold."""
    value = input_data.get("value", 0)
    threshold = input_data.get("threshold", 0)
    
    if value > threshold:
        return {
            "success": True,
            "result": {
                "valid": True,
                "message": f"Value {value} exceeds threshold {threshold}"
            }
        }
    else:
        return {
            "success": True,
            "result": {
                "valid": False,
                "message": f"Value {value} does not exceed threshold {threshold}"
            }
        }


class TestManualVariableResolution(unittest.TestCase):
    """Test cases for manual variable resolution outside of a workflow."""  # noqa: D202
    
    def test_build_context_and_manual_resolution(self):
        """Test manual building of context and variable resolution."""
        # Set up tasks with output data
        task1 = Task(task_id="task1", name="Task 1", is_llm_task=True)
        task1.set_output({"response": {"value": 100, "status": "success"}})
        task1.set_status("completed")
        
        task2 = Task(task_id="task2", name="Task 2", is_llm_task=False, tool_name="test_tool")
        task2.set_output({"result": {"items": ["a", "b", "c"]}})
        task2.set_status("completed")
        
        # Create a workflow tasks dictionary (as would be found in a real workflow)
        workflow_tasks = {
            "task1": task1.to_dict(),
            "task2": task2.to_dict()
        }
        
        # Build context from the workflow tasks
        context = build_context_from_workflow(workflow_tasks)
        
        # Test manual variable resolution
        input_template = {
            "simple_value": "${task1.output_data.value}",
            "nested_value": {
                "item": "${task2.output_data.items[1]}",
                "status": "${task1.output_data.status}"
            }
        }
        
        resolved = resolve_variables(input_template, context)
        
        # Verify resolution results
        self.assertEqual(resolved["simple_value"], 100)
        self.assertEqual(resolved["nested_value"]["item"], "b")
        self.assertEqual(resolved["nested_value"]["status"], "success")


class MockWorkflowEngine:
    """A simplified mock workflow engine for testing."""  # noqa: D202
    
    def __init__(self, workflow):
        self.workflow = workflow
    
    def run(self):
        """Run the workflow, simulating the execution of tasks with variable resolution."""
        # Build initial context
        context = {}
        
        # Execute tasks in sequence, resolving variables
        for task_id, task in self.workflow.tasks.items():
            # Skip tasks that have already been processed
            if task.status != "pending":
                continue
                
            # Process input data (resolve variables)
            processed_input = self._process_task_input(task, context)
            
            # Execute task
            if hasattr(task, 'is_direct_handler') and task.is_direct_handler:
                result = task.execute(processed_input)
                if result.get("success", False):
                    output_data = {}
                    if "response" in result:
                        output_data["response"] = result["response"]
                    if "result" in result:
                        output_data["result"] = result["result"]
                    task.set_output(output_data)
                    task.set_status("completed")
                    
                    # Update context with this task's output for downstream tasks
                    task_dict = task.to_dict()
                    context[task_id] = {
                        "id": task_id,
                        "status": task_dict["status"],
                        "output_data": task_dict["output_data"]
                    }
    
    def _process_task_input(self, task, context):
        """Process the task input by resolving variables."""
        return resolve_variables(task.input_data.copy(), context)


class TestTaskVariableResolution(unittest.TestCase):
    """Test cases for integrated task variable resolution in a workflow."""  # noqa: D202

    def setUp(self):
        """Set up a workflow with tasks that use variable resolution."""
        # Create a workflow
        self.workflow = Workflow(workflow_id="test_workflow", name="Test Variable Resolution")
        
        # Task 1: Process initial data
        self.task1 = DirectHandlerTask(
            task_id="process_data",
            name="Process Data",
            handler=process_data_handler,
            input_data={
                "value": 10,
                "multiplier": 5
            },
            next_task_id_on_success="format_result"
        )
        self.workflow.add_task(self.task1)
        
        # Task 2: Format the result using variable resolution
        self.task2 = DirectHandlerTask(
            task_id="format_result",
            name="Format Result",
            handler=format_result_handler,
            input_data={
                "value": "${process_data.output_data.processed_value}",
                "label": "Processed Value"
            },
            next_task_id_on_success="validate_result"
        )
        self.workflow.add_task(self.task2)
        
        # Task 3: Validate the result using variable resolution
        self.task3 = DirectHandlerTask(
            task_id="validate_result",
            name="Validate Result",
            handler=validate_result_handler,
            input_data={
                "value": "${format_result.output_data.raw_value}",
                "threshold": 30
            }
        )
        self.workflow.add_task(self.task3)
        
        # Use our custom mock engine for testing
        self.engine = MockWorkflowEngine(self.workflow)

    def test_workflow_variable_resolution(self):
        """Test that variables are correctly resolved during workflow execution."""
        # Execute the workflow
        self.engine.run()
        
        # Verify task1 executed correctly
        self.assertEqual(self.task1.status, "completed")
        self.assertEqual(self.task1.output_data["result"]["processed_value"], 50)
        
        # Verify task2 received the resolved value from task1
        self.assertEqual(self.task2.status, "completed")
        self.assertEqual(self.task2.output_data["result"]["formatted"], "Processed Value: 50")
        self.assertEqual(self.task2.output_data["result"]["raw_value"], 50)
        
        # Verify task3 received the resolved value from task2
        self.assertEqual(self.task3.status, "completed")
        self.assertEqual(self.task3.output_data["result"]["valid"], True)
        self.assertIn("50", self.task3.output_data["result"]["message"])
    
    def test_complex_path_resolution(self):
        """Test resolution of complex paths with nested structures and arrays."""
        # Create a workflow with nested data
        workflow = Workflow(workflow_id="nested_workflow", name="Nested Data Test")
        
        # Task 1: Generate nested data
        task1 = DirectHandlerTask(
            task_id="generate_data",
            name="Generate Nested Data",
            handler=lambda input_data: {
                "success": True,
                "result": {
                    "users": [
                        {"id": 1, "name": "Alice", "scores": [10, 20, 30]},
                        {"id": 2, "name": "Bob", "scores": [15, 25, 35]}
                    ],
                    "metadata": {
                        "count": 2,
                        "tags": ["user", "data"]
                    }
                }
            },
            input_data={},
            next_task_id_on_success="process_nested"
        )
        workflow.add_task(task1)
        
        # Task 2: Access nested data using complex paths
        task2 = DirectHandlerTask(
            task_id="process_nested",
            name="Process Nested Data",
            handler=lambda input_data: {
                "success": True,
                "result": {
                    "user_name": input_data.get("user_name"),
                    "high_score": input_data.get("high_score"),
                    "tag": input_data.get("tag"),
                    "count": input_data.get("count")
                }
            },
            input_data={
                "user_name": "${generate_data.output_data.users[1].name}",
                "high_score": "${generate_data.output_data.users[0].scores[2]}",
                "tag": "${generate_data.output_data.metadata.tags[0]}",
                "count": "${generate_data.output_data.metadata.count}"
            }
        )
        workflow.add_task(task2)
        
        # Use our mock engine
        engine = MockWorkflowEngine(workflow)
        
        # Execute the workflow
        engine.run()
        
        # Verify resolution of complex paths
        self.assertEqual(task2.status, "completed")
        self.assertEqual(task2.output_data["result"]["user_name"], "Bob")
        self.assertEqual(task2.output_data["result"]["high_score"], 30)
        self.assertEqual(task2.output_data["result"]["tag"], "user")
        self.assertEqual(task2.output_data["result"]["count"], 2)
    
    def test_error_handling_in_resolution(self):
        """Test error handling when variable resolution fails."""
        workflow = Workflow(workflow_id="error_workflow", name="Error Handling Test")
        
        # Task 1: Generate data
        task1 = DirectHandlerTask(
            task_id="source_task",
            name="Source Task",
            handler=lambda input_data: {
                "success": True,
                "result": {"value": 42}
            },
            input_data={},
            next_task_id_on_success="error_handling_task"
        )
        workflow.add_task(task1)
        
        # Task 2: Try to access nonexistent path
        task2 = DirectHandlerTask(
            task_id="error_handling_task",
            name="Error Handling Task",
            handler=lambda input_data: {
                "success": True,
                "result": {
                    "resolved_value": input_data.get("existing_value"),
                    "fallback_value": input_data.get("nonexistent_value", "fallback")
                }
            },
            input_data={
                "existing_value": "${source_task.output_data.value}",
                "nonexistent_value": "${source_task.output_data.nonexistent_path}"
            }
        )
        workflow.add_task(task2)
        
        # Use our mock engine
        engine = MockWorkflowEngine(workflow)
        
        # Execute the workflow
        engine.run()
        
        # Verify task2 executed successfully
        self.assertEqual(task2.status, "completed")
        
        # The existing path should be resolved correctly
        self.assertEqual(task2.output_data["result"]["resolved_value"], 42)
        
        # The nonexistent path should use the fallback value
        self.assertEqual(task2.output_data["result"]["fallback_value"], "fallback")


if __name__ == "__main__":
    unittest.main() 