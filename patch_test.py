#!/usr/bin/env python3
"""
Test script that patches the ChatPlannerConfig.get_max_clarifications method
to ensure it returns an integer.
"""  # noqa: D202

import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import json

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class TestPlanUserRequestHandler(unittest.TestCase):
    """Test class for plan_user_request_handler."""  # noqa: D202
    
    @patch('examples.chat_planner_config.ChatPlannerConfig.get_max_clarifications')
    @patch('examples.chat_planner_config.ChatPlannerConfig.get_prompt')
    @patch('examples.chat_planner_config.ChatPlannerConfig.get_planning_system_message')
    def test_plan_user_request_handler(self, mock_get_system_message, mock_get_prompt, mock_get_max_clarifications):
        """Test plan_user_request_handler with patched methods."""
        # Set up mocks
        mock_get_max_clarifications.return_value = 3
        mock_get_prompt.return_value = "Create a plan for: {user_request}"
        mock_get_system_message.return_value = "You are a planning assistant."
        
        # Import after patching
        from examples.chat_planner_workflow import plan_user_request_handler
        from core.task import DirectHandlerTask
        from core.services import get_services, reset_services
        from core.llm.interface import LLMInterface
        
        # Reset services
        reset_services()
        services = get_services()
        
        # Create mock LLM interface
        mock_llm = MagicMock(spec=LLMInterface)
        mock_llm.execute_llm_call.return_value = {
            "success": True,
            "response": "[]"
        }
        services.register_llm_interface(mock_llm)
        
        # Create mock task
        mock_task = MagicMock(spec=DirectHandlerTask)
        mock_task.id = "test_task"
        
        # Test the function
        result = plan_user_request_handler(
            mock_task, 
            {
                "user_request": "Test request",
                "skip_ambiguity_check": True,
                "available_tools_context": json.dumps([]),
                "available_handlers_context": json.dumps([])
            }
        )
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertEqual(result["result"]["needs_clarification"], False)
        

if __name__ == "__main__":
    unittest.main() 