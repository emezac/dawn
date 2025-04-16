# Fix for Chat Planner Test Failures

## Problem Description

The tests in `tests/core/test_chat_planner_handlers.py` were failing with the following error:

```
AttributeError: module 'examples' has no attribute 'chat_planner_config'. Did you mean: 'chat_planner_workflow'?
```

Specifically, the following tests were failing:
1. `test_plan_user_request_handler_ambiguity_detection`
2. `test_plan_user_request_handler_llm_failure`
3. `test_plan_user_request_handler_success`

The issue was related to how the tests were attempting to patch the `examples.chat_planner_config` module using the `@patch` decorator.

## Root Cause

The root cause was that the patching mechanism in Python's `unittest.mock` library relies on imports being available in the module namespace. When using a decorator like:

```python
@patch('examples.chat_planner_config.ChatPlannerConfig.get_max_clarifications', return_value=3)
```

This only works if the module `examples.chat_planner_config` can be properly imported. Even though the module was mocked using `sys.modules`, the patching mechanism was still trying to access it as a real module.

## Solution

The solution involved two key changes:

1. Define a mock function to replace the one we're trying to patch:
   ```python
   def mock_get_max_clarifications():
       return 3
   ```

2. For each test that needs this mock, directly replace the method on the mock module and restore it after the test:
   ```python
   original_func = sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications
   sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = mock_get_max_clarifications
   
   try:
       # Test code here
   finally:
       # Restore original function
       sys.modules['examples.chat_planner_config'].ChatPlannerConfig.get_max_clarifications = original_func
   ```

This approach is more direct and less prone to import-related issues than using the `@patch` decorator.

## Verification

After applying these changes, all tests pass successfully:

```
tests/core/test_chat_planner_handlers.py::TestChatPlannerHandlers::test_plan_user_request_handler_ambiguity_detection PASSED [ 33%]
tests/core/test_chat_planner_handlers.py::TestChatPlannerHandlers::test_plan_user_request_handler_llm_failure PASSED [ 40%]
tests/core/test_chat_planner_handlers.py::TestChatPlannerHandlers::test_plan_user_request_handler_success PASSED [ 53%]
```

The full test suite runs without any failures related to this issue.

## Additional Notes

This pattern can be used in other tests where modules are mocked using `sys.modules` but still need to have specific behavior for individual test cases. It's especially useful when dealing with imports that might not be available in the test environment or with complex dependency structures. 