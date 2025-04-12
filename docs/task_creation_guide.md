# Dawn Framework: Task Creation Guide

## Introduction

Tasks are the fundamental building blocks of Dawn workflows. Each task represents a single unit of work that can be executed, monitored, and connected to other tasks. This guide covers best practices for creating different types of tasks, understanding their lifecycle, and troubleshooting common issues.

## Task Types Overview

The Dawn framework provides several task types to handle different use cases:

1. **Standard Task** (`Task`): For calling registered tools from the tool registry
2. **LLM Task** (`Task` with `is_llm_task=True`): For interacting with language models
3. **Direct Handler Task** (`DirectHandlerTask`): For executing Python functions directly
4. **Join Task** (`Task` with `join_type`): For synchronizing parallel execution paths

## Task Lifecycle

Understanding the task lifecycle is crucial for effective task creation:

1. **Initialization**: Task object created with ID, name, inputs, and configuration
2. **Variable Resolution**: Template variables in input data are resolved
3. **Condition Evaluation**: Task condition is evaluated if present
4. **Execution**: Task logic is executed (tool, LLM call, or direct handler)
5. **Output Processing**: Results captured and standardized
6. **Next Task Selection**: Next task determined based on success/failure
7. **Status Update**: Task status set to completed, failed, or skipped

## Creating Standard Tasks

Standard tasks invoke tools from the tool registry:

```python
from core.task import Task

task = Task(
    task_id="fetch_data",
    name="Fetch Data from API",
    tool_name="api_client",
    input_data={
        "endpoint": "users",
        "params": {"limit": 10}
    },
    next_task_id_on_success="process_data",
    next_task_id_on_failure="handle_api_error"
)
```

### Key Parameters

- `task_id`: Unique identifier for the task within the workflow
- `name`: Human-readable name for the task
- `tool_name`: Name of the registered tool to execute
- `input_data`: Dictionary of input parameters for the tool
- `next_task_id_on_success`: Next task to execute on successful completion
- `next_task_id_on_failure`: Next task to execute if the task fails
- `condition`: Optional expression to determine if the task should execute
- `max_retries`: Number of times to retry the task if it fails
- `parallel`: Whether the task can run in parallel with other tasks

## Creating LLM Tasks

LLM tasks interface with language models for natural language processing:

```python
llm_task = Task(
    task_id="generate_summary",
    name="Generate Text Summary",
    is_llm_task=True,
    input_data={
        "prompt": "Summarize the following text in three bullets:\n\n${content}"
    },
    use_file_search=True,
    file_search_vector_store_ids=["vs_documents"],
    file_search_max_results=3,
    next_task_id_on_success="parse_summary",
    next_task_id_on_failure="handle_llm_error"
)
```

### LLM-Specific Parameters

- `is_llm_task`: Set to `True` to mark as an LLM task
- `use_file_search`: Enable semantic search before LLM processing
- `file_search_vector_store_ids`: List of vector store IDs to search
- `file_search_max_results`: Maximum number of search results to include

### Best Practices for LLM Tasks

1. **Use clear instructions** in your prompts with explicit formatting requirements
2. **Include validation examples** to demonstrate the expected output
3. **Request specific output formats** (like JSON) for easier parsing
4. **Add explicit instructions** on how to handle edge cases
5. **Use system messages** for consistent behavior across different LLM providers

## Creating Direct Handler Tasks

Direct handler tasks execute Python functions without going through the tool registry:

```python
from core.task import DirectHandlerTask

def process_data_handler(input_data):
    """Process data and return results."""
    try:
        data = input_data.get("data", [])
        processed = [item.upper() for item in data if isinstance(item, str)]
        return {
            "success": True,
            "result": processed,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to process data: {str(e)}"
        }

process_task = DirectHandlerTask(
    task_id="process_data",
    name="Process String Data",
    handler=process_data_handler,
    input_data={
        "data": "${fetch_data.output_data.result.items}"
    },
    next_task_id_on_success="format_output",
    next_task_id_on_failure="handle_processing_error"
)
```

### Direct Handler Requirements

1. Handler function must accept a single `input_data` dictionary parameter
2. Handler must return a dictionary with at least a `success` boolean field
3. For successful operations, include a `result` field with the output data
4. For failed operations, include an `error` field with an error message

See the [DirectHandlerTask Pattern](directhandler_pattern.md) documentation for in-depth guidance.

## Creating Join Tasks

Join tasks synchronize parallel execution paths:

```python
join_task = Task(
    task_id="combine_results",
    name="Combine Parallel Results",
    tool_name="data_combiner",
    input_data={
        "results": [
            "${path_a.output_data.result}",
            "${path_b.output_data.result}",
            "${path_c.output_data.result}"
        ]
    },
    join_type="all",  # Wait for all incoming paths
    next_task_id_on_success="process_combined_results"
)
```

### Join Types

- `"all"`: Wait for all incoming paths to complete
- `"any"`: Proceed after any incoming path completes
- `"N"`: (number) Proceed after N incoming paths complete

## Task Input Variable Resolution

Tasks support template variables in input data that are resolved at runtime:

### Basic Variable Resolution

```python
# Reference another task's output
"message": "${previous_task.output_data.result.message}"

# Reference workflow variables
"user_id": "${workflow.variables.user_id}"  

# Reference error information
"error_message": "${error.task_name}" 
```

### Advanced Variable Resolution

```python
# Array indexing
"first_item": "${task.output_data.result.items[0]}"

# Default values
"username": "${user.name | 'Anonymous'}"

# Conditional expressions
"status": "${is_premium == true ? 'Premium' : 'Basic'}"

# Function calls
"upper_name": "${upper(user.name)}"
```

## Task Error Handling

Effective error handling is critical for robust workflows:

### Retry Configuration

```python
task = Task(
    # ... other parameters ...
    max_retries=3,
    retry={
        "backoff_factor": 2,  # Exponential backoff
        "retry_variable_updates": {
            "attempt": "${retry_count + 1}",
            "should_use_fallback": "${retry_count >= 2 ? true : false}"
        }
    }
)
```

### Error Branching

```python
task = Task(
    # ... other parameters ...
    next_task_id_on_error={
        "path_conditions": [
            {"condition": "${contains(error, 'timeout')}", "task_id": "handle_timeout"},
            {"condition": "${contains(error, 'permission')}", "task_id": "handle_permission_error"}
        ],
        "default_task_id": "handle_generic_error"
    }
)
```

## Task Patterns and Recipes

### Pattern: Data Validation

```python
def validate_input(input_data):
    data = input_data.get("data", {})
    errors = []
    
    # Required fields
    for field in ["name", "email", "age"]:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Email validation
    if "email" in data and not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        errors.append("Invalid email format")
    
    # Age validation
    if "age" in data and (not isinstance(data["age"], int) or data["age"] < 0):
        errors.append("Age must be a positive integer")
    
    if errors:
        return {
            "success": True,  # Still consider successful to follow the validation path
            "result": {
                "valid": False,
                "errors": errors,
                "data": data
            },
            "error": None
        }
    else:
        return {
            "success": True,
            "result": {
                "valid": True,
                "data": data
            },
            "error": None
        }

validation_task = DirectHandlerTask(
    task_id="validate_input",
    name="Validate User Input",
    handler=validate_input,
    input_data={"data": "${collect_user_data.output_data.result}"},
    next_task_id_on_success="check_validation_result"
)

# Then add a condition-based task to branch based on validation results
check_task = Task(
    task_id="check_validation_result",
    name="Check Validation Result",
    tool_name="decision_router",
    input_data={"is_valid": "${validate_input.output_data.result.valid}"},
    next_task_id_on_success={
        "path_conditions": [
            {"condition": "${is_valid == true}", "task_id": "process_valid_data"},
            {"condition": "${is_valid == false}", "task_id": "handle_invalid_data"}
        ]
    }
)
```

### Pattern: LLM with Post-Processing

```python
# LLM task to generate structured data
generate_task = Task(
    task_id="generate_data",
    name="Generate Structured Data",
    is_llm_task=True,
    input_data={
        "prompt": """
        Generate a JSON array of 3 user profiles with the following fields:
        - name: Full name
        - age: Integer between 18-65
        - interests: Array of strings (2-4 interests)
        
        Only respond with the JSON array, no other text.
        """
    },
    next_task_id_on_success="parse_json"
)

# Parse JSON using DirectHandlerTask
def parse_json_handler(input_data):
    import json
    import re
    
    llm_output = input_data.get("llm_output", {})
    
    # Extract response string
    if isinstance(llm_output, dict):
        response_str = llm_output.get("response", "")
    else:
        response_str = str(llm_output)
    
    # Extract JSON from possible markdown
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_str)
    if json_match:
        response_str = json_match.group(1)
    
    try:
        parsed_data = json.loads(response_str)
        return {
            "success": True,
            "result": {
                "profiles": parsed_data,
                "count": len(parsed_data) if isinstance(parsed_data, list) else 0
            },
            "error": None
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"JSON parsing error: {str(e)}"
        }

parse_task = DirectHandlerTask(
    task_id="parse_json",
    name="Parse JSON Output",
    handler=parse_json_handler,
    input_data={"llm_output": "${generate_data.output_data}"},
    next_task_id_on_success="process_profiles",
    next_task_id_on_failure="handle_parse_error"
)
```

### Pattern: Parallel Processing with Join

```python
# Initial task
start_task = Task(
    task_id="start_task",
    name="Start Parallel Processing",
    tool_name="data_splitter",
    input_data={"data": "${input_data}"},
    next_task_ids=["process_chunk_1", "process_chunk_2", "process_chunk_3"]  # Parallel paths
)

# Parallel processing tasks
for i in range(1, 4):
    process_task = Task(
        task_id=f"process_chunk_{i}",
        name=f"Process Data Chunk {i}",
        tool_name="data_processor",
        input_data={"chunk": f"${{start_task.output_data.result.chunks[{i-1}]}}"},
        next_task_id_on_success="join_results",
        parallel=True  # Enable parallel execution
    )
    workflow.add_task(process_task)

# Join task to combine results
join_task = Task(
    task_id="join_results",
    name="Join Processing Results",
    tool_name="result_combiner",
    input_data={
        "results": [
            "${process_chunk_1.output_data.result}",
            "${process_chunk_2.output_data.result}",
            "${process_chunk_3.output_data.result}"
        ]
    },
    join_type="all",  # Wait for all processing tasks
    next_task_id_on_success="finalize_results"
)
```

## Testing Tasks

### Unit Testing Direct Handler Tasks

```python
import unittest
from unittest.mock import MagicMock

def process_data_handler(input_data):
    # ... handler implementation ...

class TestProcessDataHandler(unittest.TestCase):
    def test_successful_processing(self):
        # Test with valid input
        result = process_data_handler({"data": ["item1", "item2"]})
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], ["ITEM1", "ITEM2"])
        self.assertIsNone(result["error"])
        
    def test_error_handling(self):
        # Test with invalid input
        result = process_data_handler({"data": None})
        self.assertFalse(result["success"])
        self.assertIn("Failed to process data", result["error"])
```

### Integration Testing with TaskTestHarness

```python
from core.utils.testing import TaskTestHarness

def test_task_with_harness():
    # Create a test harness
    harness = TaskTestHarness()
    
    # Register a mock tool
    def mock_api_client(input_data):
        if input_data.get("endpoint") == "users":
            return {
                "success": True,
                "result": {"items": ["user1", "user2"]}
            }
        return {"success": False, "error": "Invalid endpoint"}
    
    harness.register_mock_tool("api_client", mock_api_client)
    
    # Create and execute the task
    task = Task(
        task_id="fetch_data",
        name="Fetch Data",
        tool_name="api_client",
        input_data={"endpoint": "users"}
    )
    
    result = harness.execute_task(task)
    
    # Verify results
    assert result is True
    assert task.status == "completed"
    assert task.output_data["response"]["items"] == ["user1", "user2"]
```

## Troubleshooting

### Issue: Task Not Executing

**Symptoms:** Task remains in "pending" state or is skipped.

**Potential Causes and Solutions:**
1. **Condition Evaluates to False**: Check the task's condition expression.
2. **Dependencies Not Satisfied**: Ensure all dependencies have completed successfully.
3. **Join Conditions Not Met**: For join tasks, verify all required incoming paths have completed.

### Issue: Variable Resolution Failures

**Symptoms:** Task fails with variable resolution errors, or variables show up as literal strings.

**Potential Causes and Solutions:**
1. **Incorrect Syntax**: Verify the variable reference format: `${task_id.output_data.result}`.
2. **Missing Task**: Ensure the referenced task exists and has executed.
3. **Nested Property Not Found**: Check the property path in the output data structure.
4. **Task Failed**: Verify the referenced task completed successfully.

### Issue: Task Always Fails

**Symptoms:** Task consistently fails despite seemingly valid inputs.

**Potential Causes and Solutions:**
1. **Invalid Tool Name**: Confirm the tool is registered correctly.
2. **Missing Required Parameters**: Check tool documentation for required parameters.
3. **Incorrect Parameter Types**: Verify parameter value types match what the tool expects.
4. **Underlying Service Issue**: Check connections to external services.

### Issue: Unexpected Next Task Selection

**Symptoms:** Workflow follows an unexpected path after task execution.

**Potential Causes and Solutions:**
1. **Misunderstanding Success/Failure Logic**: Review the tool's success criteria.
2. **Wrong Condition Expression**: Check path selection conditions for syntax errors.
3. **Missing Next Task ID**: Ensure all possible outcomes have a defined next task.

## Performance Considerations

1. **Keep Handler Functions Light**: Heavy processing in DirectHandlerTasks can block the workflow engine.
2. **Use Parallel Tasks**: For independent operations, use parallel tasks to improve throughput.
3. **Minimize Database Calls**: Batch database operations where possible.
4. **Optimize LLM Prompts**: Shorter, focused prompts are more efficient and cost-effective.
5. **Add Timeouts**: Use the `timeout_seconds` parameter to prevent hanging on slow operations.

## Security Best Practices

1. **Validate All Inputs**: Always validate inputs, especially for DirectHandlerTasks.
2. **Sanitize LLM Outputs**: Never directly execute LLM-generated code or commands.
3. **Use Least Privilege**: Ensure tools only have the permissions they actually need.
4. **Handle Sensitive Data Carefully**: Avoid logging sensitive information.
5. **Implement Rate Limiting**: Protect against abuse by adding rate limits to tools.

## Conclusion

Creating effective tasks requires understanding the different task types, their lifecycle, and best practices for implementation. By following the guidelines in this documentation, you can build robust, maintainable workflows that handle both the happy path and error conditions gracefully.

## Additional Resources

- [DirectHandlerTask Pattern](directhandler_pattern.md)
- [Error Handling Guide](error_handling.md)
- [Variable Resolution Reference](variable_resolution.md)
- [Testing Workflows and Tasks](testing_workflows_and_tasks.md)
- [LLM Task Optimization](llm_task_optimization.md) 