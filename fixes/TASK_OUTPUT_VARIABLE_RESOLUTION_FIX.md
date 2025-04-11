# Task Output and Variable Resolution Fixes

## Issue Description

Two key issues were identified in the workflow execution system:

1. **AsyncWorkflowEngine DirectHandlerTask Support**: The AsyncWorkflowEngine didn't properly handle DirectHandlerTask instances, resulting in the error message:
   ```
   ERROR: Tool task 'generate_summary_task' ('__direct_handler__') failed: Tool '__direct_handler__' not found in registry
   ```

2. **Variable Resolution Path Mismatch**: The variable resolution paths in some tasks didn't match the actual structure of the task output data:
   ```
   ERROR: Substitution error: Nested key 'summary' not found for task 'generate_summary_task'.
   ```

## Root Cause Analysis

### DirectHandlerTask Support

The AsyncWorkflowEngine was missing proper handling for DirectHandlerTask instances:

1. In WorkflowEngine, there was a check for `hasattr(task, "is_direct_handler") && task.is_direct_handler` but AsyncWorkflowEngine was missing this check.
2. This caused DirectHandlerTasks to be incorrectly treated as regular tool tasks.
3. The engine attempted to use the tool registry to execute them, looking for a tool called "__direct_handler__" which doesn't exist.

### Variable Resolution Path Mismatch

The variable resolution issues were caused by:

1. Incorrect assumptions about the output structure of DirectHandlerTask instances. 
2. When a DirectHandlerTask returns:
   ```python
   {
     "success": True,
     "result": data
   }
   ```
   The system stores this in `task.output_data.result`, but some variable references were looking for `task.output_data.summary` or directly at `task.output_data.search_results`.

3. Additionally, some handlers were returning nested data structures that didn't match what the task was expecting:
   ```python
   return {
       "success": True,
       "result": {
           "summary": summary,
           "sources_used": sources,
           "generated_at": datetime.now().isoformat()
       }
   }
   ```
   But the referencing task was looking for `${task.output_data.result}` expecting it to be a string rather than a dictionary.

## Solutions Implemented

### AsyncWorkflowEngine Fix

Added proper DirectHandlerTask support to AsyncWorkflowEngine:

1. Created a new method for handling DirectHandlerTask instances:
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

2. Updated the `async_execute_task` method to check for DirectHandlerTask:
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

### Variable Resolution Fixes

1. Updated handler output structures to match expectations:
```python
# Before
return {
    "success": True,
    "result": {
        "summary": summary,
        "sources_used": sources,
        "generated_at": datetime.now().isoformat()
    }
}

# After
return {
    "success": True,
    "result": summary,
    "metadata": {
        "sources_used": sources,
        "generated_at": datetime.now().isoformat()
    }
}
```

2. Fixed variable resolution paths in task definitions:
```python
# Before
task5_summarize = DirectHandlerTask(
    task_id="generate_summary_task",
    name="5. Generate Combined Summary",
    handler=generate_summary_handler,
    input_data={
        "doc_insights": "${file_search_task.output_data.result}",
        "regenerated_insights": "${regenerate_insights_task.output_data.insights}",
        "web_results": "${web_search_task.output_data.result}",
        "default_web_results": "${default_web_search_task.output_data.search_results}"
    },
)

# After
task5_summarize = DirectHandlerTask(
    task_id="generate_summary_task",
    name="5. Generate Combined Summary",
    handler=generate_summary_handler,
    input_data={
        "doc_insights": "${file_search_task.output_data.result}",
        "regenerated_insights": "${regenerate_insights_task.output_data.result.insights}",
        "web_results": "${web_search_task.output_data.result}",
        "default_web_results": "${default_web_search_task.output_data.result.search_results}"
    },
)
```

3. Fixed output field references:
```python
# Before
write_markdown_task = Task(
    task_id="write_markdown_task",
    name="6. Write Summary to Markdown",
    tool_name="write_markdown",
    input_data={
        "file_path": output_file_path,
        "content": "${generate_summary_task.output_data.summary}",
    },
)

# After
write_markdown_task = Task(
    task_id="write_markdown_task",
    name="6. Write Summary to Markdown",
    tool_name="write_markdown",
    input_data={
        "file_path": os.path.join(os.path.dirname(__file__), "output", "AI_ethics_summary_enhanced.md"),
        "content": "${generate_summary_task.output_data.result}",
    },
)
```

## Verification

A test script (`fixes/variable_resolution_test.py`) was created to verify that the fixes work correctly with both synchronous and asynchronous workflows. The test:

1. Creates a workflow with two DirectHandlerTask instances
2. Uses complex nested variable references between the tasks 
3. Runs the workflow with both synchronous and asynchronous engines
4. Verifies that variable resolution works correctly in both cases

## Additional Documentation

The improvements to task output and variable resolution have been documented in `docs/IMPROVED_VARIABLE_RESOLUTION.md`, which provides:

1. Overview of the improved capabilities
2. Examples of how to use DirectHandlerTask
3. Explanation of the enhanced variable resolution syntax
4. Best practices for using these features

## Conclusion

These fixes ensure that:

1. DirectHandlerTask instances work correctly in both synchronous and asynchronous workflows
2. Variable resolution can handle complex nested data structures
3. There is a consistent path to access task outputs
4. Error messages are more informative when variable resolution fails

The changes have been made with minimal impact to existing code and maintain backward compatibility with current workflows. 