# DirectHandlerTask Signature Resolution

## Problem Evolution

We encountered an evolving problem with handler signatures in the `economic_impact_researcher.py` script:

1. **Initial error**: 
   ```
   ERROR: Error during task 'plan_research' execution dispatch: custom_plan_user_request_handler() missing 2 required positional arguments: 'services' and 'logger'
   ```

2. **After our first fix** (changing to 1-parameter handlers):
   ```
   ERROR: Error during task 'plan_research' execution dispatch: custom_plan_user_request_handler() takes 1 positional argument but 2 were given
   ```

## Root Cause

The Dawn framework's `DirectHandlerTask` supports two possible handler signatures:

```python
# From core/task.py
if param_count == 1:
    # Assumes handler(input_data: dict) -> dict
    result = self.handler(input_to_use)
elif param_count == 2:
    # Assumes handler(task: Task, input_data: dict) -> dict
    result = self.handler(self, input_to_use)
```

However, in this particular implementation, the framework was specifically calling our handlers with 2 parameters (the task instance and the input data), but our handlers were defined with different signatures:

1. Original implementation: 4 parameters `(input_data, task_id, services, logger)`
2. First fix: 1 parameter `(input_data)` 
3. Final fix: 2 parameters `(task, input_data)`

## Solution

We updated all handler functions to use the 2-parameter signature, which is what the engine actually expects:

```python
def custom_plan_user_request_handler(task, input_data):
    """
    Custom handler to plan research based on user request.
    
    Args:
        task: The DirectHandlerTask instance
        input_data (dict): Input data for the task
        
    Returns:
        dict: Result of the planning operation
    """
    # Access services and logger from within the handler
    from core.services import get_services
    services = get_services()
    import logging
    logger = logging.getLogger("economic_impact_researcher")
    
    # Handler implementation...
```

The key aspects of the fix:

1. Updated all handler signatures to `(task, input_data)`
2. Access services container and logger inside the handler functions
3. For wrappers that call other handlers, pass `task.id` as the task_id parameter
4. Ensure all handlers return standardized output with `success` and `result` fields

## Key Insight

When using `DirectHandlerTask`, it's essential to understand which signature pattern the framework expects for handlers. The most reliable approach is to use the 2-parameter pattern `(task, input_data)`, as it works in all cases and provides the handler with access to the task instance, which can be helpful to:

1. Get the task ID via `task.id`
2. Set task output via `task.set_output()`
3. Access task metadata and other properties

## Lessons Learned

1. The Dawn framework's `DirectHandlerTask` works best with handlers that follow the 2-parameter signature `(task, input_data)`.

2. When wrapping other handlers that expect more parameters, use the task instance to get needed information:
   ```python
   def wrapper_handler(task, input_data):
       services = get_services()
       task_id = task.id
       # Call the original handler with its expected signature
       result = original_handler(input_data, task_id, services, logger)
       return result
   ```

3. Consistent return structures are essential for task outputs:
   ```python
   return {
       "success": True,
       "status": "completed",
       "result": {
           # ... result data ...
       }
   }
   ```

4. Keeping handler functions self-contained by importing needed services inside them rather than relying on parameters makes them more adaptable to framework changes.

This resolution ensures that our handlers align with the expected signature pattern in the Dawn framework, allowing the workflow to execute correctly.

## LLMInterface Usage Issue

### Problem
After fixing the handler signatures, a new error was encountered:
```
Error in custom_plan_user_request_handler: 'LLMInterface' object is not callable
```

This occurred because the `custom_plan_user_request_handler` was attempting to call the LLMInterface object directly as a function (`llm(prompt)`), but the LLMInterface is not a callable object.

### Solution
Updated the LLM invocation to use the `execute_llm_call` method instead of treating the LLM as a callable:

```python
# Before:
response = llm(prompt)  # Incorrect - LLMInterface is not callable

# After:
llm_result = llm.execute_llm_call(prompt)  # Correct - using the proper method
raw_llm_output = llm_result.get("response", "")
```

### Key Insights
- The LLMInterface provides methods like `execute_llm_call` that must be used to interact with the LLM
- The result from `execute_llm_call` is a structured dictionary with keys like "success" and "response"
- Always check the success status before proceeding with further processing of LLM responses

This change ensures proper handling of LLM interactions and error states in the workflow execution. 