# Dawn Framework: Common Patterns and Reuse Guidelines

This document outlines common patterns used in the Dawn framework and provides guidance on how to identify and reuse them effectively. Following these patterns ensures consistency, maintainability, and proper integration with the framework.

## Core Patterns

### 1. Tool Pattern

The Tool pattern is fundamental to Dawn's architecture and follows this structure:

```python
class SomethingTool:
    def __init__(self, client=None, **kwargs):
        # Initialize dependencies or clients
        self.client = client or DefaultClient()
        
    def do_something(self, required_param, optional_param=None):
        """Perform the tool's primary action.
        
        Args:
            required_param: Description of required parameter
            optional_param: Description of optional parameter
            
        Returns:
            dict: Result with status and data
        """
        try:
            # Implementation logic
            result = self._perform_operation(required_param, optional_param)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def _perform_operation(self, param1, param2):
        # Private helper method
        pass
```

**When to use**: Create a new tool when adding functionality that can be reused across different workflows or tasks.

**How to identify**: Look for classes that follow the naming convention `*Tool` and have a primary method that returns a dictionary with status and data/error keys.

### 2. Task Pattern

Tasks are the building blocks of workflows and follow this pattern:

```python
task = Task(
    name="meaningful_name",
    tool_name="tool_to_use",
    description="What this task does",
    input_data={
        "param1": "value1",
        "param2": "value2"
    }
)
```

**When to use**: When defining a specific operation that should be performed as part of a workflow.

**How to identify**: Look for `Task` instantiations in workflow definition files.

### 3. Workflow Pattern

Workflows connect tasks together:

```python
workflow = Workflow()
workflow.add_task(task1)
workflow.add_task(task2)
workflow.add_task(task3, depends_on=[task1.name, task2.name])
agent = Agent(workflow)
result = agent.run(initial_input)
```

**When to use**: When creating a new process that involves multiple steps with dependencies.

**How to identify**: Look for `Workflow` instantiations and sequences of `add_task` calls.

### 4. Vector Store Pattern

For working with vector stores:

```python
# Creating a vector store
create_vs_tool = CreateVectorStoreTool()
vs_id = create_vs_tool.create_vector_store("name")["data"]["vector_store_id"]

# Uploading files
upload_tool = UploadFileToVectorStoreTool()
file_id = upload_tool.upload_file_to_vector_store(
    vector_store_id=vs_id,
    file_path="path/to/file.pdf"
)["data"]["file_id"]

# Querying
query_tool = QueryVectorStoreTool()
results = query_tool.query_vector_store(
    vector_store_id=vs_id,
    query="search query",
    n_results=5
)["data"]["results"]
```

**When to use**: When working with document embeddings and semantic search.

**How to identify**: Look for operations involving `vector_store_id` parameters and the tools `CreateVectorStoreTool`, `UploadFileToVectorStoreTool`, and `QueryVectorStoreTool`.

## Utility Patterns

### 1. Validation Pattern

```python
def validate_input(input_data):
    """Validate input data.
    
    Args:
        input_data: Data to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not input_data:
        return False, "Input data cannot be empty"
    
    if required_field not in input_data:
        return False, f"Required field '{required_field}' is missing"
    
    return True, ""
    
# Usage
is_valid, error = validate_input(data)
if not is_valid:
    return {"status": "error", "error": error}
```

**When to use**: When validating inputs before processing them in tools or workflows.

**How to identify**: Look for functions that return tuples of (boolean, string) or similar validation structures.

### 2. Error Handling Pattern

```python
try:
    # Risky operation
    result = perform_operation()
    return {
        "status": "success",
        "data": result
    }
except SpecificError as e:
    # Handle specific error
    return {
        "status": "error",
        "error": f"Specific error occurred: {str(e)}"
    }
except Exception as e:
    # Catch-all for unexpected errors
    return {
        "status": "error",
        "error": f"Unexpected error: {str(e)}"
    }
```

**When to use**: For handling errors in tool operations and providing meaningful feedback.

**How to identify**: Look for try/except blocks that return standardized error responses.

### 3. Configuration Pattern

```python
from core.config import get_config

def function_needing_config():
    config = get_config()
    api_key = config.get("service.api_key")
    # Use the configuration
```

**When to use**: When accessing configuration values that might change between environments.

**How to identify**: Look for imports of `get_config` and calls to retrieve configuration values.

### 4. Logging Pattern

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Detailed information for debugging")
    logger.info("General information about operation")
    logger.warning("Something unexpected but not critical")
    logger.error("A significant error has occurred")
```

**When to use**: When adding logging to track execution and aid debugging.

**How to identify**: Look for logger initialization and calls to logger methods.

## Testing Patterns

### 1. Tool Testing Pattern

```python
def test_tool():
    # Setup
    tool = SomeTool()
    expected = {"status": "success", "data": expected_data}
    
    # Exercise
    actual = tool.do_something("test_param")
    
    # Verify
    assert actual["status"] == expected["status"]
    assert actual["data"] == expected["data"]
```

**When to use**: When creating tests for tools to verify their behavior.

**How to identify**: Look for test functions that instantiate tools and verify their output structure.

### 2. Mock Service Pattern

```python
class MockService:
    def __init__(self):
        self.calls = []
        
    def some_method(self, *args, **kwargs):
        self.calls.append({"args": args, "kwargs": kwargs})
        return {"mock": "response"}
        
def test_with_mock():
    mock_service = MockService()
    tool = SomeTool(client=mock_service)
    
    result = tool.do_something("test")
    
    assert len(mock_service.calls) == 1
    assert mock_service.calls[0]["args"][0] == "test"
```

**When to use**: When testing tools that depend on external services.

**How to identify**: Look for classes prefixed with `Mock` that track calls and return predetermined responses.

## Reuse Guidelines

1. **Search First**: Before creating new code, search the codebase for similar patterns using `grep_search` or `codebase_search`.

2. **Use Existing Tools**: Check `core/tools/registry.py` for already registered tools.

3. **Follow Naming Conventions**:
   - Tools should end with `Tool`
   - Validation functions should start with `validate_` or `is_valid_`
   - Private helper methods should start with `_`

4. **Maintain Return Structures**: Keep consistent return formats (e.g., `{"status": "success", "data": result}`) for compatible error handling.

5. **Document with Docstrings**: Always include docstrings explaining purpose, parameters, and return values.

6. **Extract Common Logic**: If you find yourself repeating code, extract it into utility functions in appropriate modules.

7. **Keep Tools Focused**: Each tool should do one thing well. Split complex operations into multiple tools.

8. **Type Hints**: Use type hints to document expectations and enable IDE assistance.

## Common Antipatterns to Avoid

1. **Direct API Client Usage**: Don't use external API clients directly in workflows; wrap them in tools.

2. **Inconsistent Error Reporting**: Stick to the standard error format.

3. **Hardcoded Configuration**: Don't hardcode credentials or environment-specific values.

4. **Long Methods**: Methods over 50 lines should be broken down.

5. **Nested Try/Except**: Avoid deeply nested error handling. Extract operations into separate functions.

By following these patterns consistently, you'll create code that integrates seamlessly with the Dawn framework and is easier to maintain and extend. 