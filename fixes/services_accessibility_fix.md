# Service Accessibility Fix for Handler Functions

## Issue

The `economic_impact_researcher.py` script was failing with the error:

```
ERROR:__main__:LLM interface not available
```

The script was attempting to access the LLM interface through `task.services.get_llm_interface()`, but the service wasn't accessible that way.

## Root Cause Analysis

There were multiple issues:

1. **Handler function couldn't access services through task**: The task object (`DirectHandlerTask`) didn't consistently provide access to the services container.
   
2. **Inconsistent service access pattern**: Different handler functions were using different patterns to access services - some through the task object, others with global lookups.

3. **ErrorCode missing constant**: The engine was using `ErrorCode.TASK_FAILED` which didn't exist, while the correct constant was `ErrorCode.EXECUTION_TASK_FAILED`.

## Solution

### 1. Direct Service Access

Updated all handlers to directly access services through the global registry:

```python
# Import services module
from core.services import get_services

# Get services directly 
services = get_services()
logger = services.logger or logging.getLogger(__name__)

# Get LLM interface directly from services
llm = services.get_llm_interface()
```

This removes the dependency on the task object having a properly set `services` attribute.

### 2. Standardized Service Access Pattern

Applied a consistent pattern across all handler functions:
- Import services at the top of each handler
- Use `get_services()` instead of assuming services are available on the task
- Use service methods directly from the services container

### 3. Fixed ErrorCode Reference

Updated the engine's error handling:
```python
# Changed from
self.workflow.set_error(
    f"Task '{current_task.id}' failed permanently.",
    ErrorCode.TASK_FAILED,  # This constant doesn't exist
    current_task.id
)

# To
self.workflow.set_error(
    f"Task '{current_task.id}' failed permanently.",
    ErrorCode.EXECUTION_TASK_FAILED,  # This constant exists in core.errors.ErrorCode
    current_task.id
)
```

## Impact

These changes ensure that:
1. Handler functions can reliably access framework services regardless of how they're called
2. Services are accessed in a consistent manner across all handlers
3. The workflow engine uses valid error codes when recording failures

## Best Practices

1. **Always use direct service access**: Don't rely on services being passed through task objects:
   ```python
   from core.services import get_services
   services = get_services()
   ```

2. **Handle service availability**: Always check if a service exists before using it:
   ```python
   llm = services.get_llm_interface()
   if not llm:
       return {"status": "error", "error": "LLM interface not available"}
   ```

3. **Consistent Error Handling**: Use standard error response formats in all handlers:
   ```python
   return {
       "status": "error",
       "error": "Error message",
       "error_code": ErrorCode.SPECIFIC_ERROR_CODE
   }
   ```

By following these practices, workflow handler functions will work more reliably and consistently across the framework. 