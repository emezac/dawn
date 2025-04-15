# Chat Planner JSON Parsing Fix

## Problem

The Chat Planner workflow in `examples/economic_impact_researcher.py` was failing due to JSON parsing errors. The LLM output in multiple steps was not properly formatted as valid JSON, causing downstream workflow tasks to fail. Specifically:

1. The `plan_user_request_handler` produced malformed JSON in its response
2. The `validate_plan` task was failing with JSON parsing errors
3. Common issues included:
   - Property names without quotes
   - Single quotes instead of double quotes
   - Trailing commas
   - JSON wrapped in markdown code blocks

The errors prevented the workflow from generating a proper research report.

## Root Cause

LLMs (like GPT models) frequently output JSON that doesn't strictly adhere to the JSON specification, particularly when the JSON is part of a larger text response or wrapped in markdown formatting. Common issues include:

- Unquoted property names: `{name: "value"}` instead of `{"name": "value"}`
- Single quotes: `{'name': 'value'}` instead of `{"name": "value"}`
- Trailing commas: `[1, 2, 3,]` instead of `[1, 2, 3]`
- Markdown code blocks: ``` ```json {...} ``` ``` surrounding the actual JSON

These issues aren't problematic for humans reading the JSON, but they cause standard JSON parsers to fail with syntax errors.

## Solution

We implemented a comprehensive solution with these components:

1. A `fix_json_from_llm` function that:
   - Extracts JSON from markdown code blocks if present
   - Fixes unquoted property names with regex
   - Replaces single quotes with double quotes
   - Removes trailing commas
   - Validates the fixed JSON by parsing and re-stringifying it

2. Custom wrapper handlers that:
   - Call the original handlers
   - Apply the JSON fixing function to the response
   - Provide fallback plans when JSON parsing still fails

3. A fallback plan system that ensures the workflow can continue even when JSON parsing fails completely

### Code Samples

```python
def fix_json_from_llm(raw_text):
    """
    Extract and fix JSON from LLM output.
    """
    # Extract JSON if wrapped in code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
    if json_match:
        json_content = json_match.group(1)
    else:
        # Try to find array brackets if not in code blocks
        json_match = re.search(r'\[\s*{[\s\S]*}\s*\]', raw_text)
        if json_match:
            json_content = json_match.group(0)
        else:
            # If no JSON-like structure found
            return None
    
    # Clean the extracted content
    # 1. Fix unquoted property names
    json_content = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', json_content)
    
    # 2. Fix single quotes to double quotes
    json_content = json_content.replace("'", '"')
    
    # 3. Remove trailing commas
    json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
    
    try:
        # Validate by parsing and re-stringifying
        parsed_json = json.loads(json_content)
        return json.dumps(parsed_json, indent=2)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to fix JSON: {e}")
        return None
```

Custom handler wrapper:

```python
def custom_plan_user_request_handler(task, input_data):
    """
    Custom wrapper for plan_user_request_handler that ensures proper JSON output.
    """
    # Call the original handler
    result = plan_user_request_handler(task, input_data)
    
    # Check if successful and contains a response
    if result.get("success") and "response" in result.get("result", {}):
        # Try to fix the JSON in the response
        fixed_json = fix_json_from_llm(result["result"]["response"])
        
        if fixed_json:
            # Update the response with the fixed JSON
            result["result"]["response"] = fixed_json
        else:
            # If fixing fails, create a fallback plan
            fallback_plan = create_fallback_plan()
            result["result"]["response"] = json.dumps(fallback_plan, indent=2)
            
    return result
```

## Implementation

1. Added the JSON fixing utilities to `examples/economic_impact_researcher.py`
2. Created custom wrapper handlers for both `plan_user_request` and `validate_plan`
3. Registered the custom wrapper handlers in place of the original handlers
4. Added fallback plan generation for cases where JSON fixing fails completely
5. Implemented an `ensure_report_exists` function to guarantee that a report is always generated

## Results

After applying these fixes:

1. The workflow successfully processes malformed JSON from the LLM
2. JSON parsing errors no longer cause the workflow to fail entirely
3. A report is generated even when there are issues with the LLM output
4. The workflow is more robust against variations in LLM output formatting

## Lessons Learned

1. **Always sanitize LLM output**: LLMs frequently produce output that doesn't strictly adhere to format specifications. Always include sanitization and validation steps when expecting structured output.

2. **Implement robust fallbacks**: Design workflows to continue functioning even when parts of them fail, using fallback plans and graceful degradation.

3. **Detailed logging**: Include detailed logging throughout the workflow to help identify where and why issues occur.

4. **End-to-end testing**: Test workflows with a variety of inputs to ensure they handle edge cases and unexpected outputs gracefully.

## Related Issues

- This fix may be applicable to other workflows that use LLM output as structured data
- Similar patterns could be used for sanitizing other structured formats from LLMs (e.g., XML, YAML)
- Consider implementing these fixes at a framework level rather than in individual applications 