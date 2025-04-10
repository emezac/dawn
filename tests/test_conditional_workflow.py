import os
import sys
import unittest
from unittest.mock import patch

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.engine import WorkflowEngine
from core.llm.interface import LLMInterface
from core.task import Task
from core.tools.registry import ToolRegistry
from core.workflow import Workflow
from tools.basic_tools import calculate, check_length


# Dummy LLM interface that returns a sufficiently long response.
class DummyLLMInterface(LLMInterface):
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key=api_key, model=model)

    def execute_llm_call(self, prompt: str) -> dict:
        # Return a response that's clearly over 100 characters.
        long_response = (
            "This is a regenerated output that is sufficiently long to pass the condition. "
            "It contains many details and exceeds one hundred characters easily."
        )
        return {"success": True, "response": long_response}


class TestConditionalWorkflow(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry and dummy tasks for conditional branching."""
        # Create a workflow with three tasks:
        # Task A (initial task) with a short output.
        # Task B (regeneration) is the failure branch.
        # Task Success is the branch to follow on success.
        self.workflow = Workflow("test_workflow", "Test Conditional Workflow")

        # Task A: Simulated task with a short output.
        self.task_a = Task(
            task_id="task_a",
            name="Task A (Short Output)",
            is_llm_task=False,
            tool_name="dummy_tool",
            input_data={},
            next_task_id_on_success="task_success",  # Success branch if condition met
            next_task_id_on_failure="task_b",  # Failure branch if condition not met
            condition="len(output_data['response']) > 100",  # Condition: output must be > 100 characters
        )
        # Simulate Task A output as too short.
        self.task_a.set_output({"response": "short"})

        # Task B: Regeneration task to be executed if Task A output is too short.
        self.task_b = Task(
            task_id="task_b",
            name="Regenerate Task",
            is_llm_task=True,
            input_data={"prompt": "Regenerate a longer output based on the training document."},
            next_task_id_on_success="task_success",
        )

        # Task Success: A dummy task to represent successful branch after regeneration.
        self.task_success = Task(
            task_id="task_success",
            name="Success Task",
            is_llm_task=False,
            tool_name="dummy_tool",
            input_data={},
        )

        # Add tasks to the workflow.
        self.workflow.add_task(self.task_a)
        self.workflow.add_task(self.task_b)
        self.workflow.add_task(self.task_success)

        # Use our DummyLLMInterface which returns a long response.
        self.llm_interface = DummyLLMInterface(api_key="dummy", model="dummy")

        # Create the workflow engine.
        self.engine = WorkflowEngine(
            workflow=self.workflow,
            llm_interface=self.llm_interface,
            tool_registry=ToolRegistry(),  # Using default registry
        )

    def test_conditional_branch(self):
        # With Task A's short output, the engine should choose task_b (failure branch).
        next_task = self.engine.get_next_task_by_condition(self.task_a)
        self.assertIsNotNone(next_task, "Next task should not be None")
        self.assertEqual(
            next_task.id,
            "task_b",
            "Engine should select the failure branch (task_b) when condition is not met",
        )

        # Simulate executing Task B (LLM task) which regenerates a long output.
        regenerated_result = self.llm_interface.execute_llm_call(self.task_b.input_data["prompt"])
        self.task_b.set_output({"response": regenerated_result["response"]})
        # Mark Task B as completed
        self.task_b.set_status("completed")

        # Ensure that the regenerated output is longer than 100 characters.
        self.assertTrue(
            len(self.task_b.output_data["response"]) > 100,
            "Regenerated output should be longer than 100 characters",
        )

        # Now, after Task B completes, the engine should select the success branch (task_success).
        next_after_b = self.engine.get_next_task_by_condition(self.task_b)
        self.assertIsNotNone(next_after_b, "Next task after Task B should not be None")
        self.assertEqual(
            next_after_b.id,
            "task_success",
            "Engine should proceed to task_success after regeneration",
        )


if __name__ == "__main__":
    unittest.main()
