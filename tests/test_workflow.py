"""
Unit tests for the Workflow class.

This module contains tests for the Workflow class functionality.
"""

import unittest
from core.task import Task
from core.workflow import Workflow


class TestWorkflow(unittest.TestCase):
    """Test cases for the Workflow class."""
    
    def test_workflow_initialization(self):
        """Test that a workflow can be initialized with correct attributes."""
        workflow = Workflow(
            workflow_id="test_workflow",
            name="Test Workflow"
        )
        
        self.assertEqual(workflow.id, "test_workflow")
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.status, "pending")
        self.assertEqual(workflow.tasks, {})
        self.assertEqual(workflow.task_order, [])
        self.assertEqual(workflow.current_task_index, 0)
    
    def test_add_task(self):
        """Test that tasks can be added to a workflow."""
        workflow = Workflow(
            workflow_id="add_task_workflow",
            name="Add Task Workflow"
        )
        
        task1 = Task(
            task_id="task1",
            name="Task 1",
            is_llm_task=True
        )
        
        task2 = Task(
            task_id="task2",
            name="Task 2",
            is_llm_task=False,
            tool_name="calculate"
        )
        
        workflow.add_task(task1)
        self.assertEqual(len(workflow.tasks), 1)
        self.assertEqual(len(workflow.task_order), 1)
        self.assertEqual(workflow.task_order[0], "task1")
        self.assertEqual(workflow.tasks["task1"], task1)
        
        workflow.add_task(task2)
        self.assertEqual(len(workflow.tasks), 2)
        self.assertEqual(len(workflow.task_order), 2)
        self.assertEqual(workflow.task_order[1], "task2")
        self.assertEqual(workflow.tasks["task2"], task2)
    
    def test_add_duplicate_task(self):
        """Test that adding a task with a duplicate ID raises an error."""
        workflow = Workflow(
            workflow_id="duplicate_workflow",
            name="Duplicate Task Workflow"
        )
        
        task1 = Task(
            task_id="task1",
            name="Task 1",
            is_llm_task=True
        )
        
        task2 = Task(
            task_id="task1",  # Same ID as task1
            name="Task 2",
            is_llm_task=True
        )
        
        workflow.add_task(task1)
        
        with self.assertRaises(ValueError):
            workflow.add_task(task2)
    
    def test_get_task(self):
        """Test that tasks can be retrieved by ID."""
        workflow = Workflow(
            workflow_id="get_task_workflow",
            name="Get Task Workflow"
        )
        
        task = Task(
            task_id="task1",
            name="Task 1",
            is_llm_task=True
        )
        
        workflow.add_task(task)
        
        retrieved_task = workflow.get_task("task1")
        self.assertEqual(retrieved_task, task)
    
    def test_get_nonexistent_task(self):
        """Test that getting a nonexistent task raises an error."""
        workflow = Workflow(
            workflow_id="nonexistent_workflow",
            name="Nonexistent Task Workflow"
        )
        
        with self.assertRaises(KeyError):
            workflow.get_task("nonexistent_task")
    
    def test_get_next_task(self):
        """Test that tasks can be retrieved in order."""
        workflow = Workflow(
            workflow_id="next_task_workflow",
            name="Next Task Workflow"
        )
        
        task1 = Task(
            task_id="task1",
            name="Task 1",
            is_llm_task=True
        )
        
        task2 = Task(
            task_id="task2",
            name="Task 2",
            is_llm_task=True
        )
        
        workflow.add_task(task1)
        workflow.add_task(task2)
        
        next_task = workflow.get_next_task()
        self.assertEqual(next_task, task1)
        self.assertEqual(workflow.current_task_index, 1)
        
        next_task = workflow.get_next_task()
        self.assertEqual(next_task, task2)
        self.assertEqual(workflow.current_task_index, 2)
        
        next_task = workflow.get_next_task()
        self.assertIsNone(next_task)
        self.assertEqual(workflow.current_task_index, 2)
    
    def test_get_next_task_by_condition(self):
        """Test that next task can be determined based on conditions."""
        workflow = Workflow(
            workflow_id="conditional_workflow",
            name="Conditional Workflow"
        )
        
        task1 = Task(
            task_id="task1",
            name="Task 1",
            is_llm_task=True,
            next_task_id_on_success="task3"
        )
        
        task2 = Task(
            task_id="task2",
            name="Task 2",
            is_llm_task=True
        )
        
        task3 = Task(
            task_id="task3",
            name="Task 3",
            is_llm_task=True
        )
        
        workflow.add_task(task1)
        workflow.add_task(task2)
        workflow.add_task(task3)
        
        # Set task1 as completed to test conditional next task
        task1.set_status("completed")
        
        next_task = workflow.get_next_task_by_condition(task1)
        self.assertEqual(next_task, task3)
        self.assertEqual(workflow.current_task_index, 2)
    
    def test_set_status(self):
        """Test that workflow status can be updated."""
        workflow = Workflow(
            workflow_id="status_workflow",
            name="Status Workflow"
        )
        
        self.assertEqual(workflow.status, "pending")
        
        workflow.set_status("running")
        self.assertEqual(workflow.status, "running")
        
        workflow.set_status("completed")
        self.assertEqual(workflow.status, "completed")
        
        workflow.set_status("failed")
        self.assertEqual(workflow.status, "failed")
    
    def test_invalid_status(self):
        """Test that setting an invalid status raises an error."""
        workflow = Workflow(
            workflow_id="invalid_status_workflow",
            name="Invalid Status Workflow"
        )
        
        with self.assertRaises(ValueError):
            workflow.set_status("invalid_status")
    
    def test_is_completed(self):
        """Test that is_completed returns correct values based on workflow status and task statuses."""
        workflow = Workflow(
            workflow_id="completed_workflow",
            name="Completed Workflow"
        )
        
        task1 = Task(
            task_id="task1",
            name="Task 1",
            is_llm_task=True
        )
        
        task2 = Task(
            task_id="task2",
            name="Task 2",
            is_llm_task=True
        )
        
        workflow.add_task(task1)
        workflow.add_task(task2)
        
        # Initially, workflow is not completed
        self.assertFalse(workflow.is_completed())
        
        # If workflow status is completed, is_completed should return True
        workflow.set_status("completed")
        self.assertTrue(workflow.is_completed())
        
        # Reset workflow status
        workflow.set_status("running")
        self.assertFalse(workflow.is_completed())
        
        # If all tasks are completed, is_completed should return True
        task1.set_status("completed")
        task2.set_status("completed")
        self.assertTrue(workflow.is_completed())
    
    def test_to_dict(self):
        """Test that to_dict returns a correct dictionary representation of the workflow."""
        workflow = Workflow(
            workflow_id="dict_workflow",
            name="Dict Workflow"
        )
        
        task = Task(
            task_id="task1",
            name="Task 1",
            is_llm_task=True
        )
        
        workflow.add_task(task)
        
        workflow_dict = workflow.to_dict()
        
        self.assertEqual(workflow_dict["id"], "dict_workflow")
        self.assertEqual(workflow_dict["name"], "Dict Workflow")
        self.assertEqual(workflow_dict["status"], "pending")
        self.assertEqual(len(workflow_dict["tasks"]), 1)
        self.assertEqual(workflow_dict["task_order"], ["task1"])
        self.assertEqual(workflow_dict["current_task_index"], 0)
        self.assertEqual(workflow_dict["tasks"]["task1"]["id"], "task1")


if __name__ == "__main__":
    unittest.main()
