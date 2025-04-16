#!/usr/bin/env python3
"""
Simple test script to verify the max_clarifications fix.
"""  # noqa: D202

import sys
import os
import logging
from unittest.mock import MagicMock, patch

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("simple_test")

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create a proper mock that returns integer 3 for get_max_clarifications
chat_planner_config_mock = MagicMock()
chat_planner_config_mock.get_max_clarifications.return_value = 3

# Patch the module
sys.modules['examples.chat_planner_config'] = MagicMock()
sys.modules['examples.chat_planner_config'].ChatPlannerConfig = chat_planner_config_mock

# Test the function
try:
    # Import after patching
    from examples.chat_planner_workflow import plan_user_request_handler
    from core.task import DirectHandlerTask
    from core.services import get_services, reset_services
    
    # Create minimal test setup
    reset_services()
    mock_task = MagicMock(spec=DirectHandlerTask)
    mock_task.id = "test_task"
    
    # Test just the problematic part
    result = plan_user_request_handler(
        mock_task, 
        {
            "user_request": "Test request",
            "skip_ambiguity_check": True
        }
    )
    
    if "success" in result:
        logger.info("Test completed!")
    else:
        logger.error(f"Test failed with error: {result.get('error')}")
        
except Exception as e:
    logger.error(f"Error in test: {str(e)}", exc_info=True) 