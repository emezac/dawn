#!/usr/bin/env python3
"""
Test runner script for core tests.

This script runs individual test files in the tests/core directory
with proper error handling to identify failures without interrupting the process.
"""  # noqa: D202

import os
import sys
import unittest
import importlib.util
import traceback
from pathlib import Path

def run_test_file(file_path):
    """
    Run a single test file and report results.
    
    Args:
        file_path: Path to the test file
        
    Returns:
        Tuple of (success, error_message)
    """
    print(f"\n{'='*80}")
    print(f"Running test file: {file_path}")
    print(f"{'='*80}")
    
    try:
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
        
        # Report results
        tests_run = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        
        print(f"\nSummary for {file_path}:")
        print(f"  Ran {tests_run} tests")
        print(f"  Failures: {failures}")
        print(f"  Errors: {errors}")
        
        if failures > 0 or errors > 0:
            error_messages = []
            
            for test, error in result.failures:
                error_messages.append(f"FAILURE: {test}\n{error}")
                
            for test, error in result.errors:
                error_messages.append(f"ERROR: {test}\n{error}")
                
            return False, "\n".join(error_messages)
        
        return True, "All tests passed"
        
    except Exception as e:
        # Handle any exceptions during test loading/execution
        error_message = f"Error running {file_path}: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return False, error_message

def main():
    """Run all core tests."""
    # Get the current directory (should be project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Make sure the Dawn codebase is in the Python path
    sys.path.insert(0, script_dir)
    
    # Path to tests/core directory
    core_tests_dir = os.path.join(script_dir, "tests", "core")
    
    # Get all test files
    test_files = []
    for file in os.listdir(core_tests_dir):
        if file.startswith("test_") and file.endswith(".py"):
            test_files.append(os.path.join(core_tests_dir, file))
    
    # Sort the files to ensure consistent order
    test_files.sort()
    
    # Run each test file
    success_count = 0
    failure_count = 0
    failures = {}
    
    for file_path in test_files:
        success, message = run_test_file(file_path)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
            failures[file_path] = message
    
    # Print summary
    print("\n\n")
    print(f"{'='*80}")
    print(f"Test Suite Summary")
    print(f"{'='*80}")
    print(f"Total test files: {len(test_files)}")
    print(f"Successful test files: {success_count}")
    print(f"Failed test files: {failure_count}")
    
    if failure_count > 0:
        print("\nFailed test files:")
        for file_path, message in failures.items():
            print(f"  - {os.path.basename(file_path)}")
            print(f"    Errors: {message.count('ERROR:') + message.count('FAILURE:')}")
        
        print("\nFirst failure details:")
        first_failure = next(iter(failures.values()))
        # Print just the first few lines to avoid too much output
        first_lines = first_failure.split('\n')[:20]
        print('\n'.join(first_lines))
        if len(first_lines) < len(first_failure.split('\n')):
            print("... (truncated output)")
        
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 