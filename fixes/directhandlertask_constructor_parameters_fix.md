# DirectHandlerTask Constructor Parameters Fix

## Problem Description

The `economic_impact_researcher.py` script was failing with the following error:

```
economic_impact_researcher - ERROR - An error occurred: DirectHandlerTask.__init__() missing 2 required positional arguments: 'task_id' and 'name'
```

This error occurred when creating instances of `DirectHandlerTask` in the `construct_economic_research_workflow()` function.

## Root Cause

The constructor signature for `DirectHandlerTask` has changed in the framework. Previously, it accepted an `id` parameter, but now it requires both `task_id` and `name` parameters.

In the `construct_economic_research_workflow()` function, all tasks were being created with the old parameter name:

```python
plan_research = DirectHandlerTask(
    id="plan_research",  # Old parameter name
    description="Plan the economic research based on user's request",
    # ...
)
```

## Solution

Updated all five `DirectHandlerTask` instances in `construct_economic_research_workflow()` to:

1. Replace `id` with `task_id`
2. Add a `name` parameter with a descriptive name for each task

For example:

```python
plan_research = DirectHandlerTask(
    task_id="plan_research",  # Changed from id to task_id
    name="Plan Research",     # Added name parameter
    description="Plan the economic research based on user's request",
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

This change reflects an API update in the Dawn framework's `DirectHandlerTask` class that required more explicit naming parameters. When framework APIs change, it's important to update all code that uses those APIs to match the new requirements. 