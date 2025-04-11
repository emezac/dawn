# Best Practices for Task Output and Variable Resolution

This guide documents the best practices for handling task outputs and variable resolution in Dawn workflows, based on improvements made to the framework in April 2025.

## Table of Contents

1. [Task Output Structure](#task-output-structure)
2. [Variable Resolution](#variable-resolution)
3. [Error Handling](#error-handling)
4. [JSON Parsing](#json-parsing)
5. [DirectHandlerTask Usage](#directhandlertask-usage)
6. [Patterns to Follow](#patterns-to-follow)
7. [Patterns to Avoid](#patterns-to-avoid)

## Task Output Structure

All tasks should return output in a standardized format:

```python
{
    # Required status fields
    "success": True,            # Boolean indicating success/failure
    "status": "success",        # String status: "success", "error", or "warning"
    
    # For successful tasks - ONE of these (both is better for compatibility)
    "result": { ... },          # The main result data
    "response": { ... },        # Alternative name for result data (for LLM tasks)
    
    # For failed tasks
    "error": "Error message",   # Human-readable error description
    "error_type": "ErrorType",  # Optional type of error
}
```

### Example of a well-structured task output:

```python
def my_task_handler(input_data):
    try:
        # Process data
        result = process_data(input_data)
        
        # Return standardized success response
        return {
            "success": True,
            "status": "success",
            "result": result,
            "response": result  # Include both for compatibility
        }
    except Exception as e:
        # Return standardized error response
        return {
            "success": False,
            "status": "error",
            "error": f"Failed to process data: {str(e)}",
            "error_type": type(e).__name__
        }
```

## Variable Resolution

### Dot Notation

Always use dot notation rather than bracket notation:

```python
# Good
${task_name.output_data.result.field}

# Avoid
${task_name.output_data["result"]["field"]}
```

### Default Values

Always provide a default value using the pipe syntax:

```python
# Good - with a default
${task_name.output_data.result.field | "default value"}

# Also good - with an empty string default
${task_name.output_data.result.field | ""}

# Less robust - no default provided
${task_name.output_data.result.field}
```

### Nested Paths

For deeply nested paths, break into logical segments:

```python
# Good - descriptive, manageable segments
${analysis_task.output_data.result.recommendations | []}

# Avoid - excessively complex paths
${analysis_task.output_data.result.analysis.details.recommendations.items[0].text}
```

## Error Handling

### Use extract_task_output

Always use the `extract_task_output` utility function to handle task outputs:

```python
# In task handlers or workflow logic
output = extract_task_output(task_output)

# With a specific field path
summary = extract_task_output(task_output, "result.summary")

# With nested path
recommendations = extract_task_output(task_output, "result.recommendations")
```

### Extract and Validate Data

Always extract and validate data from task inputs:

```python
def my_handler(input_data):
    # Extract with defaults
    document_content = input_data.get("document_content", "")
    max_results = input_data.get("max_results", 5)
    
    # Validate
    if not document_content:
        return {
            "success": False,
            "error": "Missing document content"
        }
    
    # Process valid data
    # ...
```

## JSON Parsing

### Always Add a JSON Parsing Task After LLM Tasks

```python
# LLM Task
llm_task = Task(
    task_id="llm_analysis_task",
    name="Analyze Document with LLM",
    is_llm_task=True,
    input_data={
        "prompt": "Analyze this document..."
    },
    next_task_id_on_success="parse_llm_output_task",
)

# JSON Parsing Task
parsing_task = DirectHandlerTask(
    task_id="parse_llm_output_task",
    name="Parse LLM Analysis Output",
    handler=parse_json_output,
    input_data={
        "llm_output": "${llm_analysis_task.output_data}"
    },
    next_task_id_on_success="next_step_task",
)
```

### Standard JSON Parser Implementation

```python
def parse_json_output(input_data):
    """Parse JSON output from LLM task"""
    llm_output = input_data.get("llm_output", "{}")
    
    # Handle dictionary with response field
    if isinstance(llm_output, dict) and "response" in llm_output:
        llm_output = llm_output.get("response", "{}")
            
    # Handle string output
    if isinstance(llm_output, str):
        try:
            # Try to parse as JSON
            result = json.loads(llm_output)
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except json.JSONDecodeError as e:
            # Try to extract JSON with regex
            import re
            json_pattern = r'{.*}'
            match = re.search(json_pattern, llm_output, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(0))
                    return {
                        "success": True,
                        "result": result,
                        "error": None
                    }
                except:
                    pass
            
            # Return the original text if parsing fails
            return {
                "success": False,
                "result": {
                    "text": llm_output,
                    "message": "Failed to parse as JSON"
                },
                "error": f"Failed to parse JSON: {str(e)}"
            }
    
    # For other input types
    return {
        "success": False,
        "result": {
            "text": str(llm_output)
        },
        "error": "Input was not in expected format"
    }
```

## DirectHandlerTask Usage

### Creating DirectHandlerTasks

```python
task = DirectHandlerTask(
    task_id="process_data_task",
    name="Process Data",
    handler=process_data_handler,
    input_data={
        "data": "${previous_task.output_data.result | ''}",
        "options": {"max_items": 10}
    },
    next_task_id_on_success="next_task",
    next_task_id_on_failure="error_handler_task",
)
```

### No Dependencies Parameter

DirectHandlerTask does not support the `dependencies` parameter:

```python
# INCORRECT - will cause errors
task = DirectHandlerTask(
    task_id="task_id",
    handler=my_handler,
    dependencies=["previous_task"]  # This will cause issues
)

# CORRECT - check and remove dependencies
for task_id, task in workflow.tasks.items():
    if hasattr(task, 'is_direct_handler') and task.is_direct_handler:
        if hasattr(task, 'dependencies'):
            delattr(task, 'dependencies')
```

## Patterns to Follow

### 1. Always Check For and Handle Empty Results

```python
def check_results_handler(input_data):
    search_results = input_data.get("search_results", [])
    
    # Handle empty results
    if not search_results or len(search_results) == 0:
        return {
            "success": True,  # Still successful, just empty
            "result": {
                "has_results": False,
                "default_summary": "No search results were found."
            }
        }
    
    # Process normal results
    # ...
```

### 2. Add Fallbacks for Important Data Paths

```python
def generate_report_handler(input_data):
    # Extract primary data with fallbacks
    primary_data = extract_task_output(
        input_data.get("primary_task_output"), 
        "result.data"
    ) or {}
    
    # Extract backup data as fallback
    backup_data = extract_task_output(
        input_data.get("backup_task_output"), 
        "result.data"
    ) or {}
    
    # Use primary if available, otherwise fallback to backup
    data_to_use = primary_data if primary_data else backup_data
    
    # ...
```

### 3. Use Fallback Task Paths

```python
task = Task(
    task_id="search_task",
    name="Search Documents",
    tool_name="search",
    input_data={"query": "search query"},
    next_task_id_on_success="process_results_task",
    next_task_id_on_failure="fallback_search_task",  # Fallback path
)

fallback_task = DirectHandlerTask(
    task_id="fallback_search_task",
    name="Fallback Search Handler",
    handler=fallback_search_handler,
    next_task_id_on_success="process_results_task",  # Rejoin main flow
)
```

## Patterns to Avoid

### 1. Assuming Task Output Structure

```python
# BAD - assumes structure without checking
def risky_handler(input_data):
    # Will fail if previous_task.output_data doesn't have the expected structure
    first_item = input_data["previous_results"]["items"][0]
    # ...

# GOOD - checks structure at each level
def safe_handler(input_data):
    previous_results = input_data.get("previous_results", {})
    items = previous_results.get("items", [])
    first_item = items[0] if items else None
    
    if not first_item:
        # Handle missing data case
        # ...
```

### 2. Direct Indexing Without Checks

```python
# BAD - direct indexing of lists is risky
${task.output_data.result.items[0].name}

# GOOD - use extract_task_output and handle missing data
first_item_name = extract_task_output(task.output_data, "result.items.0.name") or "Default Name"
```

### 3. Hardcoding Error Messages

```python
# BAD - hardcoded error message
return {"status": "error", "message": "Process failed"}

# GOOD - specific error with context
return {
    "success": False, 
    "error": f"Process failed while handling {context}: {str(error)}"
}
```

---

By following these best practices, your workflows will be more resilient, easier to debug, and better at handling unexpected data. 