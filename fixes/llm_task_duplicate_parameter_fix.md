# Fix for Duplicate Prompt Parameter in LLM Tasks

## Issue Description

An error was occurring when running workflows that contain LLM tasks:

```
ERROR: Engine error executing task 'task_1_analyze_risk_llm': core.llm.interface.LLMInterface.execute_llm_call() got multiple values for keyword argument 'prompt'
```

This error was specifically affecting the Smart Compliance Workflow example, causing tasks to fail after multiple retry attempts.

## Root Cause

In the `WorkflowEngine.run` method, when executing LLM tasks, the code was passing the `prompt` parameter twice to the `execute_llm_call` function:

1. First, it extracted `prompt` from `resolved_input` and passed it explicitly as a named parameter
2. Then, it also passed the entire `resolved_input` dictionary (which still contained the `prompt` key) as keyword arguments using the `**` operator

Python does not allow a function to receive the same parameter twice, which was causing the error.

Original problematic code:

```python
prompt = resolved_input.get("prompt", "")
if not prompt: raise ValueError("Missing 'prompt' for LLM task.")
output = self.llm_interface.execute_llm_call(
    prompt=prompt, # Pass required args
    **resolved_input # Pass other resolved inputs as potential kwargs
)
```

## Solution

The solution was to create a copy of the `resolved_input` dictionary and remove the `prompt` key before passing it as keyword arguments:

```python
prompt = resolved_input.get("prompt", "")
if not prompt: raise ValueError("Missing 'prompt' for LLM task.")

# Create a copy of resolved_input without the prompt key to avoid passing it twice
other_params = resolved_input.copy()
other_params.pop("prompt", None)

output = self.llm_interface.execute_llm_call(
    prompt=prompt, # Pass required args
    **other_params # Pass other resolved inputs as potential kwargs
)
```

This ensures that the `prompt` parameter is only passed once to the function.

## Related Components

- `core/engine.py` - Contains the `WorkflowEngine` class with the LLM task execution logic
- `examples/smart_compliance_workflow.py` - An example workflow that was failing due to this issue

## Testing

After applying this fix, the Smart Compliance Workflow should run without errors related to duplicate parameters. 