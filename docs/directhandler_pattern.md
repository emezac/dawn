# Dawn Framework: DirectHandlerTask Pattern

## Overview

The `DirectHandlerTask` pattern is a powerful approach for defining workflow tasks that need direct access to Python functions without going through the tool registry. This pattern enables more efficient workflow development, better type safety, and simplified testing.

## Key Benefits

- **Direct Python Function Execution**: Call Python functions directly without tool registry overhead
- **Type Safety**: Improved IDE support with direct function references
- **Simplified Testing**: Easier to mock and test through direct function references
- **Better Error Handling**: Consistent error propagation and clearer debugging
- **Reduced Boilerplate**: No need to register functions as tools for internal operations

## When to Use DirectHandlerTask

Use the `DirectHandlerTask` pattern when:

1. The function is specific to a single workflow and doesn't need to be shared
2. You need better IDE support for function parameters and return values
3. You're parsing or transforming data between tasks (e.g., parsing JSON from LLM outputs)
4. You're implementing workflow-specific business logic
5. You need to handle variables that might not be resolved properly

## Basic Usage

```python
from core.task import DirectHandlerTask

# Define your handler function
def parse_json_output(input_data):
    """Parse JSON output from an LLM task."""
    try:
        llm_output = input_data.get("llm_output", "{}")
        # Handle different input types
        if isinstance(llm_output, dict) and "response" in llm_output:
            text_to_parse = llm_output.get("response", "")
        else:
            text_to_parse = llm_output
            
        # Try to parse as JSON
        import json
        result = json.loads(text_to_parse)
        return {
            "success": True,
            "result": result,
            "error": None
        }
    except json.JSONDecodeError as e:
        # Return a fallback structure on error
        return {
            "success": True,  # Still consider this a "success" to continue workflow
            "result": {
                "fallback": "true",
                "error_parsing": str(e),
                "original_text": text_to_parse[:100] + "..." if len(text_to_parse) > 100 else text_to_parse
            },
            "error": None  # Don't trigger error path
        }

# Create the DirectHandlerTask
parse_task = DirectHandlerTask(
    task_id="parse_llm_output",
    name="Parse LLM JSON Output",
    handler=parse_json_output,
    input_data={
        "llm_output": "${previous_llm_task.output_data}"
    },
    next_task_id_on_success="next_task",
    next_task_id_on_failure="error_handler"
)

# Add to workflow
workflow.add_task(parse_task)
```

## Best Practices

### 1. Standardized Return Format

All handler functions should return a dictionary with the standardized format:

```python
{
    "success": bool,      # Whether the operation was successful
    "result": Any,        # The result data (for successful operations)
    "error": str          # Error message (for failed operations)
}
```

### 2. Robust Error Handling

Always include proper error handling in your handler functions:

```python
def robust_handler(input_data):
    try:
        # Main logic here
        result = process_data(input_data)
        return {
            "success": True,
            "result": result,
            "error": None
        }
    except Exception as e:
        # Log the error
        logger.error(f"Error in handler: {str(e)}")
        # Return standardized error response
        return {
            "success": False,
            "error": f"Failed to process data: {str(e)}"
        }
```

### 3. Handle Unresolved Variables

Include fallbacks for unresolved template variables:

```python
def handle_with_fallbacks(input_data):
    # Get input with fallback
    user_input = input_data.get("user_input", "")
    
    # Check for unresolved variables
    if "${" in user_input:
        # Handle the unresolved variable
        user_input = "Default value"
    
    # Continue processing
    # ...
```

### 4. Use Clear Function and Variable Names

Name your handler functions and tasks descriptively:

```python
# Good
def extract_entity_names(input_data):
    # ...

# Better than
def process_data(input_data):
    # ...
```

### 5. Keep Handler Functions Focused

Each handler function should do one thing well:

```python
# Good - Separate handlers for each step
def parse_json(input_data):
    # Only parse JSON
    
def validate_data(input_data):
    # Only validate the data structure
    
def transform_data(input_data):
    # Only transform the data

# Bad - One big handler doing multiple things
def parse_validate_and_transform(input_data):
    # Does too many things
```

## Advanced Usage

### Conditional Task Execution

You can use the `condition` parameter to conditionally execute tasks:

```python
validation_task = DirectHandlerTask(
    task_id="validate_data",
    name="Validate Data Structure",
    handler=validate_data_handler,
    input_data={
        "data": "${parse_json.output_data.result}"
    },
    condition="${parse_json.output_data.result.needs_validation == true}",
    next_task_id_on_success="process_data"
)
```

### Adding Custom Debug Information

You can add extra debugging information to your handler responses:

```python
def handler_with_debug(input_data):
    import time
    start_time = time.time()
    
    # Process data
    result = process_data(input_data)
    
    # Calculate processing time
    processing_time = time.time() - start_time
    
    return {
        "success": True,
        "result": result,
        "debug_info": {
            "processing_time_ms": processing_time * 1000,
            "input_size": len(str(input_data)),
            "output_size": len(str(result))
        }
    }
```

### Task Dependencies

While the `DirectHandlerTask` doesn't support the `dependencies` parameter directly, you can achieve the same effect through input variable references:

```python
# This task effectively depends on both task_a and task_b
combined_task = DirectHandlerTask(
    task_id="combined_processor",
    name="Process Combined Results",
    handler=combined_handler,
    input_data={
        "result_a": "${task_a.output_data.result}",
        "result_b": "${task_b.output_data.result}"
    }
)
```

## Common Patterns

### 1. JSON Parsing Pattern

Use `DirectHandlerTask` to parse LLM-generated JSON:

```python
def parse_llm_json(input_data):
    import json
    import re
    
    llm_output = input_data.get("llm_output", "")
    if isinstance(llm_output, dict):
        llm_output = llm_output.get("response", "")
        
    # Extract JSON if wrapped in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', llm_output)
    if json_match:
        llm_output = json_match.group(1)
        
    try:
        result = json.loads(llm_output)
        return {"success": True, "result": result}
    except json.JSONDecodeError:
        # Fallback structure
        return {
            "success": True,
            "result": {"error": "Failed to parse JSON", "fallback": True}
        }
```

### 2. Decision Logic Pattern

Use `DirectHandlerTask` for complex decision-making:

```python
def determine_next_action(input_data):
    risk_level = input_data.get("risk_level", "UNKNOWN")
    findings = input_data.get("findings", [])
    
    # Determine appropriate action based on risk level
    if risk_level == "Critical" or risk_level == "High":
        action = "ACTION_REQUIRED"
    elif risk_level == "Medium":
        action = "REVIEW_RECOMMENDED"
    else:
        action = "LOG_INFO"
        
    # Check for specific concerns that might escalate the action
    for finding in findings:
        if "HIPAA" in finding.get("framework", "") and "PHI" in finding.get("finding", ""):
            action = "ACTION_REQUIRED"  # Override for HIPAA PHI issues
            
    return {
        "success": True,
        "result": {
            "action": action,
            "original_risk": risk_level,
            "reason": f"Determined based on {risk_level} risk level and {len(findings)} findings"
        }
    }
```

### 3. Variable Resolution Checking Pattern

Use `DirectHandlerTask` to handle potential unresolved variables:

```python
def check_resolved_variables(input_data):
    message = input_data.get("message", "")
    
    # Check if variables were properly resolved
    if "${" in message:
        # Replace unresolved variables with sensible defaults
        message = re.sub(r'\${[^}]+}', '[NOT AVAILABLE]', message)
        
    return {
        "success": True,
        "result": {
            "cleaned_message": message,
            "had_unresolved_vars": "${" in input_data.get("message", "")
        }
    }
```

## Troubleshooting

### Issue: Task Always Takes Error Path

If your task always takes the error path despite seeming successful:

1. Verify your handler returns `"success": True` for successful operations
2. Check for incorrect naming in variable references
3. Make sure your handler isn't raising uncaught exceptions

### Issue: Variables Not Resolved

If your task has issues with variable resolution:

1. Check the syntax of your variable references (e.g., `${task_id.output_data.result}`)
2. Add fallback handling for potentially unresolved variables
3. Log the input_data at the start of your handler to debug

### Issue: Task Dependencies Not Working

If task dependencies don't seem to work:

1. Remember that `DirectHandlerTask` doesn't support the `dependencies` parameter directly
2. Use variable references in `input_data` to create implicit dependencies
3. Make sure your workflow execution order allows for dependencies to be resolved

## Complete Example

Here's a complete example of a pattern using multiple `DirectHandlerTask` instances:

```python
def build_workflow():
    workflow = Workflow(workflow_id="example_workflow", name="Example Pattern")
    
    # Step 1: LLM task to generate JSON
    generate_task = Task(
        task_id="generate_data",
        name="Generate Data with LLM",
        is_llm_task=True,
        input_data={
            "prompt": "Generate a JSON object with fields 'name', 'age', and 'interests'. Use only JSON in your response."
        },
        next_task_id_on_success="parse_json",
        next_task_id_on_failure="handle_error"
    )
    workflow.add_task(generate_task)
    
    # Step 2: Parse the JSON output
    def parse_json_handler(input_data):
        import json
        try:
            llm_output = input_data.get("llm_output", {}).get("response", "{}")
            parsed = json.loads(llm_output)
            return {"success": True, "result": parsed}
        except Exception as e:
            return {"success": True, "result": {"error": str(e), "fallback": True}}
    
    parse_task = DirectHandlerTask(
        task_id="parse_json",
        name="Parse JSON Output",
        handler=parse_json_handler,
        input_data={"llm_output": "${generate_data.output_data}"},
        next_task_id_on_success="validate_data"
    )
    workflow.add_task(parse_task)
    
    # Step 3: Validate the data
    def validate_data_handler(input_data):
        data = input_data.get("data", {})
        validation_errors = []
        
        # Check required fields
        for field in ["name", "age", "interests"]:
            if field not in data:
                validation_errors.append(f"Missing required field: {field}")
                
        # Check field types
        if "age" in data and not isinstance(data["age"], (int, float)):
            validation_errors.append("Age must be a number")
            
        if "interests" in data and not isinstance(data["interests"], list):
            validation_errors.append("Interests must be a list")
            
        if validation_errors:
            return {
                "success": True,
                "result": {
                    "is_valid": False,
                    "errors": validation_errors,
                    "data": data
                }
            }
        else:
            return {
                "success": True,
                "result": {
                    "is_valid": True,
                    "data": data
                }
            }
    
    validate_task = DirectHandlerTask(
        task_id="validate_data",
        name="Validate Data Structure",
        handler=validate_data_handler,
        input_data={"data": "${parse_json.output_data.result}"},
        next_task_id_on_success="determine_action"
    )
    workflow.add_task(validate_task)
    
    # Step 4: Determine action based on validation
    def determine_action_handler(input_data):
        validation_result = input_data.get("validation_result", {})
        is_valid = validation_result.get("is_valid", False)
        
        if is_valid:
            return {
                "success": True,
                "result": {
                    "action": "PROCESS_DATA",
                    "message": "Data is valid and ready for processing"
                }
            }
        else:
            errors = validation_result.get("errors", [])
            return {
                "success": True,
                "result": {
                    "action": "REQUEST_CORRECTION",
                    "message": f"Data validation failed with {len(errors)} errors",
                    "errors": errors
                }
            }
    
    action_task = DirectHandlerTask(
        task_id="determine_action",
        name="Determine Next Action",
        handler=determine_action_handler,
        input_data={"validation_result": "${validate_data.output_data.result}"},
        next_task_id_on_success="final_task"
    )
    workflow.add_task(action_task)
    
    # Step 5: Final task based on action
    def final_task_handler(input_data):
        action_data = input_data.get("action_data", {})
        action = action_data.get("action", "UNKNOWN")
        message = action_data.get("message", "No message provided")
        
        return {
            "success": True,
            "result": {
                "workflow_completed": True,
                "final_action": action,
                "final_message": message,
                "timestamp": time.time()
            }
        }
    
    final_task = DirectHandlerTask(
        task_id="final_task",
        name="Final Processing Step",
        handler=final_task_handler,
        input_data={"action_data": "${determine_action.output_data.result}"}
    )
    workflow.add_task(final_task)
    
    # Error handler task
    def error_handler_func(input_data):
        error = input_data.get("error", "Unknown error")
        return {
            "success": True,
            "result": {
                "error_handled": True,
                "original_error": error,
                "resolution": "Error logged and notification sent"
            }
        }
    
    error_task = DirectHandlerTask(
        task_id="handle_error",
        name="Handle Error Condition",
        handler=error_handler_func,
        input_data={"error": "${error}"}
    )
    workflow.add_task(error_task)
    
    return workflow
```

## Conclusion

The `DirectHandlerTask` pattern provides a powerful way to extend your workflows with custom Python logic without the overhead of tool registration. By following the best practices outlined in this guide, you can create more maintainable, testable, and robust workflows that handle a wide variety of scenarios. 