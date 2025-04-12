#!/usr/bin/env python3
"""
Script to demonstrate how to run workflow tests.

This script runs the example workflow tests to demonstrate the workflow testing utilities.
"""  # noqa: D202

import sys
import os
import unittest

# Add the project root to the Python path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create test suite
suite = unittest.TestSuite()

# Define run_tests function outside the try block to avoid scope issues
def run_tests():
    try:
        # Import the test cases with their new names
        from tests.workflows.examples.test_workflow_examples import TestWorkflowExamplesClass, TestTaskExamplesClass
        
        print("Running workflow and task tests...")
        
        # Add workflow test cases with updated class names
        suite.addTest(unittest.makeSuite(TestWorkflowExamplesClass))
        
        # Add task test cases with updated class names
        suite.addTest(unittest.makeSuite(TestTaskExamplesClass))
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print("\nTest Summary:")
        print(f"  Ran {result.testsRun} tests")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        
        if result.failures or result.errors:
            print("\nDetailed failure information:")
            for failure in result.failures:
                print(f"\nFAILURE: {failure[0]}")
                print(f"{failure[1]}")
            
            for error in result.errors:
                print(f"\nERROR: {error[0]}")
                print(f"{error[1]}")
        
        return len(result.failures) + len(result.errors)
        
    except ImportError as e:
        # Handle import errors gracefully
        print(f"Error importing test modules: {e}")
        print("This may be due to incompatible module structure.")
        print("Please check the following:")
        print("1. Ensure all __init__.py files are in place in the test directories")
        print("2. Check that the imports in core/utils/testing.py match the actual module structure")
        print("3. Verify that all necessary dependencies are installed")
        print("\nTest Summary:")
        print("  Ran 0 tests")
        print("  Failures: 0")
        print("  Errors: 1")
        return 1  # Return error code


if __name__ == "__main__":
    sys.exit(run_tests()) 