# Fix for validate_plan_handler Strictness Levels

## Issue Description

A failing test was identified in `test_chat_planner_handlers.py` related to the validation of plans with unavailable tools or handlers:

```
FAIL: test_validate_plan_handler_capability_check (__main__.TestChatPlannerHandlers)
Test validate_plan_handler's check for unavailable tools/handlers.
```

The test expected that when a plan references unavailable tools or handlers, the validation should succeed with warnings rather than fail with errors, regardless of the validation strictness level.

However, after the "Option B" changes were applied to remove LLM validation from the `validate_plan_handler` function, the behavior had changed. When in "strict" mode, unavailable tools/handlers were being treated as errors rather than warnings.

## Root Cause

In the `validate_plan_handler` function in `chat_planner_workflow.py`, there was a conditional that would add unavailable tool/handler messages to the `validation_errors` list when in "strict" mode, causing validation to fail. The test expected these to be treated as warnings in all cases.

The problematic code:

```python
if capability_name and capability_name not in available_tool_names:
    msg = f"Step {i+1} ('{step_id}'): Tool '{capability_name}' is not available."
    if strictness == "strict": validation_errors.append(msg)  # This causes failure in strict mode
    else: validation_warnings.append(msg)
```

## Solution

The solution was to always treat unavailable tools/handlers as warnings rather than errors, regardless of the strictness level:

```python
if capability_name and capability_name not in available_tool_names:
    msg = f"Step {i+1} ('{step_id}'): Tool '{capability_name}' is not available."
    # Always add as warning, never as error, regardless of strictness
    validation_warnings.append(msg)
```

This change ensures that unavailable tools/handlers are always reported as warnings rather than errors, allowing validation to succeed as expected by the test.

## Related Components

- `examples/chat_planner_workflow.py` - The file containing the `validate_plan_handler` function
- `tests/core/test_chat_planner_handlers.py` - The file containing the failing test
- `ChatPlannerConfig` - Configuration class that controls validation strictness

## Testing

After the fix, the failing test `test_validate_plan_handler_capability_check` should pass successfully. 