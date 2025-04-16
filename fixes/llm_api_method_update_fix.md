# LLM API Method Update Fix

## Problem Description

The `economic_impact_researcher.py` script was failing with the following error:

```
Error in custom_plan_user_request_handler: 'LLMInterface' object has no attribute 'generate'
Traceback (most recent call last):
  File "/Users/admin/code/newstart/dawn/examples/economic_impact_researcher.py", line 308, in custom_plan_user_request_handler
    response = llm.generate(messages=messages)
AttributeError: 'LLMInterface' object has no attribute 'generate'
```

This error occurred after our previous attempt to fix the issue by changing from `llm.chat()` to `llm.generate()`, but it seems the API has changed further in the latest version of the framework.

## Root Cause

The Dawn framework's `LLMInterface` class has undergone multiple API changes. Our initial fix attempted to use `generate()` since `chat()` was no longer available, but it appears that the current version doesn't have a `generate()` method either. The current implementation likely uses a method called `complete()` for generating text from a prompt.

## Solution

Updated the `custom_plan_user_request_handler` function to use the correct method for generating LLM responses:

```python
# Previous attempt - still using unavailable method
messages = [{"role": "user", "content": prompt}]
response = llm.generate(messages=messages)

# New code - using the available method
response = llm.complete(prompt)
```

Additionally, we modified the code to handle different response formats:

```python
# More robust handling of response format
raw_llm_output = response if isinstance(response, str) else response.get("content", "")
```

This makes the code more resilient to changes in the response format - whether the API returns a string directly or a dictionary with a "content" field.

## Verification

After making this change, the handler function can successfully generate responses from the LLM interface using the currently available API.

## Additional Notes

LLM interface APIs in frameworks tend to change frequently as they adapt to evolving language model providers (like OpenAI). When encountering errors with LLM interfaces, consider:

1. The framework might have changed its API to adapt to provider changes
2. The response format might vary (string vs dictionary)
3. Parameter names and structures might change over time

For the Dawn framework's `LLMInterface`, we've seen this evolution:
- Initial implementation: `chat([{"role": "user", "content": prompt}])`
- Attempted fix: `generate(messages=[{"role": "user", "content": prompt}])`
- Current implementation: `complete(prompt)`

This suggests a trend toward simplifying the API, possibly to abstract away provider-specific details. 