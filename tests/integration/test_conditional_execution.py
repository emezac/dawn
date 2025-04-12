#!/usr/bin/env python3
"""
Integration Tests for Conditional Execution in Workflows

This module tests the conditional branching capabilities of the Dawn workflow engine,
verifying that workflows can make decisions based on task outputs and route accordingly.
"""  # noqa: D202

import unittest
import os
import sys
import logging
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import workflow components
from core.workflow import Workflow
from core.task import Task, ConditionalTask
from core.engine import WorkflowEngine
from core.utils.testing import MockToolRegistry, WorkflowTestHarness

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestConditionalExecution(unittest.TestCase):
    """Test suite for conditional execution in workflows."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Create a clean test harness
        self.harness = WorkflowTestHarness()
        
        # Register a decision tool that returns different results based on input
        def decision_tool(input_data):
            value = input_data.get("value", 0)
            if value > 10:
                return {
                    "success": True,
                    "result": "high",
                    "category": "above_threshold",
                    "is_valid": True
                }
            elif value > 5:
                return {
                    "success": True,
                    "result": "medium",
                    "category": "medium_threshold",
                    "is_valid": True
                }
            else:
                return {
                    "success": True,
                    "result": "low",
                    "category": "below_threshold",
                    "is_valid": False
                }
        
        self.harness.register_mock_tool("decision_tool", decision_tool)
        
        # Register a simple processing tool
        def process_tool(input_data):
            category = input_data.get("category", "unknown")
            return {
                "success": True,
                "result": f"Processed {category} data",
                "processed": True
            }
        
        self.harness.register_mock_tool("process_tool", process_tool)

    def test_basic_conditional_branching(self):
        """Test conditional task with multiple branches based on a condition."""
        workflow = Workflow(workflow_id="basic_conditional", name="Basic Conditional Workflow")
        
        # Task 1: Make a decision
        decision_task = Task(
            task_id="make_decision",
            name="Make Decision",
            tool_name="decision_tool",
            input_data={"value": 15},  # Should return "high"
            next_task_id_on_success="route_decision"
        )
        workflow.add_task(decision_task)
        
        # Task 2: Conditional routing based on the decision
        conditional_task = ConditionalTask(
            task_id="route_decision",
            name="Route Decision",
            conditions=[
                {
                    "condition": "${make_decision.output_data.result == 'high'}",
                    "next_task_id": "high_process"
                },
                {
                    "condition": "${make_decision.output_data.result == 'medium'}",
                    "next_task_id": "medium_process"
                },
                {
                    "condition": "${make_decision.output_data.result == 'low'}",
                    "next_task_id": "low_process"
                }
            ],
            default_task_id="unknown_process"
        )
        workflow.add_task(conditional_task)
        
        # Task 3-6: Different processing paths
        for category in ["high", "medium", "low", "unknown"]:
            process_task = Task(
                task_id=f"{category}_process",
                name=f"Process {category.capitalize()} Result",
                tool_name="process_tool",
                input_data={
                    "category": f"{category}"
                }
            )
            workflow.add_task(process_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that the right path was taken
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("make_decision", executed_tasks)
        self.assertIn("route_decision", executed_tasks)
        self.assertIn("high_process", executed_tasks)
        self.assertNotIn("medium_process", executed_tasks)
        self.assertNotIn("low_process", executed_tasks)
        self.assertNotIn("unknown_process", executed_tasks)
        
        # Verify the high process task was executed with the right input
        high_task = self.harness.get_task("high_process")
        self.assertEqual(high_task.input_data.get("category"), "high")
        self.assertEqual(high_task.output_data.get("result"), "Processed high data")

    def test_conditional_with_complex_expressions(self):
        """Test conditional routing with complex boolean expressions."""
        workflow = Workflow(workflow_id="complex_conditional", name="Complex Conditional Workflow")
        
        # Task 1: Make a decision
        decision_task = Task(
            task_id="make_decision",
            name="Make Decision",
            tool_name="decision_tool",
            input_data={"value": 7},  # Should return "medium"
            next_task_id_on_success="complex_route"
        )
        workflow.add_task(decision_task)
        
        # Task 2: Conditional routing with complex expressions
        conditional_task = ConditionalTask(
            task_id="complex_route",
            name="Complex Route",
            conditions=[
                {
                    # Check both result and is_valid
                    "condition": "${make_decision.output_data.result == 'high' and make_decision.output_data.is_valid == true}",
                    "next_task_id": "high_valid_process"
                },
                {
                    # Check multiple conditions with OR
                    "condition": "${make_decision.output_data.result == 'medium' or make_decision.output_data.category == 'medium_threshold'}",
                    "next_task_id": "medium_process"
                },
                {
                    # Check negation
                    "condition": "${make_decision.output_data.is_valid != true}",
                    "next_task_id": "invalid_process"
                }
            ],
            default_task_id="default_process"
        )
        workflow.add_task(conditional_task)
        
        # Tasks for different paths
        for path in ["high_valid", "medium", "invalid", "default"]:
            process_task = Task(
                task_id=f"{path}_process",
                name=f"Process {path.capitalize()} Path",
                tool_name="process_tool",
                input_data={
                    "category": path
                }
            )
            workflow.add_task(process_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that the medium path was taken (since value=7 returns "medium")
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("make_decision", executed_tasks)
        self.assertIn("complex_route", executed_tasks)
        self.assertIn("medium_process", executed_tasks)
        self.assertNotIn("high_valid_process", executed_tasks)
        self.assertNotIn("invalid_process", executed_tasks)
        self.assertNotIn("default_process", executed_tasks)

    def test_nested_conditional_execution(self):
        """Test nested conditional routing (conditions based on previous conditional branches)."""
        workflow = Workflow(workflow_id="nested_conditional", name="Nested Conditional Workflow")
        
        # First decision
        first_decision = Task(
            task_id="first_decision",
            name="First Decision",
            tool_name="decision_tool",
            input_data={"value": 15},  # Should return "high"
            next_task_id_on_success="first_route"
        )
        workflow.add_task(first_decision)
        
        # First conditional route
        first_conditional = ConditionalTask(
            task_id="first_route",
            name="First Route",
            conditions=[
                {
                    "condition": "${first_decision.output_data.result == 'high'}",
                    "next_task_id": "high_case"
                },
                {
                    "condition": "${first_decision.output_data.result != 'high'}",
                    "next_task_id": "not_high_case"
                }
            ],
            default_task_id="default_case"
        )
        workflow.add_task(first_conditional)
        
        # High case leads to another decision
        high_case = Task(
            task_id="high_case",
            name="High Case",
            tool_name="decision_tool",
            input_data={"value": 3},  # Should return "low"
            next_task_id_on_success="second_route"
        )
        workflow.add_task(high_case)
        
        # Not high case (we won't reach this in the test)
        not_high_case = Task(
            task_id="not_high_case",
            name="Not High Case",
            tool_name="process_tool",
            input_data={"category": "not_high"}
        )
        workflow.add_task(not_high_case)
        
        # Default case (we won't reach this in the test)
        default_case = Task(
            task_id="default_case",
            name="Default Case",
            tool_name="process_tool",
            input_data={"category": "default"}
        )
        workflow.add_task(default_case)
        
        # Second conditional based on the high case result
        second_conditional = ConditionalTask(
            task_id="second_route",
            name="Second Route",
            conditions=[
                {
                    "condition": "${high_case.output_data.result == 'low' and high_case.output_data.is_valid == false}",
                    "next_task_id": "low_invalid_process"
                },
                {
                    "condition": "${high_case.output_data.result == 'low' and high_case.output_data.is_valid == true}",
                    "next_task_id": "low_valid_process"
                },
                {
                    "condition": "${high_case.output_data.result != 'low'}",
                    "next_task_id": "not_low_process"
                }
            ],
            default_task_id="second_default"
        )
        workflow.add_task(second_conditional)
        
        # Final processing tasks
        for path in ["low_invalid", "low_valid", "not_low", "second_default"]:
            process_task = Task(
                task_id=f"{path}_process",
                name=f"Process {path.capitalize()}",
                tool_name="process_tool",
                input_data={
                    "category": path
                }
            )
            workflow.add_task(process_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check the execution path
        executed_tasks = self.harness.get_executed_tasks()
        
        # First branch should go to high_case
        self.assertIn("first_decision", executed_tasks)
        self.assertIn("first_route", executed_tasks)
        self.assertIn("high_case", executed_tasks)
        self.assertNotIn("not_high_case", executed_tasks)
        self.assertNotIn("default_case", executed_tasks)
        
        # Second branch should go to low_invalid_process
        self.assertIn("second_route", executed_tasks)
        self.assertIn("low_invalid_process", executed_tasks)
        self.assertNotIn("low_valid_process", executed_tasks)
        self.assertNotIn("not_low_process", executed_tasks)
        self.assertNotIn("second_default", executed_tasks)

    def test_dynamic_condition_based_on_workflow_variables(self):
        """Test conditional routing using dynamically calculated variables."""
        workflow = Workflow(workflow_id="dynamic_conditional", name="Dynamic Conditional")
        
        # Set initial workflow variables
        workflow.variables = {
            "threshold": 8,
            "strict_mode": True
        }
        
        # Task 1: Make a decision
        decision_task = Task(
            task_id="make_decision",
            name="Make Decision",
            tool_name="decision_tool",
            input_data={"value": 7},  # Medium
            next_task_id_on_success="dynamic_route"
        )
        workflow.add_task(decision_task)
        
        # Conditional based on workflow variables
        dynamic_conditional = ConditionalTask(
            task_id="dynamic_route",
            name="Dynamic Route",
            conditions=[
                {
                    # Compare value directly with dynamic threshold
                    "condition": "${int(make_decision.output_data.value) > workflow.variables.threshold}",
                    "next_task_id": "above_threshold"
                },
                {
                    # Use strict mode flag in conjunction with another condition
                    "condition": "${workflow.variables.strict_mode == true and make_decision.output_data.is_valid == false}",
                    "next_task_id": "strict_invalid"
                },
                {
                    # Compare result against dynamic variable - we want to show this can be done
                    # even though it's not the cleanest way to structure it
                    "condition": "${make_decision.output_data.result == (workflow.variables.threshold > 7 ? 'high' : 'medium')}",
                    "next_task_id": "threshold_based_result"
                }
            ],
            default_task_id="fallback_process"
        )
        workflow.add_task(dynamic_conditional)
        
        # Process tasks
        for path in ["above_threshold", "strict_invalid", "threshold_based_result", "fallback_process"]:
            process_task = Task(
                task_id=path,
                name=f"Process {path.replace('_', ' ').title()}",
                tool_name="process_tool",
                input_data={
                    "category": path
                }
            )
            workflow.add_task(process_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # With threshold=8, value=7, strict_mode=True, and is_valid=False (from low/medium value),
        # the strict_invalid condition should be met
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("strict_invalid", executed_tasks)
        self.assertNotIn("above_threshold", executed_tasks)
        self.assertNotIn("threshold_based_result", executed_tasks)
        self.assertNotIn("fallback_process", executed_tasks)

    def test_default_branch(self):
        """Test that the default branch is taken when no conditions match."""
        workflow = Workflow(workflow_id="default_branch", name="Default Branch")
        
        # Task 1: Make a decision
        decision_task = Task(
            task_id="make_decision",
            name="Make Decision",
            tool_name="decision_tool",
            input_data={"value": 7},  # Returns "medium"
            next_task_id_on_success="no_match_route"
        )
        workflow.add_task(decision_task)
        
        # Conditional with no matching conditions
        no_match_conditional = ConditionalTask(
            task_id="no_match_route",
            name="No Match Route",
            conditions=[
                {
                    "condition": "${make_decision.output_data.result == 'very_high'}",
                    "next_task_id": "very_high_process"
                },
                {
                    "condition": "${make_decision.output_data.result == 'very_low'}",
                    "next_task_id": "very_low_process"
                }
            ],
            default_task_id="default_handler"
        )
        workflow.add_task(no_match_conditional)
        
        # Process tasks
        for path in ["very_high_process", "very_low_process", "default_handler"]:
            process_task = Task(
                task_id=path,
                name=f"Process {path.replace('_', ' ').title()}",
                tool_name="process_tool",
                input_data={
                    "category": path
                }
            )
            workflow.add_task(process_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that default handler was executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("default_handler", executed_tasks)
        self.assertNotIn("very_high_process", executed_tasks)
        self.assertNotIn("very_low_process", executed_tasks)

    def test_condition_evaluation_with_invalid_expression(self):
        """Test how the workflow handles invalid conditional expressions."""
        workflow = Workflow(workflow_id="invalid_condition", name="Invalid Condition")
        
        # Task 1: Make a decision
        decision_task = Task(
            task_id="make_decision",
            name="Make Decision",
            tool_name="decision_tool",
            input_data={"value": 15},  # Returns "high"
            next_task_id_on_success="bad_condition_route"
        )
        workflow.add_task(decision_task)
        
        # Conditional with invalid expressions
        bad_conditional = ConditionalTask(
            task_id="bad_condition_route",
            name="Bad Condition Route",
            conditions=[
                {
                    # Invalid syntax in expression
                    "condition": "${make_decision.output_data.result = 'high'}",  # Missing "="
                    "next_task_id": "syntax_error_handler"
                },
                {
                    # Valid condition that should match if first one fails
                    "condition": "${make_decision.output_data.result == 'high'}",
                    "next_task_id": "valid_condition_handler"
                }
            ],
            default_task_id="default_error_handler",
            next_task_id_on_error="expression_error_handler"
        )
        workflow.add_task(bad_conditional)
        
        # Add possible handlers
        for path in ["syntax_error_handler", "valid_condition_handler", 
                     "default_error_handler", "expression_error_handler"]:
            handler_task = Task(
                task_id=path,
                name=f"{path.replace('_', ' ').title()}",
                tool_name="process_tool",
                input_data={
                    "category": path,
                    "error": "${error.bad_condition_route}"
                }
            )
            workflow.add_task(handler_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Workflow should still complete
        self.assertTrue(result.get("success", False))
        
        # On invalid syntax, should either go to the second valid condition
        # or the error handler depending on how the workflow engine is implemented
        executed_tasks = self.harness.get_executed_tasks()
        
        # It should NOT execute the invalid condition's handler
        self.assertNotIn("syntax_error_handler", executed_tasks)
        
        # It should have either gone to the valid handler or the error handler
        # Both outcomes are reasonable depending on how the engine handles evaluation errors
        valid_path_taken = "valid_condition_handler" in executed_tasks
        error_path_taken = "expression_error_handler" in executed_tasks
        
        self.assertTrue(valid_path_taken or error_path_taken, 
                        "Neither valid condition nor error handler was executed")
        
        # Default should not be taken if there's a valid condition or error handler
        if valid_path_taken or error_path_taken:
            self.assertNotIn("default_error_handler", executed_tasks)


if __name__ == "__main__":
    unittest.main() 