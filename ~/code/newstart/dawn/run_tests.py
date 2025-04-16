import subprocess
import sys

def run_tests():
    """Run the specified tests and capture the output."""
    test_path = "tests/core/test_plan_validation.py"
    cmd = ["python", "-m", "pytest", test_path, "-v"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        print("==== TEST OUTPUT ====")
        print(result.stdout)
        
        if result.stderr:
            print("==== ERROR OUTPUT ====")
            print(result.stderr)
        
        print(f"Exit code: {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests()) 