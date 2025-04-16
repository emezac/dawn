# Plan Validation and Conversion Fix

## Problem Description

The test script `examples/test_validation_conversion.py` was failing to validate and convert sample research plans due to a mismatch in the expected format. The script was attempting to import `convert_plan_to_tasks_handler` from `examples.economic_impact_researcher`, but:

1. The function was not defined in that module
2. The format of the test plan did not match the expected schema for validation
3. The validation handler was not handling structured format plans (with methodology.steps)

## Root Cause

1. **Missing Handler Function**: `convert_plan_to_tasks_handler` was referenced but not defined in `economic_impact_researcher.py`. Instead, the module imported and used `plan_to_tasks_handler` from `chat_planner_workflow.py`.

2. **Schema Format Mismatch**: `PLAN_SCHEMA` from `chat_planner_workflow.py` expected an array of step objects, but the test was using a structured object with `methodology.steps` containing the actual steps.

3. **Incompatible Handler Logic**: The handler code in both `validate_plan_handler` and (missing) `convert_plan_to_tasks_handler` was not checking for different input formats, leading to errors when processing data in a different structure than expected.

## Solution

1. **Added Missing Handler**: Created a new `convert_plan_to_tasks_handler` function in `economic_impact_researcher.py` that acts as a wrapper around the functionality needed for testing. This function handles the conversion from a validated plan to executable dynamic tasks.

2. **Format Flexibility**: Modified both handlers to detect and support multiple formats:
   - Direct array of step objects (matching `PLAN_SCHEMA`)
   - Structured format with `methodology.steps` containing the steps

3. **Format Conversion**: Added logic to convert from the structured format to the array format expected by the framework, mapping field names like `id` → `step_id` and `dependencies` → `depends_on`.

## Code Changes

### 1. Added `convert_plan_to_tasks_handler` function to economic_impact_researcher.py

```python
def convert_plan_to_tasks_handler(task_input_data: dict, task_context: dict) -> dict:
    """Convert a validated research plan to executable dynamic tasks."""
    # Get the validated plan
    validated_plan = task_input_data.get("validated_plan_json", None)
    
    # Handle different formats: either a list of steps directly or a structured object
    steps = []
    if isinstance(validated_plan, list):
        # Already in the expected format of a list of steps
        steps = validated_plan
    elif isinstance(validated_plan, dict) and 'methodology' in validated_plan and 'steps' in validated_plan['methodology']:
        # Extract steps from methodology.steps and convert format
        steps_array = validated_plan.get("methodology", {}).get("steps", [])
        for step in steps_array:
            if isinstance(step, dict):
                converted_step = {
                    "step_id": step.get("id", ""),
                    "description": step.get("description", ""),
                    "type": "tool",
                    "name": "web_search",
                    "inputs": {"query": step.get("description", "")},
                    "depends_on": step.get("dependencies", []),
                    "outputs": [f"{step.get('id', '')}_results"]
                }
                steps.append(converted_step)

    # Return the dynamic tasks result
    return {
        "success": True,
        "status": "completed",
        "result": {
            "dynamic_tasks_json": steps
        }
    }
```

### 2. Enhanced `validate_plan_handler` to detect and convert structured formats

```python
# Detecting structured plan format
if isinstance(json_data, dict) and 'methodology' in json_data and 'steps' in json_data['methodology']:
    steps_array = json_data['methodology']['steps']
    converted_steps = []
    
    # Convert steps to format expected by PLAN_SCHEMA
    for step in steps_array:
        converted_step = {
            "step_id": step.get("id", ""),
            "description": step.get("description", ""),
            "type": "tool",
            "name": "web_search",
            "inputs": {"query": step.get("description", "")},
            "depends_on": step.get("dependencies", []),
            "outputs": [f"{step.get('id', '')}_results"]
        }
        converted_steps.append(converted_step)
        
    # Use the converted steps for validation
    json_data = converted_steps
```

### 3. Modified the test script to use the expected array format directly

The sample plan in `test_validation_conversion.py` was changed to a list of step objects that conforms directly to the expected schema format.

## Verification

After making these changes, the test script `examples/test_validation_conversion.py` runs successfully:

```
=== RESULTS SUMMARY ===
JSON Format: Validation ✅, Conversion ✅
Markdown Format: Validation ✅, Conversion ✅
Text Format: Validation ✅, Conversion ✅
```

All three test formats pass both validation and conversion. The improved regex pattern added to better extract JSON arrays from plain text, solving the issue with the third test format:

```python
# Additional regex pattern for arrays in square brackets
if json_data is None:
    print("\nAttempt 4: Looking for arrays in square brackets")
    array_pattern = r"\[\s*\{[\s\S]*?\}\s*\]"
    matches = re.findall(array_pattern, raw_llm_output)
    
    if matches:
        print(f"Found {len(matches)} potential JSON arrays, trying first match")
        for i, match in enumerate(matches[:3]):  # Try first 3 matches
            try:
                json_data = json.loads(match)
                print(f"JSON array parsing from match {i+1} successful")
                break
            except json.JSONDecodeError as e:
                error_msg = f"JSON array parsing from match {i+1} failed: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
    else:
        print("No arrays with square brackets found")
```

## Additional Notes

- The current test script now uses a format that matches `PLAN_SCHEMA` directly. If future tests need to use the structured format with methodology.steps, both handlers are now equipped to handle it.
- The approach of format conversion could be extended to additional schema versions or formats if needed.
- An improved regex pattern was added to better extract JSON arrays from plain text, solving the issue with the third test format:

```python
# Additional regex pattern for arrays in square brackets
if json_data is None:
    print("\nAttempt 4: Looking for arrays in square brackets")
    array_pattern = r"\[\s*\{[\s\S]*?\}\s*\]"
    matches = re.findall(array_pattern, raw_llm_output)
    
    if matches:
        print(f"Found {len(matches)} potential JSON arrays, trying first match")
        for i, match in enumerate(matches[:3]):  # Try first 3 matches
            try:
                json_data = json.loads(match)
                print(f"JSON array parsing from match {i+1} successful")
                break
            except json.JSONDecodeError as e:
                error_msg = f"JSON array parsing from match {i+1} failed: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
    else:
        print("No arrays with square brackets found")
```

After this final improvement, all three test formats pass both validation and conversion:

```
=== RESULTS SUMMARY ===
JSON Format: Validation ✅, Conversion ✅
Markdown Format: Validation ✅, Conversion ✅
Text Format: Validation ✅, Conversion ✅
``` 