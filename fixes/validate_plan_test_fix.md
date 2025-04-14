# Fix for Plan Validation Tests After LLM Validation Removal

## Issue Description

A failing test was identified in `test_plan_validation.py`:

```
FAIL: test_llm_assisted_validation_called_on_failure (__main__.TestPlanValidation)
----------------------------------------------------------------------
AssertionError: Expected 'validate_plan_with_llm' to have been called once. Called 0 times.
```

This test was failing because it expected the `validate_plan_with_llm` function to be called during plan validation, but this functionality had been removed as part of "Option B" changes.

## Root Cause

The test `test_llm_assisted_validation_called_on_failure` was written to verify that when validation fails, the code would attempt to use LLM validation to fix the plan. However, the LLM validation code had been intentionally removed from the `validate_plan_handler` function as indicated by a comment:

```python
# --- LLM Validation Block Removed (Option B applied) ---
```

The test was still expecting this behavior, causing it to fail when the `validate_plan_with_llm` function was never called.

## Solution

The test needed to be updated to match the new expected behavior after Option B was applied. Rather than testing that LLM validation is called, we now test that:

1. The `validate_plan_with_llm` function is *not* called
2. Validation simply fails with appropriate errors when given an invalid plan
3. No LLM-specific result fields are present in the response

The test was changed from:

```python
@patch('examples.chat_planner_workflow.validate_plan_with_llm')
def test_llm_assisted_validation_called_on_failure(self, mock_validate_with_llm):
    # ... setup code ...
    mock_validate_with_llm.assert_called_once()
    self.assertTrue(result["success"])
    self.assertTrue(result["result"].get("fixed_by_llm", False))
    self.assertEqual(result["result"]["validated_plan"], fixed_plan_list)
```

To:

```python
@patch('examples.chat_planner_workflow.validate_plan_with_llm')
def test_llm_assisted_validation_called_on_failure(self, mock_validate_with_llm):
    # ... setup code ...
    mock_validate_with_llm.assert_not_called()
    self.assertFalse(result["success"])
    self.assertTrue(result["validation_errors"])
    # No fixed_by_llm or validated_by_llm fields anymore
```

## Related Components

- `examples/chat_planner_workflow.py` - Contains the `validate_plan_handler` function from which LLM validation was removed
- `tests/core/test_plan_validation.py` - Contains the test that needed to be updated

## Testing

After the fix, the test now correctly checks for the current expected behavior of the `validate_plan_handler` function without LLM validation. 