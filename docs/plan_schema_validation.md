# Plan Schema Validation

This document outlines the JSON schema validation implemented for the "Think & Analyze" planning component in the chat-driven workflow system.

## Overview

The planning component of our workflow system generates a structured execution plan in JSON format. To ensure the plan adheres to our expected structure and contains all required information, we've implemented schema validation using the Python `jsonschema` library.

## Schema Definition

The schema is defined as a Python dictionary in `examples/chat_planner_workflow.py`:

```python
PLAN_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "step_id": {"type": "string", "minLength": 1, "description": "Unique identifier for the step."},
            "description": {"type": "string", "description": "Natural language description of the step's purpose."},
            "type": {"type": "string", "enum": ["tool", "handler"], "description": "The type of capability to execute."},
            "name": {"type": "string", "minLength": 1, "description": "The exact name of the tool or handler."},
            "inputs": {
                "type": "object",
                "description": "Key-value pairs for inputs. Values can be literals or variable references like ${...}.",
                "additionalProperties": True  # Allow any properties
            },
            "outputs": {
                "type": "array",
                "items": {"type": "string"},
                "description": "(Optional) List of expected output keys from this step."
            },
            "depends_on": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of step_ids this step directly depends on. Empty for the first step."
            }
        },
        "required": ["step_id", "description", "type", "name", "inputs", "depends_on"],
        "additionalProperties": False  # Disallow extra properties at the step level
    },
    "description": "A list of steps defining the execution plan."
}
```

## Enforced Constraints

The schema enforces the following constraints on the plan:

1. **Structure**: The plan must be a JSON array of step objects.
2. **Required Fields**: Each step must contain all the required fields: `step_id`, `description`, `type`, `name`, `inputs`, and `depends_on`.
3. **Field Types**: Fields must be of the correct type (e.g., `inputs` must be an object, `depends_on` must be an array).
4. **Enumerated Values**: The `type` field must be either "tool" or "handler".
5. **String Length**: Fields like `step_id` and `name` must be non-empty strings.
6. **Additional Properties**: Step objects cannot contain properties beyond those defined in the schema.

## Implementation in Validation Handler

The `validate_plan_handler` in `examples/chat_planner_workflow.py` uses the schema as follows:

```python
# After parsing the JSON from the LLM output
try:
    jsonschema.validate(instance=plan, schema=PLAN_SCHEMA)
    logger.info("Plan successfully validated against JSON schema.")
except jsonschema.exceptions.ValidationError as schema_err:
    validation_errors.append(f"JSON Schema validation failed: {schema_err.message} (Path: {'/'.join(map(str, schema_err.path))})")
    logger.warning(f"Schema validation failed: {schema_err.message}")
```

## Additional Semantic Validation

Beyond the basic schema validation, the handler also performs semantic validation that cannot be expressed in JSON Schema:

1. **Duplicate Step IDs**: Checks that each `step_id` is unique within the plan.
2. **Tool/Handler Existence**: Verifies that the specified tools and handlers exist in the system.
3. **Dependency Validation**: Ensures all referenced dependencies exist and there are no self-dependencies.
4. **Input Variable References**: Validates that variable references in step inputs (using the `${...}` syntax) are properly formatted and refer to existing steps:
   - Recognizes and validates `${user_prompt}` as the initial workflow input.
   - Validates references to outputs from other steps (`${step_id.output.field_path}`):
     - Checks that the referenced step exists in the plan
     - Ensures that referenced steps are properly listed in the `depends_on` array
     - Validates the reference format follows the expected pattern

## Error Handling

When validation fails, the handler collects detailed error messages that:

1. Identify the specific validation that failed
2. Pinpoint the location (step index/ID) of the error
3. Provide a descriptive message explaining the issue

These messages are returned to the workflow engine, which can then take appropriate action (e.g., retry with a fixed prompt, notify the user).

### Enhanced Error Handling Features

The validation system includes several advanced error handling capabilities:

1. **Error Categorization**: Errors are categorized by type (JSON parsing, schema validation, tool/handler existence, dependencies, input references) to provide more targeted feedback.

2. **Recovery Attempts**: For malformed JSON, the system attempts to recover by:
   - Trying different parsing methods
   - Applying common fixes (adding missing quotes, fixing brackets, etc.)
   - Converting single-object plans to lists when possible

3. **User-Friendly Error Messages**: Error responses include a formatted, user-friendly error message that:
   - Summarizes the number and types of errors
   - Highlights the most critical issue
   - Provides example errors (limited to a reasonable number)
   - Offers specific suggestions for fixing the issues

4. **Graceful Degradation**: The system proceeds with as much validation as possible even when early validations fail, gathering all potential issues in one pass.

5. **Warning System**: Non-critical issues are flagged as warnings, allowing plans with minor issues to proceed with caution.

### Sample Error Response

When validation fails, the handler returns a comprehensive error response structure:

```python
{
    "success": False,
    "error": "Plan validation failed.",
    "validation_errors": [detailed_error_list],  # All validation errors found
    "validation_warnings": [warning_list],       # Non-critical issues
    "error_summary": {                           # Categorized error information
        "has_json_error": True/False,
        "has_schema_error": True/False,
        "has_tool_handler_error": True/False,
        "has_dependency_error": True/False,
        "has_input_reference_error": True/False,
        "error_count": 3,                        # Total number of errors
        "most_critical_error": "Critical error message", 
        "example_errors": ["Error 1", "Error 2", "Error 3"]
    },
    "user_friendly_error": "Formatted error message for display", 
    "parsed_plan": [partially_parsed_plan]       # Whatever could be parsed
}
```

## Benefits of Schema Validation

Using JSON Schema validation provides several benefits:

1. **Self-Documentation**: The schema itself serves as documentation for the expected structure of the plan.
2. **Clear Error Messages**: Schema validation produces specific, actionable error messages.
3. **Separation of Concerns**: Basic structure validation is handled by the schema, while semantic validation is handled by custom code.
4. **Future-Proofing**: As the plan format evolves, the schema can be updated to reflect new requirements.

## Future Improvements

Potential improvements to the validation system include:

1. **Expanded Output Field Validation**: Enhance the input variable reference validation to check if referenced output fields are likely available based on the tool/handler's known output structure.
2. **Cyclic Dependency Detection**: Detect cyclic dependencies in the task graph (beyond simple self-dependencies).
3. **Schema Versioning**: Add schema versioning to support multiple versions of the plan format.
4. **External Schema File**: Move the schema to an external JSON file for easier maintenance and sharing with other components. 