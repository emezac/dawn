#!/usr/bin/env python3
import sys
import os
import unittest

def run_tests(test_path):
    """Run a specific test module or test case."""
    # Add project root to sys.path if needed
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Load and run the tests
    test_suite = unittest.defaultTestLoader.loadTestsFromName(test_path)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    # Return non-zero exit code if tests failed
    if result.failures or result.errors:
        return 1
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_runner.py <test_module_or_case>")
        print("Example: python test_runner.py tests.core.test_direct_handler_task")
        print("Example: python test_runner.py tests.core.test_direct_handler_task.TestWorkflowEngineWithDirectHandler.test_run_workflow_with_mixed_tasks")
        sys.exit(1)
    
    test_path = sys.argv[1]
    sys.exit(run_tests(test_path)) 