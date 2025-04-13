#!/usr/bin/env python3
"""
Edge case test for execute_dynamic_tasks_handler.

This script tests various edge cases in the execute_dynamic_tasks_handler
to verify robustness of the implementation.
"""  # noqa: D202

import sys
import os
import logging
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Import the handler to test
from examples.chat_planner_workflow import execute_dynamic_tasks_handler

# Import other needed modules
from core.task import DirectHandlerTask
from core.services import get_services, reset_services
from core.tools.registry import ToolRegistry
from core.handlers.registry import HandlerRegistry

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("edge_case_test")

def test_edge_cases():
    """Test edge cases for execute_dynamic_tasks_handler."""
    logger.info("=== Setting up test environment ===")
    
    # Reset services before test
    reset_services()
    services = get_services()
    
    # Create and register tool registry with mock tools
    tool_registry = ToolRegistry()
    services.register_tool_registry(tool_registry)
    
    # Create and register handler registry with mock handlers
    handler_registry = HandlerRegistry()
    services.register_handler_registry(handler_registry)
    
    # Register mock tools and handlers
    mock_tool = MagicMock(return_value={"success": True, "result": "Tool result"})
    mock_handler = MagicMock(return_value={"success": True, "result": "Handler result"})
    
    tool_registry.register_tool("mock_tool", mock_tool)
    handler_registry.register_handler("mock_handler", mock_handler)
    
    # Create mock task for passing to handler
    mock_task = MagicMock(spec=DirectHandlerTask)
    mock_task.id = "execute_dynamic_tasks"
    mock_task.name = "Execute Dynamic Tasks"
    
    # Test cases
    test_cases = [
        {
            "name": "None input_data",
            "input_data": None,
            "expected_success": True,
            "expected_message": "No tasks to execute"
        },
        {
            "name": "Empty input_data",
            "input_data": {},
            "expected_success": True,
            "expected_message": "No tasks to execute"
        },
        {
            "name": "Empty task list",
            "input_data": {"tasks": []},
            "expected_success": True,
            "expected_message": "No tasks to execute"
        },
        {
            "name": "Non-dict task definition",
            "input_data": {"tasks": ["not a dict"]},
            "expected_success": True,
            "expected_outputs": []
        },
        {
            "name": "Invalid task (no capability)",
            "input_data": {"tasks": [{"task_id": "invalid_task", "name": "Invalid Task"}]},
            "expected_success": False,
            "expected_error": "No tool_name or handler_name specified"
        },
        {
            "name": "Invalid variable reference (non-existent task)",
            "input_data": {
                "tasks": [
                    {
                        "task_id": "task_with_bad_ref",
                        "name": "Task With Bad Reference",
                        "tool_name": "mock_tool",
                        "input_data": {
                            "param": "${nonexistent_task.output.result}"
                        }
                    }
                ]
            },
            "expected_success": True,
            "expected_outputs": [{"success": True}]
        },
        {
            "name": "Invalid variable reference (bad path)",
            "input_data": {
                "tasks": [
                    {
                        "task_id": "tool_task",
                        "name": "Tool Task",
                        "tool_name": "mock_tool",
                        "input_data": {"param": "value"}
                    },
                    {
                        "task_id": "task_with_bad_path",
                        "name": "Task With Bad Path",
                        "handler_name": "mock_handler",
                        "task_class": "DirectHandlerTask",
                        "input_data": {
                            "param": "${tool_task.output.nonexistent.path}"
                        },
                        "depends_on": ["tool_task"]
                    }
                ]
            },
            "expected_success": True,
            "expected_outputs": [{"success": True}, {"success": True}]
        },
        {
            "name": "Invalid task type",
            "input_data": {
                "tasks": [
                    {
                        "task_id": "invalid_type_task",
                        "name": "Invalid Type Task",
                        "type": "unknown_type",
                        "tool_name": "mock_tool",
                        "input_data": {"param": "value"}
                    }
                ]
            },
            "expected_success": False,
            "expected_error": "Unsupported task type"
        },
        {
            "name": "Valid task with user_prompt reference",
            "input_data": {
                "tasks": [
                    {
                        "task_id": "prompt_task",
                        "name": "Prompt Task",
                        "tool_name": "mock_tool",
                        "input_data": {
                            "param": "${user_prompt}"
                        }
                    }
                ],
                "user_prompt": "Test user prompt"
            },
            "expected_success": True,
            "expected_outputs": [{"success": True}]
        }
    ]
    
    # Run the test cases
    for i, test_case in enumerate(test_cases):
        logger.info(f"\n=== Test Case {i+1}: {test_case['name']} ===")
        
        try:
            # Reset mock call counts
            mock_tool.reset_mock()
            mock_handler.reset_mock()
            
            # Execute handler
            result = execute_dynamic_tasks_handler(mock_task, test_case["input_data"])
            
            # Validate result
            logger.info(f"Result: {result}")
            
            if "expected_success" in test_case:
                success_matches = result["success"] == test_case["expected_success"]
                logger.info(f"Success matches expected: {success_matches}")
                
            if "expected_message" in test_case and "message" in result.get("result", {}):
                message_matches = test_case["expected_message"] in result["result"]["message"]
                logger.info(f"Message matches expected: {message_matches}")
                
            if "expected_error" in test_case:
                # Check if error message is in any of the outputs
                error_found = False
                for output in result.get("result", {}).get("outputs", []):
                    if "error" in output and test_case["expected_error"] in output["error"]:
                        error_found = True
                        break
                logger.info(f"Error message found as expected: {error_found}")
                
            if "expected_outputs" in test_case:
                outputs_match = len(result.get("result", {}).get("outputs", [])) == len(test_case["expected_outputs"])
                logger.info(f"Number of outputs matches expected: {outputs_match}")
                
                # Check success status of each output
                for i, expected_output in enumerate(test_case["expected_outputs"]):
                    if i < len(result.get("result", {}).get("outputs", [])):
                        actual_output = result["result"]["outputs"][i]
                        success_match = actual_output.get("success") == expected_output.get("success")
                        logger.info(f"Output {i} success matches expected: {success_match}")
            
            # Test case specific checks
            if test_case["name"] == "Valid task with user_prompt reference":
                if mock_tool.called:
                    # Check that the user_prompt was passed correctly
                    args, kwargs = mock_tool.call_args
                    if "param" in args[0] and args[0]["param"] == "Test user prompt":
                        logger.info("User prompt correctly substituted in input")
                    else:
                        logger.error(f"User prompt not correctly substituted: {args}")
            
        except Exception as e:
            logger.exception(f"Error during test case: {e}")
    
    logger.info("\n=== All test cases completed ===")

if __name__ == "__main__":
    test_edge_cases() 