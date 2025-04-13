#!/usr/bin/env python3
"""
Simple test for execute_dynamic_tasks_handler function.
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_dynamic_tasks")

def main():
    """Run a simple test of execute_dynamic_tasks_handler."""
    logger.info("Setting up test environment...")
    
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
    mock_search_tool = MagicMock(return_value={"success": True, "result": "Mock search results"})
    mock_summarize_handler = MagicMock(return_value={"success": True, "result": "Mock summary"})
    
    tool_registry.register_tool("mock_search", mock_search_tool)
    handler_registry.register_handler("mock_summarize", mock_summarize_handler)
    
    # Create mock task for passing to handler
    mock_task = MagicMock(spec=DirectHandlerTask)
    mock_task.id = "execute_dynamic_tasks"
    mock_task.name = "Execute Dynamic Tasks"
    
    # Sample task definitions that would be output from plan_to_tasks_handler
    sample_task_defs = [
        {
            "task_id": "search_task",
            "name": "Search Task",
            "tool_name": "mock_search",
            "input_data": {
                "query": "test query"
            },
            "depends_on": []
        },
        {
            "task_id": "summarize_task",
            "name": "Summarize Task",
            "handler_name": "mock_summarize",
            "task_class": "DirectHandlerTask",
            "input_data": {
                "text": "${search_task.output.result}"
            },
            "depends_on": ["search_task"]
        }
    ]
    
    # Test 1: Test with normal task list
    logger.info("Test 1: Execute with normal task list")
    result1 = execute_dynamic_tasks_handler(
        mock_task,
        {"tasks": sample_task_defs}
    )
    logger.info(f"Result 1: {result1}\n")
    
    # Test 2: Test with empty task list
    logger.info("Test 2: Execute with empty task list")
    result2 = execute_dynamic_tasks_handler(
        mock_task,
        {"tasks": []}
    )
    logger.info(f"Result 2: {result2}\n")
    
    # Test 3: Test with missing input
    logger.info("Test 3: Execute with missing input")
    result3 = execute_dynamic_tasks_handler(
        mock_task,
        {}
    )
    logger.info(f"Result 3: {result3}\n")
    
    # Test 4: Test variable substitution with more complex variables
    logger.info("Test 4: Test variable substitution")
    # Create task definitions with variable references that need to be resolved
    var_tasks = [
        {
            "task_id": "data_task",
            "name": "Data Task",
            "tool_name": "mock_search",
            "input_data": {
                "query": "${user_prompt}"  # Reference to user input
            },
            "depends_on": []
        },
        {
            "task_id": "process_task",
            "name": "Process Task",
            "handler_name": "mock_summarize",
            "task_class": "DirectHandlerTask",
            "input_data": {
                "text": "${data_task.output.result}"  # Reference to previous task output
            },
            "depends_on": ["data_task"]
        }
    ]
    
    result4 = execute_dynamic_tasks_handler(
        mock_task,
        {
            "tasks": var_tasks,
            "user_prompt": "User's original request"  # Provide user input for substitution
        }
    )
    logger.info(f"Result 4: {result4}\n")
    
    logger.info("All tests completed")

if __name__ == "__main__":
    main() 