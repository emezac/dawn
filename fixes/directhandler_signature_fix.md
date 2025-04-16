# DirectHandlerTask Signature Fix

## Problem

The `economic_impact_researcher.py` script was failing with the following error:

```
ERROR: Error during task 'plan_research' execution dispatch: custom_plan_user_request_handler() missing 2 required positional arguments: 'services' and 'logger'
```

This error occurred because we had updated our handler functions to use a 4-parameter signature `(input_data, task_id, services, logger)`, but the `DirectHandlerTask` execution system only supports 1-parameter `(input_data)` or 2-parameter `(task, input_data)` handlers.

Our initial fix changed handlers to use the 1-parameter signature, which led to a new error:

```
ERROR: Error during task 'plan_research' execution dispatch: custom_plan_user_request_handler() takes 1 positional argument but 2 were given
```

This indicated that the engine was trying to call our handlers with 2 parameters, not 1.

## Root Cause

The Dawn framework's `DirectHandlerTask` class uses Python's `inspect` module to determine the signature of handler functions and calls them appropriately. Looking at the source code in `core/task.py`:

```python
# Use inspect to call handler correctly (1 or 2 args)
import inspect
handler_sig = inspect.signature(self.handler)
param_count = len(handler_sig.parameters)

if param_count == 1:
    # Assumes handler(input_data: dict) -> dict
    result = self.handler(input_to_use)
elif param_count == 2:
    # Assumes handler(task: Task, input_data: dict) -> dict
    result = self.handler(self, input_to_use)
else:
    raise TypeError(f"Handler '{self.handler_name or 'anonymous'}' for task '{self.id}' has an invalid signature: {param_count} parameters detected. Expected 1 (input_data) or 2 (task, input_data).")
```

Our handlers had 4 parameters, but the system only supports 1 or 2 parameters, leading to the error.

## Solution

We updated all handler functions to use the 2-parameter signature, which is what the engine expects:

1. Changed from:
   ```python
   def custom_plan_user_request_handler(input_data, task_id, services, logger):
   ```

   To:
   ```python
   def custom_plan_user_request_handler(task, input_data):
   ```

2. For handlers that need access to services or logging:
   - We added imports to access the services container and logger directly:
     ```python
     from core.services import get_services
     import logging
     
     services = get_services()
     logger = logging.getLogger("economic_impact_researcher")
     ```

3. For handlers that wrap other handlers (like `custom_execute_dynamic_tasks_handler`):
   - We modified the handler to use the 2-parameter signature but still properly call the underlying handlers:
     ```python
     def custom_execute_dynamic_tasks_handler(task, input_data):
         # Get the services for calling the original handler
         services = get_services()
         task_id = task.id  # Use the actual task ID
         logger = logging.getLogger("economic_impact_researcher")
         
         # Call the original handler with the parameters it expects
         result = execute_dynamic_tasks_handler(input_data, task_id, services, logger)
     ```

4. Ensured that all handlers return properly structured results:
   ```python
   return {
       "success": True,  # Required
       "status": "completed",  # Optional, but good practice
       "result": {
           # ... actual result data ...
       }
   }
   ```
   
   Or for errors:
   ```python
   return {
       "success": False,
       "status": "error",
       "result": {
           "error": "Error message",
           # ... other error details ...
       }
   }
   ```

## Verification

After applying these changes, the economic impact researcher workflow functions correctly. The DirectHandlerTask execution system can properly invoke our handler functions with the expected parameter format.

## Lessons Learned

1. When working with the DirectHandlerTask system, ensure that handler functions follow the supported signature patterns:
   - `handler(input_data: dict) -> dict`
   - `handler(task: Task, input_data: dict) -> dict`

2. Instead of relying on parameters passed to the handler, access global services and loggers directly within the handler when needed.

3. For wrapper functions that call other handlers, manually construct and pass the expected parameters rather than trying to pass them through.

4. Always ensure handler results include the `success` field to indicate execution status, which is used by the workflow engine to determine next steps.

5. Handle input key names flexibly by checking multiple possible keys for the same data:
   ```python
   # Get the topic from input_data - this could be called "topic" or "request"
   user_request = input_data.get("topic", "")
   if not user_request:
       # Try alternative keys if "topic" is not found
       user_request = input_data.get("user_request", "")
       if not user_request:
           user_request = input_data.get("request", "")
   ```
   This approach helps when the workflow engine or dependent tasks may use different field names. 