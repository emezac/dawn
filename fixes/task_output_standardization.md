# Task Output Standardization Fix

## Issue

When running the `economic_impact_researcher.py` script, the workflow failed at the `validate_plan` task with the error:

```
Failed to parse research plan JSON: Expecting value: line 1 column 1 (char 0)
```

Investigation revealed that the issue was caused by inconsistent task output formats across different handler functions and incorrect path references between dependent tasks.

### Root Causes

1. **Inconsistent Output Format**: Handler functions were returning dictionaries with different structures, using varying field names (`status`, `error`, etc.) instead of following a standardized format.

2. **Incorrect Variable Resolution**: Tasks were attempting to access data from previous tasks using incorrect paths, and the variable resolution wasn't working as expected.

3. **Nested Data Access Issues**: The variable resolver had difficulty accessing fields at different levels (top-level, metadata, nested objects).

4. **Missing Success Flag**: Some handlers returned responses without the required `success` flag that helps the workflow engine determine task status.

## Solution

1. **Standardized Output Format with Centralized Result Field**: Updated all handler functions to use a consistent return format with all task-specific data placed in the `result` field:
   ```python
   {
       "success": True/False,       # Required: Boolean indicating success
       "status": "completed/failed", # Required: String status code
       "result": {                  # All task-specific data goes here
           "key_field1": value1,
           "key_field2": value2
       },
       "error": "error_message"     # Error message (when failed)
   }
   ```

2. **Consistent Result Field Access**: Updated all task dependencies to access data through the `result` field:
   ```python
   # Accessing data from previous tasks
   "field_name": "${previous_task.result.field_name}"
   ```

3. **Structured Data Organization**: Ensured all data that will be accessed by dependent tasks is placed inside the `result` dictionary with clear naming patterns:
   ```python
   return {
       "success": True,
       "status": "completed",
       "result": {
           "research_plan": research_plan,
           "raw_llm_output": raw_llm_output
       }
   }
   ```

4. **Consistent Error Handling**: Ensured that all error responses include the required fields (`success=False`, `status="failed"`, and an `error` message).

## Implementation Details

1. Updated the task definition in `construct_economic_research_workflow()` to access data through the `result` field.
2. Refactored all handler functions to place their output data in a structured `result` field.
3. Ensured consistent patterns across all tasks in the workflow.
4. Added debugging to track the actual structure of task outputs to help diagnose variable resolution issues.

## Best Practices

1. **Use the Standard Output Format**: All handler functions should return a dictionary with:
   - `success`: Boolean indicating success or failure
   - `status`: String with values "completed", "failed", or "warning"
   - `result`: Dictionary containing all task-specific data
   - `error`: Error message (when failed)

2. **Always Use the Result Field for Data**: Place all data that will be accessed by dependent tasks inside the `result` field:
   ```python
   return {
       "success": True,
       "status": "completed",
       "result": {
           "key_data": value,
           "additional_data": other_value
       }
   }
   ```

3. **Use Consistent Access Patterns**: When referencing data from a previous task, always use the `result` field:
   ```python
   "input_key": "${task_id.result.data_field}"
   ```

4. **Document Expected Input/Output**: Each handler function should clearly document what input it expects and what output fields it produces.

5. **Debug Task Output Structure**: When encountering variable resolution issues, log the complete structure of the task output to identify the correct paths.

## Impact

This standardized approach ensures that the workflow engine can consistently resolve variable references between tasks. By placing all task data in the `result` field, we create a predictable pattern that simplifies debugging and maintenance.

The changes have resolved the variable resolution issues in the economic impact researcher workflow and provided a more robust pattern for data sharing between dependent tasks throughout the system. 