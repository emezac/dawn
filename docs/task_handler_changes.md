# Task Handler System Updates

This document describes recent changes to the Dawn workflow task handler system to improve compatibility, reliability, and error handling.

## 1. CustomTask Parameter Handling

The `CustomTask` class now accepts an `is_llm_task` parameter (defaulting to `False`), which is properly passed to the parent `Task` class. This allows custom tasks to specify whether they're LLM tasks, bypassing the requirement for a tool name.

```python
# Before
class CustomTask(Task):
    def __init__(self, task_id, name, task_type, ...):
        super().__init__(
            task_id=task_id,
            name=name,
            is_llm_task=False,  # Hardcoded value
            tool_name=None,
            ...
        )

# After
class CustomTask(Task):
    def __init__(self, task_id, name, task_type, ..., is_llm_task=False):
        super().__init__(
            task_id=task_id,
            name=name,
            is_llm_task=is_llm_task,  # Parameter passed through
            tool_name=None,
            ...
        )
```

When creating a custom task that doesn't use a tool from the registry, you can now set `is_llm_task=True` to bypass the validation that would otherwise require a tool name:

```python
class TextProcessingTask(CustomTask):
    def __init__(self, task_id, name, operation, ...):
        super().__init__(
            task_id=task_id,
            name=name,
            task_type="text_processor",
            is_llm_task=True,  # Bypasses tool_name requirement
            ...
        )
```

## 2. DirectHandlerTask Handler Compatibility

The `DirectHandlerTask.execute()` method now adaptively handles both older and newer handler function signatures:

- Single parameter: `handler(input_data)`
- Two parameters: `handler(task, input_data)`

```python
# Execution logic now adapts to the handler signature
import inspect
handler_sig = inspect.signature(self.handler)

if len(handler_sig.parameters) == 1:
    # Handler takes only the input data
    result = self.handler(input_to_use)
else:
    # Handler takes both task and input data
    result = self.handler(self, input_to_use)
```

This change ensures backward compatibility with existing handler functions while supporting the newer pattern that provides access to the task object.

## 3. Task Dictionary Representation

The `Task.to_dict()` method now returns the task ID with the key `"task_id"` instead of `"id"` for consistency with other parts of the system:

```python
# Before
def to_dict(self):
    return {
        "id": self.id,
        "name": self.name,
        ...
    }

# After
def to_dict(self):
    return {
        "task_id": self.id,
        "name": self.name,
        ...
    }
```

## 4. Workflow Task Retrieval

The `Workflow.get_task()` method now safely returns `None` when a task ID isn't found, rather than raising an exception:

```python
# Before
def get_task(self, task_id):
    if task_id not in self.tasks:
        raise KeyError(f"Task with id {task_id} not found in workflow")
    return self.tasks[task_id]

# After
def get_task(self, task_id):
    return self.tasks.get(task_id)  # Returns None if task not found
```

This allows the workflow engine to handle missing tasks more gracefully, especially when evaluating conditions and determining next tasks.

## Best Practices for Task Handlers

When writing handler functions for `DirectHandlerTask`, we recommend:

1. Using the two-parameter form for new handlers:
   ```python
   def my_handler(task, input_data):
       # task provides context and access to the task object
       # input_data contains the processed input for this execution
       return {"success": True, "result": "Task completed"}
   ```

2. Properly handling both success and error cases:
   ```python
   def robust_handler(task, input_data):
       try:
           # Process input data
           result = process_data(input_data)
           return {"success": True, "result": result}
       except Exception as e:
           return {"success": False, "error": str(e)}
   ```

3. Using the task object to access task metadata when needed:
   ```python
   def metadata_aware_handler(task, input_data):
       log_info(f"Executing task {task.name} (ID: {task.id})")
       # Use task properties like max_retries, etc.
       return {"success": True, "result": "Task completed"}
   ```

These changes collectively improve the robustness and flexibility of the workflow task system while maintaining backward compatibility. 