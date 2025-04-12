#!/usr/bin/env python3
"""Script to run a single test file."""  # noqa: D202

import os
import sys
import importlib.util
import unittest
import traceback

def run_test_file(file_path):
    """Run a single test file."""
    print(f"Running test file: {file_path}")
    
    try:
        # Add the Dawn codebase to the Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Load the module
        spec = importlib.util.spec_from_file_location("test_module", file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["test_module"] = module
        spec.loader.exec_module(module)
        
        # Discover tests in the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print(f"\nRan {result.testsRun} tests")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        # Return exit code based on success
        return 0 if len(result.failures) == 0 and len(result.errors) == 0 else 1
        
    except Exception as e:
        print(f"Error running test file: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_one_test.py <test_file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    sys.exit(run_test_file(file_path)) 