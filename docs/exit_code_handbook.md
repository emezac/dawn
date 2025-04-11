# Dawn Framework Exit Codes Handbook

## Introduction

Exit codes in the Dawn Framework provide a standardized way to communicate the outcome of script executions through operating system signals. This handbook details the exit code standards, explains when each code is used, and provides guidance on handling exit codes in different contexts.

## Why Exit Codes Matter

Exit codes are essential for:

1. **Automated Workflows**: CI/CD pipelines and automation scripts rely on exit codes to determine success or failure
2. **Error Handling**: Different types of failures require different recovery strategies
3. **Operational Monitoring**: Monitoring systems can categorize issues based on exit codes
4. **Debugging**: Quick identification of error categories without parsing logs

## Standardized Exit Code Conventions

The Dawn Framework uses the following standardized exit codes:

| Exit Code | Category | Description |
|-----------|----------|-------------|
| 0 | SUCCESS | Workflow or process completed successfully |
| 1 | GENERAL_ERROR | General unexpected error occurred |
| 2 | CONFIG_ERROR | Configuration error (missing API keys, invalid settings) |
| 3 | RESOURCE_ERROR | Resource error (missing tools, service unavailable) |
| 4 | EXECUTION_ERROR | Execution error (task failures, workflow routing issues) |
| 5 | INPUT_ERROR | Input validation error (invalid format, missing fields) |
| 130 | INTERRUPTED | Process was interrupted by the user (SIGINT) |

## When Each Exit Code is Used

### 0: SUCCESS
- Workflow completed without critical errors
- All tasks executed successfully
- Expected output was generated

```python
# Example of successful exit
logger.info("Workflow completed successfully")
sys.exit(0)  # Explicit successful exit
```

### 1: GENERAL_ERROR
- Unexpected exceptions or errors that don't fit other categories
- Framework initialization failures
- Unhandled exceptions in the main process

```python
# Example of general error exit
try:
    # Main workflow code
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    traceback.print_exc()
    sys.exit(1)  # General error exit
```

### 2: CONFIG_ERROR
- Missing required environment variables
- Invalid configuration settings
- Missing API keys or credentials
- Incorrect file paths in configuration

```python
# Example of configuration error exit
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY environment variable is required for LLM tasks")
    sys.exit(2)  # Configuration error exit
```

### 3: RESOURCE_ERROR
- Required tools missing from registry
- External service unavailable
- Failed to create or access required resources
- Database connection failures

```python
# Example of resource error exit
compliance_vs_id = create_compliance_vector_store_if_needed()
if not compliance_vs_id:
    logger.error("Failed to ensure compliance vector store is ready")
    sys.exit(3)  # Resource error exit
```

### 4: EXECUTION_ERROR
- Workflow task failures
- Tool execution errors
- LLM generation failures
- Issues with workflow routing logic

```python
# Example of execution error exit
if failed_tasks > 0:
    logger.warning("Workflow marked as failed due to task failures")
    sys.exit(4)  # Execution error exit
```

### 5: INPUT_ERROR
- Invalid input data format
- Missing required input fields
- Validation errors in input data
- Type mismatches in input parameters

```python
# Example of input error exit
if not validate_input_structure(input_data):
    logger.error(f"Invalid input data structure: {validation_errors}")
    sys.exit(5)  # Input error exit
```

### 130: INTERRUPTED
- Process was interrupted by user (Ctrl+C)
- Graceful handling of SIGINT signal
- Usually not explicitly set, but returned by the OS

```python
# Example of handling interruption
try:
    # Main workflow code
except KeyboardInterrupt:
    logger.info("Process interrupted by user")
    sys.exit(130)  # Standard code for SIGINT
```

## Using the Exit Code Manager

The Dawn Framework provides utility functions for standardized exit code handling in the `core.utils.exit_code_manager` module.

### The ExitCode Enum

Use the `ExitCode` enum for type-safe exit code references:

```python
from core.utils.exit_code_manager import ExitCode

# Using enum values
if critical_error:
    sys.exit(ExitCode.CONFIG_ERROR.value)
```

### The `wrap_main_function` Decorator

The recommended approach for handling exit codes is to use the `wrap_main_function` decorator:

```python
from core.utils.exit_code_manager import wrap_main_function

def main() -> Dict[str, Any]:
    """Main function that returns a status dictionary."""
    try:
        # Your workflow code here
        
        # Return success
        return {
            "success": True,
            "result": result_data
        }
    except ValueError as e:
        # Return input error
        return {
            "success": False,
            "error": str(e),
            "error_type": "input"
        }
    # Additional error handling...

if __name__ == "__main__":
    # Let the wrapper handle exit codes
    wrap_main_function(main)()
```

The decorator will:
1. Call your main function
2. Examine the returned status dictionary
3. Exit with the appropriate code based on the `success` and `error_type` fields

### Supported Error Types

When using `wrap_main_function`, use these error types in your status dictionaries:

| error_type | Mapped Exit Code |
|------------|------------------|
| "config" | 2 (CONFIG_ERROR) |
| "resource" | 3 (RESOURCE_ERROR) |
| "execution" | 4 (EXECUTION_ERROR) |
| "input" | 5 (INPUT_ERROR) |
| Any other value | 1 (GENERAL_ERROR) |

## Handling Exit Codes in Automation Scripts

When calling Dawn Framework scripts from automation tools or other scripts, check the exit code to determine the outcome:

### Bash Example

```bash
#!/bin/bash

# Run workflow script
python examples/smart_compliance_workflow.py

# Check exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Workflow completed successfully"
elif [ $EXIT_CODE -eq 2 ]; then
    echo "Configuration error - check environment variables"
elif [ $EXIT_CODE -eq 3 ]; then
    echo "Resource error - check services and connections"
elif [ $EXIT_CODE -eq 4 ]; then
    echo "Execution error - check workflow tasks"
else
    echo "Unknown error (code $EXIT_CODE)"
fi
```

### Python Example

```python
import subprocess

# Run workflow script
result = subprocess.run(["python", "examples/smart_compliance_workflow.py"], capture_output=True)

# Check exit code
if result.returncode == 0:
    print("Workflow completed successfully")
elif result.returncode == 2:
    print("Configuration error - check environment variables")
    # Take remedial action...
elif result.returncode == 3:
    print("Resource error - check services and connections")
    # Take remedial action...
elif result.returncode == 4:
    print("Execution error - check workflow tasks")
    # Take remedial action...
else:
    print(f"Unknown error (code {result.returncode})")
```

## Best Practices

1. **Always Use Standard Exit Codes**: Use the defined exit codes consistently in all scripts
2. **Return Status Dictionaries**: Have main functions return status dictionaries instead of calling `sys.exit` directly
3. **Use the Wrapper**: Use `wrap_main_function` to standardize exit code handling
4. **Provide Detailed Error Messages**: Include descriptive error messages in your status dictionaries
5. **Handle Specific Exceptions**: Catch and categorize exceptions to use the most appropriate exit code
6. **Log Before Exiting**: Always log an appropriate message before exiting with a non-zero code
7. **Document Special Cases**: If your script has unique exit code needs, document them clearly

## Integrating with Monitoring Systems

Exit codes can be integrated with monitoring systems to provide meaningful alerts:

```bash
# Example alert configuration in a monitoring system
if [[ $(grep "exit code: [2-5]" /var/logs/dawn/*.log) ]]; then
  # Send alert based on code
  if [[ $(grep "exit code: 2" /var/logs/dawn/*.log) ]]; then
    send_alert "Configuration error" "critical"
  elif [[ $(grep "exit code: 3" /var/logs/dawn/*.log) ]]; then
    send_alert "Resource error" "high"
  elif [[ $(grep "exit code: 4" /var/logs/dawn/*.log) ]]; then
    send_alert "Execution error" "medium"
  else
    send_alert "Input error" "low"
  fi
fi
```

## Troubleshooting Common Issues

### Issue: Script Always Exits with Code 1
- Check for unhandled exceptions in the main function
- Ensure your status dictionary has the `success` field set correctly
- Verify you're not overriding the exit code elsewhere

### Issue: Wrong Exit Code for Error Type
- Ensure you're using the standard error type strings ("config", "resource", etc.)
- Check that your main function is returning the status dictionary correctly
- Verify the error is being caught in the right exception handler

### Issue: Exit Code Not Detected by Parent Process
- Ensure you're properly capturing the exit code in the parent process
- Check for any middleware that might modify exit codes
- Verify the script is actually exiting with `sys.exit()` and not just returning

## Conclusion

Standardized exit codes provide a consistent way to communicate script execution outcomes throughout the Dawn Framework. By following these conventions, you'll make your scripts more reliable, easier to monitor, and simpler to integrate into automated workflows.

For more information on error handling in the Dawn Framework, see also:
- [Error Codes Reference](./error_codes_reference.md)
- [Error Propagation](./error_propagation.md)
- [Error Handling](./ERROR_HANDLING.md) 