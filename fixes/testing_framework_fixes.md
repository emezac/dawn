# Testing Framework Fixes

## Issues with the Testing Utilities

### Problem 1: TaskStatus Import Error
The testing framework (`core/utils/testing.py`) was attempting to import a `TaskStatus` enum from `core.task`, but this enum wasn't defined in that module. This caused the following error when running workflow tests:

```
Error importing test modules: cannot import name 'TaskStatus' from 'core.task' (/Users/admin/code/newstart/dawn/core/task.py)
```

### Problem 2: MockToolRegistry Import Error
After fixing the first issue, another import error appeared. The testing framework was attempting to import `MockToolRegistry` from `core.tools.registry`, but this class is actually defined in `core.tools.mock_registry`.

```
Error importing test modules: cannot import name 'MockToolRegistry' from 'core.tools.registry' (/Users/admin/code/newstart/dawn/core/tools/registry.py)
```

### Problem 3: Incorrect Test Reporting
The `run_tests.sh` script was incorrectly reporting "All tests passed!" even when some tests failed, because it was only checking the exit code of the last test run.

### Problem 4: MockToolRegistry Constructor Mismatch
After addressing the import errors, we encountered initialization errors. In the testing utilities, `MockToolRegistry` was being initialized with mock executions passed directly to the constructor, but the actual implementation of `MockToolRegistry` doesn't accept parameters in its constructor:

```
TypeError: MockToolRegistry.__init__() takes 1 positional argument but 2 were given
```

## Solutions

### Fix for TaskStatus Import
We defined a `TaskStatus` enum locally in the testing.py file instead of trying to import it:

```python
# Define TaskStatus enum locally since it doesn't exist in core.task
from enum import Enum

class TaskStatus(Enum):
    """Task status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
```

### Fix for MockToolRegistry Import
We updated the import statement to use the correct module:

```python
# Changed from:
from core.tools.registry import MockToolRegistry
# To:
from core.tools.mock_registry import MockToolRegistry
```

### Fix for Test Reporting
We modified the `run_tests.sh` script to track test failures throughout execution rather than just checking the last exit code:

```bash
# Initialize test failure tracker
TESTS_FAILED=0

# After each test run:
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    TESTS_FAILED=1
fi

# Check final status based on the failure tracker
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    # ...
else
    echo -e "\n${RED}Some tests failed!${NC}"
    # ...
fi
```

### Fix for MockToolRegistry Constructor Mismatch
We changed how the `MockToolRegistry` is initialized in the testing utilities. Instead of passing mock executions directly to the constructor, we create the registry first and then configure it using the proper methods:

```python
# Before:
mock_registry = MockToolRegistry(mock_executions)

# After:
mock_registry = MockToolRegistry()

# Configure mock executions
for tool_name, executions in mock_executions.items():
    for mock_config in executions:
        input_pattern = mock_config.get("input_pattern", {})
        output = mock_config.get("output", {})
        exception = mock_config.get("exception")
        
        if exception:
            # Configure an exception to be raised
            mock_registry.mock_tool_as_failure(
                tool_name, 
                str(exception),
            )
        else:
            # Configure a success response
            mock_registry.add_mock_response(
                tool_name,
                input_pattern,
                output or {}
            )
```

We've used `get()` with default values to safely extract configuration values, improving robustness against missing keys. We applied this fix in both the `workflow_test_context` function and the `TaskTestHarness` class.

## Remaining Issues

There may still be some test failures in the workflow examples test file that need further investigation. The MockToolRegistry initialization fix should address the most immediate initialization errors, but other integration and functionality issues might exist.

## Related Documentation

See also:
- `fixes/workflow_test_fixes.md` for earlier fixes to the testing framework
- `tests/workflows/examples/test_workflow_examples.py` for example workflow tests 