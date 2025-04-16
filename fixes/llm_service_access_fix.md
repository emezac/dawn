# LLM Service Access Method Fix

## Problem Description

The `economic_impact_researcher.py` script was failing with the following error:

```
Error in custom_plan_user_request_handler: "No service registered with name 'llm'"
Traceback (most recent call last):
  File "/Users/admin/code/newstart/dawn/examples/economic_impact_researcher.py", line 304, in custom_plan_user_request_handler
    llm = services.get_service("llm")
  File "/Users/admin/code/newstart/dawn/core/services.py", line 147, in get_service
    raise KeyError(f"No service registered with name '{service_name}'")
KeyError: "No service registered with name 'llm'"
```

This error occurred in the `custom_plan_user_request_handler` function when it attempted to access the LLM service using `services.get_service("llm")`.

## Root Cause

The Dawn framework doesn't register the LLM interface as a standard service with name "llm". Instead, it's registered through a special method `register_llm_interface()` and should be accessed using `get_llm_interface()`.

In the code, the LLM interface was registered in the `main()` function with:
```python
services.register_llm_interface(llm_interface)
```

However, in the handler function, it was trying to access it with:
```python
llm = services.get_service("llm")
```

Which is the wrong accessor method for LLM interfaces in the Dawn framework.

## Solution

Updated the `custom_plan_user_request_handler` function to use the correct method to access the LLM interface:

```python
# Old code - incorrect access method
services = get_services()
llm = services.get_service("llm")

# New code - correct access method
services = get_services()
llm = services.get_llm_interface()
```

This change ensures that the handler properly accesses the LLM interface that was registered in the `main()` function.

## Verification

After making this change, the handler function can successfully access the LLM interface and make API calls to generate the research plan.

## Additional Notes

The Dawn framework has a special pattern for registering and accessing LLM interfaces that's different from standard services. When working with LLM components in the framework, always use:

- `services.register_llm_interface(llm_instance)` for registration
- `services.get_llm_interface()` for accessing

This specialized accessor pattern provides better type safety and default handling than the generic service registry. 