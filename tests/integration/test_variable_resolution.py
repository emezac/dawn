#!/usr/bin/env python3
"""
Integration Tests for Variable Resolution in Workflows

This module tests the variable resolution capabilities of the Dawn workflow engine,
verifying that workflow variables are correctly resolved, propagated between tasks,
and handled properly in various scenarios.
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
from core.task import Task
from core.engine import WorkflowEngine
from core.utils.testing import MockToolRegistry, WorkflowTestHarness
from core.variables import VariableResolutionError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestVariableResolution(unittest.TestCase):
    """Test suite for variable resolution in workflows."""  # noqa: D202

    def setUp(self):
        """Set up the test environment."""
        # Create a clean test harness
        self.harness = WorkflowTestHarness()
        
        # Register tools for testing
        def generate_data_tool(input_data):
            """Tool that generates data based on input parameters."""
            data_type = input_data.get("type", "default")
            count = input_data.get("count", 1)
            
            if data_type == "user":
                return {
                    "success": True,
                    "data": [
                        {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"}
                        for i in range(1, count + 1)
                    ]
                }
            elif data_type == "product":
                return {
                    "success": True,
                    "data": [
                        {"id": i, "name": f"Product {i}", "price": i * 10.0}
                        for i in range(1, count + 1)
                    ]
                }
            else:
                return {
                    "success": True,
                    "data": [{"id": i, "value": f"Item {i}"} for i in range(1, count + 1)]
                }
        
        def process_data_tool(input_data):
            """Tool that processes data and returns results."""
            data = input_data.get("data", [])
            operation = input_data.get("operation", "count")
            
            if operation == "count":
                return {
                    "success": True,
                    "result": len(data),
                    "summary": f"Processed {len(data)} items"
                }
            elif operation == "sum":
                try:
                    total = sum(item.get("price", 0) for item in data)
                    return {
                        "success": True,
                        "result": total,
                        "summary": f"Total sum: {total}"
                    }
                except (TypeError, KeyError):
                    return {
                        "success": False,
                        "error": "Unable to sum data, missing price field"
                    }
            elif operation == "transform":
                try:
                    transformed = [
                        {
                            "item_id": item.get("id", 0),
                            "display_name": item.get("name", "Unknown"),
                            "metadata": {
                                "email": item.get("email", ""),
                                "price": item.get("price", 0)
                            }
                        }
                        for item in data
                    ]
                    return {
                        "success": True,
                        "result": transformed,
                        "summary": f"Transformed {len(transformed)} items"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Transform failed: {str(e)}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
                
        def format_result_tool(input_data):
            """Tool that formats results for presentation."""
            result = input_data.get("result", None)
            format_type = input_data.get("format", "text")
            title = input_data.get("title", "Result")
            
            if format_type == "json":
                try:
                    return {
                        "success": True,
                        "formatted_result": json.dumps(result, indent=2),
                        "content_type": "application/json"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"JSON formatting failed: {str(e)}"
                    }
            elif format_type == "html":
                if isinstance(result, list):
                    try:
                        html = f"<h1>{title}</h1><ul>"
                        for item in result:
                            html += f"<li>{item}</li>"
                        html += "</ul>"
                        return {
                            "success": True,
                            "formatted_result": html,
                            "content_type": "text/html"
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"HTML formatting failed: {str(e)}"
                        }
                else:
                    return {
                        "success": True,
                        "formatted_result": f"<h1>{title}</h1><p>{result}</p>",
                        "content_type": "text/html"
                    }
            else:  # text
                return {
                    "success": True,
                    "formatted_result": f"{title}: {result}",
                    "content_type": "text/plain"
                }
                
        # Register the tools
        self.harness.register_mock_tool("generate_data_tool", generate_data_tool)
        self.harness.register_mock_tool("process_data_tool", process_data_tool)
        self.harness.register_mock_tool("format_result_tool", format_result_tool)
        
    def test_basic_variable_resolution(self):
        """Test basic variable resolution between tasks."""
        workflow = Workflow(workflow_id="basic_variable_test", name="Basic Variable Resolution Test")
        
        # Task 1: Generate user data
        generate_task = Task(
            task_id="generate_users",
            name="Generate Users",
            tool_name="generate_data_tool",
            input_data={
                "type": "user",
                "count": 3
            },
            next_task_id_on_success="process_users"
        )
        workflow.add_task(generate_task)
        
        # Task 2: Process the user data (using variable from previous task)
        process_task = Task(
            task_id="process_users",
            name="Process Users",
            tool_name="process_data_tool",
            input_data={
                "data": "${generate_users.output_data.data}",
                "operation": "count"
            },
            next_task_id_on_success="format_results"
        )
        workflow.add_task(process_task)
        
        # Task 3: Format the results (using variable from previous task)
        format_task = Task(
            task_id="format_results",
            name="Format Results",
            tool_name="format_result_tool",
            input_data={
                "result": "${process_users.output_data.result}",
                "title": "User Count",
                "format": "text"
            }
        )
        workflow.add_task(format_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that all tasks were executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("generate_users", executed_tasks)
        self.assertIn("process_users", executed_tasks)
        self.assertIn("format_results", executed_tasks)
        
        # Verify the output of each task
        generate_task = self.harness.get_task("generate_users")
        self.assertEqual(len(generate_task.output_data.get("data", [])), 3)
        
        process_task = self.harness.get_task("process_users")
        self.assertEqual(process_task.output_data.get("result"), 3)
        
        format_task = self.harness.get_task("format_results")
        self.assertEqual(format_task.output_data.get("formatted_result"), "User Count: 3")
        self.assertEqual(format_task.output_data.get("content_type"), "text/plain")

    def test_nested_variable_resolution(self):
        """Test resolution of nested variables within complex data structures."""
        workflow = Workflow(workflow_id="nested_variables", name="Nested Variable Resolution")
        
        # Set initial workflow variables
        workflow.variables = {
            "config": {
                "data_source": "user",
                "options": {
                    "count": 2,
                    "format": "json"
                }
            },
            "default_title": "Data Processing Results"
        }
        
        # Task 1: Generate data using nested workflow variables
        generate_task = Task(
            task_id="generate_data",
            name="Generate Data",
            tool_name="generate_data_tool",
            input_data={
                "type": "${workflow.variables.config.data_source}",
                "count": "${workflow.variables.config.options.count}"
            },
            next_task_id_on_success="process_data"
        )
        workflow.add_task(generate_task)
        
        # Task 2: Process data with dynamically resolved operation
        process_task = Task(
            task_id="process_data",
            name="Process Data",
            tool_name="process_data_tool",
            input_data={
                "data": "${generate_data.output_data.data}",
                "operation": "transform"
            },
            next_task_id_on_success="format_output"
        )
        workflow.add_task(process_task)
        
        # Task 3: Format output using nested variable resolution
        format_task = Task(
            task_id="format_output",
            name="Format Output",
            tool_name="format_result_tool",
            input_data={
                "result": "${process_data.output_data.result}",
                "format": "${workflow.variables.config.options.format}",
                "title": "${workflow.variables.default_title}"
            }
        )
        workflow.add_task(format_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check the final formatted output
        format_task = self.harness.get_task("format_output")
        self.assertEqual(format_task.output_data.get("content_type"), "application/json")
        
        # Verify the nested structure was correctly passed through the workflow
        generate_task = self.harness.get_task("generate_data")
        self.assertEqual(generate_task.input_data.get("type"), "user")
        self.assertEqual(generate_task.input_data.get("count"), 2)
        
        # Verify transformation worked with the nested data
        process_task = self.harness.get_task("process_data")
        transformed_data = process_task.output_data.get("result", [])
        self.assertEqual(len(transformed_data), 2)
        self.assertIn("item_id", transformed_data[0])
        self.assertIn("display_name", transformed_data[0])
        self.assertIn("metadata", transformed_data[0])

    def test_variable_resolution_with_list_access(self):
        """Test accessing elements in lists through variable resolution."""
        workflow = Workflow(workflow_id="list_access", name="List Element Access")
        
        # Task 1: Generate product data
        generate_task = Task(
            task_id="generate_products",
            name="Generate Products",
            tool_name="generate_data_tool",
            input_data={
                "type": "product",
                "count": 3
            },
            next_task_id_on_success="access_first_product"
        )
        workflow.add_task(generate_task)
        
        # Task 2: Access the first product
        first_product_task = Task(
            task_id="access_first_product",
            name="Access First Product",
            tool_name="format_result_tool",
            input_data={
                "result": "${generate_products.output_data.data[0].name}",
                "title": "First Product",
                "format": "text"
            },
            next_task_id_on_success="access_last_product"
        )
        workflow.add_task(first_product_task)
        
        # Task 3: Access the last product
        last_product_task = Task(
            task_id="access_last_product",
            name="Access Last Product",
            tool_name="format_result_tool",
            input_data={
                "result": "${generate_products.output_data.data[2].price}",
                "title": "Last Product Price",
                "format": "text"
            },
            next_task_id_on_success="compute_total"
        )
        workflow.add_task(last_product_task)
        
        # Task 4: Compute total price
        compute_total_task = Task(
            task_id="compute_total",
            name="Compute Total Price",
            tool_name="process_data_tool",
            input_data={
                "data": "${generate_products.output_data.data}",
                "operation": "sum"
            }
        )
        workflow.add_task(compute_total_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check the results of list access
        first_product_task = self.harness.get_task("access_first_product")
        self.assertEqual(first_product_task.output_data.get("formatted_result"), "First Product: Product 1")
        
        last_product_task = self.harness.get_task("access_last_product")
        self.assertEqual(last_product_task.output_data.get("formatted_result"), "Last Product Price: 30.0")
        
        # Check the total computation
        compute_total_task = self.harness.get_task("compute_total")
        self.assertEqual(compute_total_task.output_data.get("result"), 60.0)  # 10 + 20 + 30

    def test_variable_resolution_with_default_values(self):
        """Test using default values for variables that might not be resolved."""
        workflow = Workflow(workflow_id="default_values", name="Default Value Resolution")
        
        # Task 1: Generate data with potential for missing fields
        generate_task = Task(
            task_id="generate_basic_data",
            name="Generate Basic Data",
            tool_name="generate_data_tool",
            input_data={
                "type": "default",
                "count": 1
            },
            next_task_id_on_success="process_with_defaults"
        )
        workflow.add_task(generate_task)
        
        # Task 2: Process with default values for potentially missing fields
        process_task = Task(
            task_id="process_with_defaults",
            name="Process With Defaults",
            tool_name="format_result_tool",
            input_data={
                # Default items will be used since these fields don't exist
                "result": "${generate_basic_data.output_data.data[0].name ?? 'Unknown Item'}",
                "title": "${generate_basic_data.output_data.title ?? 'Default Title'}",
                "format": "${generate_basic_data.output_data.preferred_format ?? 'text'}"
            }
        )
        workflow.add_task(process_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check that default values were used
        process_task = self.harness.get_task("process_with_defaults")
        self.assertEqual(process_task.output_data.get("formatted_result"), "Default Title: Unknown Item")
        self.assertEqual(process_task.output_data.get("content_type"), "text/plain")  # From default 'text'

    def test_variable_resolution_with_conditional_expressions(self):
        """Test variable resolution with conditional (ternary) expressions."""
        workflow = Workflow(workflow_id="conditional_expressions", name="Conditional Expressions")
        
        # Set initial workflow variables
        workflow.variables = {
            "premium_user": False,
            "admin_user": True
        }
        
        # Task 1: Generate data based on user type
        generate_task = Task(
            task_id="generate_conditional_data",
            name="Generate Conditional Data",
            tool_name="generate_data_tool",
            input_data={
                # Use ternary to determine data type
                "type": "${workflow.variables.premium_user ? 'product' : 'user'}",
                # Use ternary with another variable and a literal
                "count": "${workflow.variables.admin_user ? 5 : 2}"
            },
            next_task_id_on_success="format_conditional"
        )
        workflow.add_task(generate_task)
        
        # Task 2: Format with conditional title
        format_task = Task(
            task_id="format_conditional",
            name="Format With Conditional",
            tool_name="format_result_tool",
            input_data={
                "result": "${generate_conditional_data.output_data.data}",
                # Nested conditional
                "title": "${workflow.variables.premium_user ? 'Premium Content' : (workflow.variables.admin_user ? 'Admin View' : 'Basic View')}",
                # Conditional format
                "format": "${workflow.variables.admin_user ? 'json' : 'text'}"
            }
        )
        workflow.add_task(format_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check conditional resolutions
        generate_task = self.harness.get_task("generate_conditional_data")
        self.assertEqual(generate_task.input_data.get("type"), "user")  # premium_user is False
        self.assertEqual(generate_task.input_data.get("count"), 5)  # admin_user is True
        
        format_task = self.harness.get_task("format_conditional")
        self.assertEqual(format_task.input_data.get("title"), "Admin View")  # Nested conditional
        self.assertEqual(format_task.input_data.get("format"), "json")  # admin_user is True
        self.assertEqual(format_task.output_data.get("content_type"), "application/json")

    def test_handling_unresolvable_variables(self):
        """Test how the workflow engine handles unresolvable variables."""
        workflow = Workflow(workflow_id="unresolvable_vars", name="Unresolvable Variables")
        
        # Task 1: Generate data
        generate_task = Task(
            task_id="generate_simple_data",
            name="Generate Simple Data",
            tool_name="generate_data_tool",
            input_data={
                "type": "user",
                "count": 1
            },
            next_task_id_on_success="task_with_bad_vars",
            next_task_id_on_error="handle_generation_error"
        )
        workflow.add_task(generate_task)
        
        # Task 2: Try to use non-existent variables
        bad_var_task = Task(
            task_id="task_with_bad_vars",
            name="Task With Bad Variables",
            tool_name="format_result_tool",
            input_data={
                # This variable doesn't exist
                "result": "${non_existent_task.output_data.result}",
                "title": "Should Fail",
                "format": "text"
            },
            next_task_id_on_success="should_never_reach",
            next_task_id_on_error="handle_resolution_error"
        )
        workflow.add_task(bad_var_task)
        
        # Task 3a: Handle variable resolution error
        handle_error_task = Task(
            task_id="handle_resolution_error",
            name="Handle Resolution Error",
            tool_name="format_result_tool",
            input_data={
                "result": "Variable resolution failed as expected",
                "title": "Error Handler",
                "format": "text"
            }
        )
        workflow.add_task(handle_error_task)
        
        # Task 3b: Handle generation error (shouldn't be reached)
        handle_gen_error_task = Task(
            task_id="handle_generation_error",
            name="Handle Generation Error",
            tool_name="format_result_tool",
            input_data={
                "result": "Generation failed unexpectedly",
                "title": "Error",
                "format": "text"
            }
        )
        workflow.add_task(handle_gen_error_task)
        
        # Task 4: Should never reach this
        final_task = Task(
            task_id="should_never_reach",
            name="Should Never Reach",
            tool_name="format_result_tool",
            input_data={
                "result": "This should never be reached",
                "title": "Unexpected",
                "format": "text"
            }
        )
        workflow.add_task(final_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow still completed (even with errors)
        self.assertTrue(result.get("success", False))
        
        # Check that the error handler was executed
        executed_tasks = self.harness.get_executed_tasks()
        self.assertIn("generate_simple_data", executed_tasks)
        self.assertIn("task_with_bad_vars", executed_tasks)
        self.assertIn("handle_resolution_error", executed_tasks)
        self.assertNotIn("handle_generation_error", executed_tasks)
        self.assertNotIn("should_never_reach", executed_tasks)
        
        # Verify task status
        bad_var_task = self.harness.get_task("task_with_bad_vars")
        self.assertFalse(bad_var_task.success)
        self.assertIsNotNone(bad_var_task.error)
        self.assertIn("variable resolution", str(bad_var_task.error).lower())

    def test_workflow_variable_updates(self):
        """Test updating workflow variables during execution."""
        workflow = Workflow(workflow_id="variable_updates", name="Variable Updates")
        
        # Initial workflow variables
        workflow.variables = {
            "count": 3,
            "processed": False,
            "results": []
        }
        
        # Task 1: Generate data
        generate_task = Task(
            task_id="generate_update_data",
            name="Generate Data for Updates",
            tool_name="generate_data_tool",
            input_data={
                "type": "product",
                "count": "${workflow.variables.count}"
            },
            # Update workflow variables with task output
            workflow_variable_updates={
                "data": "${output_data.data}",
                "generated": True
            },
            next_task_id_on_success="process_update_data"
        )
        workflow.add_task(generate_task)
        
        # Task 2: Process data and update variables
        process_task = Task(
            task_id="process_update_data",
            name="Process Updated Data",
            tool_name="process_data_tool",
            input_data={
                "data": "${workflow.variables.data}",
                "operation": "sum"
            },
            # Update workflow variables with task output
            workflow_variable_updates={
                "processed": True,
                "total": "${output_data.result}",
                "results": "${array_append(workflow.variables.results, output_data.result)}"
            },
            next_task_id_on_success="format_with_updates"
        )
        workflow.add_task(process_task)
        
        # Task 3: Format results using updated variables
        format_task = Task(
            task_id="format_with_updates",
            name="Format With Updates",
            tool_name="format_result_tool",
            input_data={
                "result": {
                    "total": "${workflow.variables.total}",
                    "processed": "${workflow.variables.processed}",
                    "results": "${workflow.variables.results}",
                    "count": "${workflow.variables.count}"
                },
                "title": "Updated Variables",
                "format": "json"
            }
        )
        workflow.add_task(format_task)
        
        # Run the workflow
        result = self.harness.run_workflow(workflow)
        
        # Verify workflow completed successfully
        self.assertTrue(result.get("success", False))
        
        # Check the final task's input to verify variable updates
        format_task = self.harness.get_task("format_with_updates")
        input_result = format_task.input_data.get("result", {})
        
        self.assertEqual(input_result.get("total"), 60)  # Sum of 10+20+30
        self.assertTrue(input_result.get("processed"))
        self.assertEqual(input_result.get("results"), [60])  # Added to the results array
        self.assertEqual(input_result.get("count"), 3)  # Original variable unchanged
        
        # Verify the workflow variables directly
        self.assertEqual(workflow.variables.get("total"), 60)
        self.assertTrue(workflow.variables.get("processed"))
        self.assertEqual(workflow.variables.get("results"), [60])
        self.assertTrue(workflow.variables.get("generated"))
        self.assertEqual(len(workflow.variables.get("data")), 3)


if __name__ == "__main__":
    unittest.main() 