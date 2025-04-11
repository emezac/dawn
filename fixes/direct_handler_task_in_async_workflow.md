# Fix: DirectHandlerTask Support in AsyncWorkflowEngine

## Issue Description

When using `DirectHandlerTask` in a workflow executed by the `AsyncWorkflowEngine`, the following error occurs:

```
ERROR: Tool task 'generate_summary_task' ('__direct_handler__') failed: Tool '__direct_handler__' not found in registry
```

This happens because while the synchronous `WorkflowEngine` has special handling for `DirectHandlerTask` instances, the asynchronous version (`AsyncWorkflowEngine`) does not. When it encounters a `DirectHandlerTask`, it treats it as a regular tool task and attempts to find a tool named `__direct_handler__` in the registry, which doesn't exist.

## Root Cause Analysis

1. In `core/engine.py`, the `WorkflowEngine.execute_task()` method checks for `DirectHandlerTask` instances with:
   ```python
   if hasattr(task, "is_direct_handler") and task.is_direct_handler:
       # Execute DirectHandlerTask directly using its execute method
       result = task.execute(processed_input)
   ```

2. However, in `core/async_workflow_engine.py`, the `AsyncWorkflowEngine.async_execute_task()` method only checks for LLM tasks:
   ```python
   if task.is_llm_task:
       execution_result = await self.async_execute_llm_task(task)
   else:
       execution_result = await self.async_execute_tool_task(task)
   ```

3. This causes `DirectHandlerTask` instances to be passed to `async_execute_tool_task()`, which attempts to execute them using the tool registry, resulting in the error.

## Solution

The solution is to add proper support for `DirectHandlerTask` in the `AsyncWorkflowEngine` by:

1. Adding a new method to handle direct handler tasks:
```python
async def async_execute_direct_handler_task(self, task: Task) -> Dict[str, Any]:
    """Executes a DirectHandlerTask by calling its execute method directly."""
    processed_input = self.process_task_input(task)
    
    try:
        # Execute the DirectHandlerTask's execute method
        result = task.execute(processed_input)
        
        if result.get("success"):
            return {"success": True, "result": result.get("result", result.get("response", {}))}
        else:
            error_msg = result.get("error", "Unknown DirectHandlerTask error")
            log_error(f"DirectHandlerTask '{task.id}' failed: {error_msg}")
            return {"success": False, "error": error_msg}
    except Exception as e:
        log_error(f"Exception during execution of DirectHandlerTask '{task.id}': {e}", exc_info=True)
        return {"success": False, "error": f"DirectHandlerTask execution error: {str(e)}"}
```

2. Modifying `async_execute_task()` to check for direct handler tasks:
```python
async def async_execute_task(self, task: Task) -> bool:
    """Executes a single task, handles retries, sets output and status."""
    log_task_start(task.id, task.name, self.workflow.id)
    task.set_status("running")
    execution_result: Dict[str, Any] = {}

    try:
        # Check if this is a DirectHandlerTask
        if hasattr(task, "is_direct_handler") and task.is_direct_handler:
            execution_result = await self.async_execute_direct_handler_task(task)
        elif task.is_llm_task:
            execution_result = await self.async_execute_llm_task(task)
        else:
            execution_result = await self.async_execute_tool_task(task)

        # Rest of the method remains the same...
```

## Testing

A verification script has been created at `fix_for_direct_handler_task.py` that demonstrates the proper operation of a `DirectHandlerTask` and provides the implementation for the fix.

## Additional Improvements to Variable Resolution

The workflow failure also revealed issues with variable resolution in the AsyncWorkflowEngine when tasks are in the "pending" state. The following warnings were observed:

```
WARNING: Substitution skipped: Referenced task 'regenerate_insights_task' status is 'pending'. Cannot resolve value.
WARNING: Substitution skipped: Referenced task 'default_web_search_task' status is 'pending'. Cannot resolve value.
```

This is expected behavior when dependent tasks haven't completed yet, but it may indicate a need for better handling of task dependencies in the workflow definition to ensure that tasks don't rely on output from tasks that may never execute.

## Implementation Notes

This fix was applied to the codebase in April 2024 to resolve the issue with running complex parallel workflows that use `DirectHandlerTask` instances. The fix maintains consistency between the synchronous and asynchronous workflow engines, allowing for seamless switching between them. 