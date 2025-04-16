#!/usr/bin/env python3
"""Script to run the chat_planner_handlers tests and capture the output."""  # noqa: D202

import subprocess
import sys
import os

def run_tests():
    """Run the specified tests and capture the output."""
    test_path = "tests/core/test_chat_planner_handlers.py"
    output_file = "chat_planner_tests.log"
    
    print(f"Running tests for {test_path}")
    print(f"Results will be saved to {output_file}")
    
    try:
        with open(output_file, "w") as f:
            result = subprocess.run(
                ["python", "-m", "pytest", test_path, "-v"],
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                check=False
            )
        
        print(f"Tests completed with exit code: {result.returncode}")
        
        # Now print the content of the output file
        with open(output_file, "r") as f:
            print("\nTest output:")
            print("-" * 80)
            print(f.read())
            
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests()) 