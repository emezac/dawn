# Fix for Plan Validation Test When Using Unavailable Tools

## Issue Description

A failing test was identified in `test_chat_planner_handlers.py`:

```
FAIL: test_validate_plan_handler_capability_check (__main__.TestChatPlannerHandlers)
Test validate_plan_handler's check for unavailable tools/handlers.
----------------------------------------------------------------------
AssertionError: False is not true
```

This test was failing because it was expecting the validation handler to succeed with warnings when a plan references an unavailable tool, but the validation was failing with errors instead.

## Root Cause

There were two issues:

1. The test plan was missing the required `depends_on` field, causing it to fail schema validation before it even got to the tool availability check. This made it impossible to test the specific behavior we wanted to validate.

2. The test was not explicitly setting a validation strictness level, so it was using the default "high" strictness, which was causing the validation to fail for any issues found.

## Solution

The solution involved two changes:

1. Added the required `depends_on` field to the test plan:

```python
plan_with_unavailable_tool = [
    {
        "step_id": "step_1",
        "description": "Use unavailable tool",
        "type": "tool",
        "name": "nonexistent_tool",
        "inputs": {},
        "depends_on": []  # Added the required depends_on field
    }
]
```

2. Explicitly set the validation strictness to "medium" for the test and added cleanup code to restore the original value after the test:

```python
# Set medium strictness for this test
original_strictness = config_get("chat_planner.validation_strictness", "high")
self.addCleanup(config_set, "chat_planner.validation_strictness", original_strictness)
config_set("chat_planner.validation_strictness", "medium")
```

## Related Components

- `examples/chat_planner_workflow.py` - Contains the `validate_plan_handler` function
- `tests/core/test_chat_planner_handlers.py` - Contains the failing test

## Testing

After the fix, the test correctly passes by ensuring:
1. The plan passes schema validation (with the required field)
2. It uses medium strictness (where tool availability is a warning, not an error)
3. The warning about the unavailable tool is properly included in the results

These changes ensure that the test is properly testing the intended behavior - that unavailable tools result in warnings rather than validation errors. 