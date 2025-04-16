#!/usr/bin/env python3
"""
Run tests with mock modules to avoid external dependencies like PyYAML.

This script sets up mock modules for testing and runs specific test files.
"""  # noqa: D202

import sys
import os
import unittest
import importlib
from unittest.mock import MagicMock

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create mock yaml module
mock_yaml = MagicMock()
mock_yaml.safe_load = lambda f: {}
mock_yaml.dump = lambda data, f: None

# Register the mock in sys.modules
sys.modules['yaml'] = mock_yaml

# Use our test version of config
sys.path.insert(0, os.path.join(project_root, 'tests', 'core', 'mocks'))

def run_test_file(test_file_path):
    """Run a single test file with proper setup."""
    print(f"\nRunning {test_file_path}...")
    
    # Use unittest discovery to run the tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(test_file_path), 
                                      pattern=os.path.basename(test_file_path))
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return True if tests passed
    return result.wasSuccessful()

def main():
    """Main function to run the tests."""
    print("Running tests with mock modules...")
    
    success = True
    
    # Test files that need special handling due to yaml dependency
    test_files = [
        "tests/core/test_plan_validation.py",
        "tests/core/test_chat_planner_handlers.py"
    ]
    
    for test_file in test_files:
        file_success = run_test_file(test_file)
        if not file_success:
            success = False
    
    if success:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 