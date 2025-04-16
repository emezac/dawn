# DirectHandlerTask Handler Parameter Fix

## Problem Description

The `economic_impact_researcher.py` script was failing with the following error:

```
DirectHandlerTask 'plan_research' requires either 'handler' callable or 'handler_name' string.
```

This error occurred when creating instances of `DirectHandlerTask` in the `construct_economic_research_workflow()` function.

## Root Cause

The constructor signature for `DirectHandlerTask` has changed in the framework. Previously, it accepted a `handler_function` parameter for specifying the handler function, but now it requires a parameter named `handler` instead.

In the `construct_economic_research_workflow()` function, all tasks were being created with the old parameter name:

```python
plan_research = DirectHandlerTask(
    task_id="plan_research",
    name="Plan Research",
    description="Plan the economic research based on user's request",
    handler_function=custom_plan_user_request_handler,  # Old parameter name
    # ...
)
```

## Solution

Updated all five `DirectHandlerTask` instances in `construct_economic_research_workflow()` to use the `handler` parameter instead of `handler_function`:

```python
plan_research = DirectHandlerTask(
    task_id="plan_research",
    name="Plan Research",
    description="Plan the economic research based on user's request",
    handler=custom_plan_user_request_handler,  # Changed from handler_function to handler
    # ...
)
```

This change was applied to all five tasks in the workflow:
- `plan_research`
- `validate_plan`
- `plan_to_tasks`
- `execute_tasks`
- `summarize_results`

## Verification

After making these changes, the script runs without the constructor parameter errors, allowing the workflow to initialize properly.

## Additional Notes

This change follows our previous fix for the `id` to `task_id` parameter change in the same class. The API of the `DirectHandlerTask` class has been updated to use more consistent naming conventions, with `handler` being the parameter for specifying the callable function that handles the task's execution. 