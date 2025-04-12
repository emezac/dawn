#!/usr/bin/env python3
"""
Script to run individual test files with detailed error reporting.

This script allows running a single test file or a specific test case within a file,
with better error reporting and diagnostic output.
"""  # noqa: D202

import os
import sys
import unittest
import importlib.util
import traceback
from pathlib import Path

def run_test_file(file_path):
    """
    Run a single test file and report detailed results.
    
    Args:
        file_path: Path to the test file
        
    Returns:
        True if all tests passed, False otherwise
    """
    print(f"\n{'='*80}")
    print(f"Running test file: {file_path}")
    print(f"{'='*80}")
    
    try:
        # Ensure the file exists
        if not os.path.exists(file_path):
            print(f"ERROR: Test file {file_path} does not exist")
            return False
            
        # Load the module
        module_name = os.path.basename(file_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Print the test classes found
        test_classes = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, unittest.TestCase) and attr != unittest.TestCase:
                test_classes.append(attr)
                print(f"Found test class: {attr.__name__}")
                print(f"  Test methods:")
                # List test methods
                for method_name in dir(attr):
                    if method_name.startswith("test_"):
                        print(f"    - {method_name}")
        
        if not test_classes:
            print(f"WARNING: No test classes found in {file_path}")
            return False
        
        # Discover tests in the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Report detailed results
        tests_run = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        
        print(f"\nSummary for {file_path}:")
        print(f"  Ran {tests_run} tests")
        print(f"  Failures: {failures}")
        print(f"  Errors: {errors}")
        
        if failures > 0 or errors > 0:
            print("\nDetailed failure and error information:")
            
            for i, (test, error) in enumerate(result.failures):
                print(f"\nFAILURE {i+1}: {test}")
                print(f"{'-'*60}")
                print(error)
            
            for i, (test, error) in enumerate(result.errors):
                print(f"\nERROR {i+1}: {test}")
                print(f"{'-'*60}")
                print(error)
            
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR running {file_path}: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run the specified test file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up Python path
    sys.path.insert(0, script_dir)
    
    if len(sys.argv) < 2:
        print("USAGE: python run_individual_test.py <test_file_path> [<test_class>.<test_method>]")
        print("Example: python run_individual_test.py tests/core/test_direct_handler_task.py")
        print("Example: python run_individual_test.py tests/core/test_direct_handler_task.py TestDirectHandlerTask.test_init")
        return 1
    
    # Get the test file path
    test_file = sys.argv[1]
    
    # If it's a relative path, make it absolute
    if not os.path.isabs(test_file):
        test_file = os.path.join(script_dir, test_file)
    
    # Run the test file
    success = run_test_file(test_file)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 