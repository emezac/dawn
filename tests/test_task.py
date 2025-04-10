"""
Unit tests for the Task class.

This module contains tests for the Task class functionality.
"""

import os
import sys
import unittest

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task import Task
from core.tools.registry import ToolRegistry


class TestTask(unittest.TestCase):
    """Test cases for the Task class."""

    def test_task_initialization(self):
        """Test that a task can be initialized with correct attributes."""
        task = Task(
            task_id="test_task",
            name="Test Task",
            is_llm_task=True,
            input_data={"prompt": "Test prompt"},
            max_retries=2,
        )

        self.assertEqual(task.id, "test_task")
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.input_data, {"prompt": "Test prompt"})
        self.assertEqual(task.output_data, {})
        self.assertTrue(task.is_llm_task)
        self.assertIsNone(task.tool_name)
        self.assertEqual(task.retry_count, 0)
        self.assertEqual(task.max_retries, 2)

    def test_tool_task_initialization(self):
        """Test that a tool task can be initialized with correct attributes."""
        task = Task(
            task_id="test_tool_task",
            name="Test Tool Task",
            is_llm_task=False,
            tool_name="calculate",
            input_data={"operation": "add", "a": 1, "b": 2},
            max_retries=1,
        )

        self.assertEqual(task.id, "test_tool_task")
        self.assertEqual(task.name, "Test Tool Task")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.input_data, {"operation": "add", "a": 1, "b": 2})
        self.assertEqual(task.output_data, {})
        self.assertFalse(task.is_llm_task)
        self.assertEqual(task.tool_name, "calculate")
        self.assertEqual(task.retry_count, 0)
        self.assertEqual(task.max_retries, 1)

    def test_invalid_task_initialization(self):
        """Test that initializing a non-LLM task without a tool name raises an error."""
        with self.assertRaises(ValueError):
            Task(
                task_id="invalid_task",
                name="Invalid Task",
                is_llm_task=False,
                input_data={"data": "test"},
            )

    def test_set_status(self):
        """Test that task status can be updated."""
        task = Task(task_id="status_task", name="Status Task", is_llm_task=True)

        self.assertEqual(task.status, "pending")

        task.set_status("running")
        self.assertEqual(task.status, "running")

        task.set_status("completed")
        self.assertEqual(task.status, "completed")

        task.set_status("failed")
        self.assertEqual(task.status, "failed")

    def test_invalid_status(self):
        """Test that setting an invalid status raises an error."""
        task = Task(task_id="invalid_status_task", name="Invalid Status Task", is_llm_task=True)

        with self.assertRaises(ValueError):
            task.set_status("invalid_status")

    def test_increment_retry(self):
        """Test that retry count can be incremented."""
        task = Task(task_id="retry_task", name="Retry Task", is_llm_task=True, max_retries=3)

        self.assertEqual(task.retry_count, 0)

        task.increment_retry()
        self.assertEqual(task.retry_count, 1)

        task.increment_retry()
        self.assertEqual(task.retry_count, 2)

    def test_can_retry(self):
        """Test that can_retry returns correct values based on retry count and max retries."""
        task = Task(task_id="can_retry_task", name="Can Retry Task", is_llm_task=True, max_retries=2)

        self.assertTrue(task.can_retry())  # 0 < 2

        task.increment_retry()
        self.assertTrue(task.can_retry())  # 1 < 2

        task.increment_retry()
        self.assertFalse(task.can_retry())  # 2 >= 2

    def test_set_input_output(self):
        """Test that input and output data can be set."""
        task = Task(task_id="data_task", name="Data Task", is_llm_task=True)

        input_data = {"prompt": "New prompt"}
        task.set_input(input_data)
        self.assertEqual(task.input_data, input_data)

        output_data = {"response": "Test response"}
        task.set_output(output_data)
        self.assertEqual(task.output_data, output_data)

    def test_to_dict(self):
        """Test that to_dict returns a correct dictionary representation of the task."""
        task = Task(
            task_id="dict_task",
            name="Dict Task",
            is_llm_task=True,
            input_data={"prompt": "Test prompt"},
            max_retries=2,
            next_task_id_on_success="success_task",
            next_task_id_on_failure="failure_task",
        )

        task_dict = task.to_dict()

        self.assertEqual(task_dict["id"], "dict_task")
        self.assertEqual(task_dict["name"], "Dict Task")
        self.assertEqual(task_dict["status"], "pending")
        self.assertEqual(task_dict["input_data"], {"prompt": "Test prompt"})
        self.assertEqual(task_dict["output_data"], {})
        self.assertTrue(task_dict["is_llm_task"])
        self.assertIsNone(task_dict["tool_name"])
        self.assertEqual(task_dict["retry_count"], 0)
        self.assertEqual(task_dict["max_retries"], 2)
        self.assertEqual(task_dict["next_task_id_on_success"], "success_task")
        self.assertEqual(task_dict["next_task_id_on_failure"], "failure_task")


if __name__ == "__main__":
    unittest.main()
