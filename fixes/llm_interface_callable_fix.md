# LLM Interface Callable Fix

## Problem

The `economic_impact_researcher.py` script was using outdated methods to call the LLM interface, such as:

```python
response = llm.complete(prompt)
```

This error occurred after our previous attempts to fix the issue by changing from `llm.chat()` to `llm.generate()` and then to `llm.complete()`, but none of these methods are available in the current version of the framework.

Additionally, several handler functions had incorrect signatures and were not properly integrated with the updated LLM interface.

## Root Cause

The Dawn framework LLM interface API has undergone several iterations:

1. Initial complex API: `llm.chat([{"role": "user", "content": prompt}])`
2. Simplified but still method-based: `llm.generate(messages=[{"role": "user", "content": prompt}])`
3. Further simplified method: `llm.complete(prompt)`
4. Current direct callable interface: `llm(prompt)`

The economic impact researcher script was using method #3, but the framework had been updated to use method #4.

Also, handler function signatures had not been updated to match the new interface, causing incompatibilities when passing parameters.

## Solution

1. Updated the `custom_plan_user_request_handler` function to use the callable LLM interface:
   ```python
   response = llm(prompt)
   ```

2. Implemented the missing `summarize_results_handler` function using the correct interface pattern:
   ```python
   def summarize_results_handler(input_data, task_id, services, logger):
       # ...
       # Get the LLM interface
       llm = services.get_llm_interface()
       # ...
       # Call the LLM directly as a function
       response = llm(prompt)
       # ...
   ```

3. Updated all handler function signatures to match the required interface:
   - Changed from: `def handler(task, input_data: dict) -> dict`
   - To: `def handler(input_data, task_id, services, logger)`

4. Replaced all `print()` statements with `logger.info()` or appropriate logging level calls.

5. Updated the `custom_execute_dynamic_tasks_handler` function to use the correct parameters when calling `execute_dynamic_tasks_handler`.

## Verification

After applying these changes, the economic impact researcher workflow functions correctly. The script properly:

1. Generates a research plan using the LLM interface
2. Validates the plan structure
3. Converts the plan to executable tasks
4. Executes those tasks
5. Summarizes the results into a final report

The workflow visualization is also generated successfully, showing both the static structure of the workflow and the dynamically generated tasks.

## Lessons Learned

1. When interfaces evolve in the framework, it's important to update all dependent code to use the new patterns.
2. Function signatures for handlers should match the expected interface defined by the framework.
3. For functions that wrap other functions, ensure that parameter passing is updated when the wrapped function's signature changes.
4. Proper logging should be used instead of print statements for better debugging and monitoring. 