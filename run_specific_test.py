#!/usr/bin/env python3
"""Script to run a specific test with output saved to a file."""  # noqa: D202

import subprocess
import sys
import os

def main():
    """Run the test file and save output to a file."""
    test_file = "tests/core/test_plan_validation.py"
    output_file = "plan_validation_tests.log"
    
    cmd = ["python", "-m", "pytest", test_file, "-v"]
    
    try:
        with open(output_file, "w") as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                check=False
            )
        
        print(f"Test execution completed. Results saved to {output_file}")
        print(f"Exit code: {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 