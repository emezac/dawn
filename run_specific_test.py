#!/usr/bin/env python3

import unittest
import sys

if __name__ == "__main__":
    from tests.core.test_chat_planner_handlers import TestChatPlannerHandlers
    
    # Create a test suite with just the specific test
    suite = unittest.TestSuite()
    suite.addTest(TestChatPlannerHandlers('test_validate_plan_handler_capability_check'))
    
    # Run the test
    result = unittest.TextTestRunner().run(suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful()) 