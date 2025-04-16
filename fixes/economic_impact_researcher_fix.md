# Economic Impact Researcher Workflow Fix

## Problem Description

The `economic_impact_researcher.py` example was failing with the following error:

```
2025-04-15 22:37:49,436 - economic_impact_researcher - ERROR - An error occurred: 'ServicesContainer' object has no attribute 'llm_interface'
2025-04-15 22:37:49,437 - economic_impact_researcher - ERROR - Traceback (most recent call last):
  File "/Users/admin/code/newstart/dawn/examples/economic_impact_researcher.py", line 597, in main
    llm_interface=services.llm_interface,  # Pass the llm_interface from services
AttributeError: 'ServicesContainer' object has no attribute 'llm_interface'. Did you mean: '_llm_interfaces'?
```

The error occurred when constructing the `WorkflowEngine` instance. The code was attempting to directly access the `llm_interface` attribute of the `ServicesContainer` object, but this attribute doesn't exist publicly.

## Root Cause

The Dawn framework's service container has different access patterns for different types of services:

1. LLM interfaces are stored in a private `_llm_interfaces` dictionary and must be accessed through the `get_llm_interface()` method.
2. Tool and handler registries are available as direct attributes (`tool_registry` and `handler_registry`).

In the original code, we were incorrectly trying to access the LLM interface directly with:

```python
llm_interface=services.llm_interface  # Error: this doesn't exist
```

When we tried to "fix" it by also using getter methods for the tool registry:

```python
tool_registry=services.get_tool_registry()  # Error: this method doesn't exist
```

This caused another error because the service container doesn't have a `get_tool_registry()` method.

## Solution

The correct way to access services in the Dawn framework is as follows:

```python
# LLM interfaces - use getter method
llm = services.get_llm_interface()  # Get the default interface
custom_llm = services.get_llm_interface("gpt4")  # Get a named interface

# Tool and handler registries - direct attribute access
tool_registry = services.tool_registry
handler_registry = services.handler_registry
```

Our fix for the `economic_impact_researcher.py` example was:

```python
# Before (error)
engine = WorkflowEngine(
    workflow=research_workflow,
    llm_interface=services.llm_interface,  # Error: Direct attribute access doesn't work
    tool_registry=services.tool_registry,
    services=services
)

# After (fixed)
engine = WorkflowEngine(
    workflow=research_workflow,
    llm_interface=services.get_llm_interface(),  # Using getter method for LLM
    tool_registry=services.tool_registry,  # Direct attribute access for tool registry
    services=services
)
```

## Verification

After applying the fix, the script runs successfully and generates:

1. The static workflow visualization (`economic_research_static_workflow.png`)
2. The dynamic workflow visualization (`economic_research_dynamic_workflow.pdf`)
3. The dynamic workflow JSON representation (`debug_dynamic_workflow.json`)
4. The final research report (`informe_tarifas_trump.md`)

## Additional Notes

When working with the Dawn framework's `ServicesContainer`, remember:

- Use `get_llm_interface(name='default')` to access LLM interfaces
- Use direct attribute access for `tool_registry` and `handler_registry`
- Use `get_service(name)` for custom registered services 