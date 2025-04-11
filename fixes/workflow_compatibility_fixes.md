# Workflow Compatibility Fixes

## Problem

The Dawn framework's workflow implementation changes over time, causing examples to break in the following ways:

1. Task access and iteration patterns change (direct access vs. methods)
2. Tool registry access methods evolve (direct dictionary access vs. getter methods)
3. Expected return formats for tools change
4. Task and workflow attribute names may be different between versions
5. Error handling and exit code behavior may vary
6. Custom tool handlers may not be properly registered or accessible to the workflow

## Solution

### 1. Safe Task History Access

When extracting task history from a workflow, use defensive programming:

```python
def get_task_history(workflow):
    """Extract task history from a workflow."""
    if not workflow:
        return []
        
    history = []
    
    # Handle different workflow structures
    if hasattr(workflow, 'tasks') and isinstance(workflow.tasks, dict):
        for task_id, task in workflow.tasks.items():
            task_data = {
                'task_id': task_id,
                'status': getattr(task, 'status', 'unknown'),
                'output_data': getattr(task, 'output_data', {})
            }
            history.append(task_data)
    elif hasattr(workflow, 'get_tasks'):
        # Some workflow implementations might have a get_tasks method
        tasks = workflow.get_tasks()
        for task in tasks:
            task_id = getattr(task, 'id', getattr(task, 'task_id', str(id(task))))
            task_data = {
                'task_id': task_id,
                'status': getattr(task, 'status', 'unknown'),
                'output_data': getattr(task, 'output_data', {})
            }
            history.append(task_data)
    
    return history
```

### 2. Safe Tool Registry Access

Use the proper tool registry methods instead of direct dictionary access:

```python
# Incorrect (fragile):
if "tool_name" not in list(registry.tools.keys()):
    # Register tool

# Correct (robust):
if "tool_name" not in registry.get_tool_names():
    # Register tool
```

### 3. Consistent Tool Handler Response Format

Ensure tool handlers return a consistent format regardless of framework version:

```python
def tool_handler(input_data):
    # Process input
    result = process_data(input_data)
    
    # Return with all possible keys the framework might expect
    return {
        "status": "success",  # For newer versions
        "success": True,      # For older versions
        "result": result,     # The actual result data
        "error": None         # Always include error field
    }
```

### 4. Robust Task Collection

When accessing tasks from a workflow, accommodate different workflow structures:

```python
# Incorrect (fragile):
all_tasks = {t.id: t for t in workflow.tasks}

# Correct (robust):
all_tasks = {}
if hasattr(workflow, 'tasks') and isinstance(workflow.tasks, dict):
    for task_id, task in workflow.tasks.items():
        all_tasks[task_id] = task
```

### 5. Proper Exit Code Handling

Ensure example scripts exit with appropriate status codes to properly signal errors:

```python
def main():
    try:
        # Setup code
        if not setup_successful:
            logger.error("Setup failed")
            sys.exit(1)  # Non-zero exit code signals error
            
        # Main execution
        result = execute_workflow()
        
        # Check results
        if result.success:
            logger.info("Workflow completed successfully")
            sys.exit(0)  # Explicit zero exit code signals success
        else:
            logger.error("Workflow failed")
            sys.exit(1)  # Non-zero exit code signals error
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()  # Print full traceback for debugging
        sys.exit(1)  # Non-zero exit code signals error
```

Also ensure runner scripts properly handle exit codes:

```bash
# In shell script
python script.py
SCRIPT_EXIT_CODE=$?

if [ $SCRIPT_EXIT_CODE -eq 0 ]; then
    echo "Script completed successfully!"
else
    echo "Script failed with exit code $SCRIPT_EXIT_CODE!"
fi
```

### 6. Handle Custom Tools with Direct Execution

When using custom tools that aren't properly registered in the tool registry, create a specialized task class that directly executes the handler:

```python
# Import the necessary types
from types import MethodType
from core.engine import WorkflowEngine
from core.task import Task

# Create a task subclass for direct handler execution
class DirectHandlerTask(Task):
    """A Task subclass that directly executes a handler function."""
    
    def __init__(self, task_id, name, handler, input_data=None, condition=None, 
                 next_task_id_on_success=None, next_task_id_on_failure=None, max_retries=0):
        # Call the parent constructor with a dummy tool name
        super().__init__(
            task_id=task_id,
            name=name,
            tool_name="_direct_handler_",  # Dummy name to satisfy validation
            is_llm_task=False,
            input_data=input_data,
            condition=condition,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            max_retries=max_retries
        )
        # Store the handler function
        self.handler = handler
        self._is_direct_handler = True
        
    def execute(self, agent=None):
        """Override to directly call the handler function."""
        try:
            # Execute handler directly
            result = self.handler(self.input_data)
            
            # Set output and status
            self.output_data = result
            if result.get("success", False) or result.get("status") == "success":
                self.status = "completed"
                return True
            else:
                self.status = "failed"
                return False
        except Exception as e:
            self.status = "failed"
            self.output_data = {"success": False, "error": str(e)}
            return False

# Patch the workflow engine to handle DirectHandlerTask
def patch_workflow_engine():
    """Apply patches to support direct handler tasks."""
    # Store the original execute_task method
    original_execute_task = WorkflowEngine.execute_task
    
    # Define our patched method
    def patched_execute_task(self, task):
        if isinstance(task, DirectHandlerTask):
            # Call the DirectHandlerTask's execute method directly
            return task.execute(agent=None)
        else:
            # Call the original method for regular tasks
            return original_execute_task(self, task)
    
    # Apply the patch
    WorkflowEngine.execute_task = patched_execute_task

# Use in task creation
def create_task(task_id, name, tool_name=None, input_data=None, **kwargs):
    if tool_name in ["my_custom_tool"]:
        # Convert to a DirectHandlerTask
        return DirectHandlerTask(
            task_id=task_id,
            name=name,
            handler=my_custom_handler,
            input_data=input_data,
            **kwargs
        )
    else:
        # Create a regular task
        return Task(
            task_id=task_id,
            name=name,
            tool_name=tool_name,
            input_data=input_data,
            **kwargs
        )

# In workflow creation
def build_workflow():
    # Apply the patch
    patch_workflow_engine()
    
    # Create workflow
    workflow = Workflow(...)
    
    # Add tasks
    workflow.add_task(create_task(...))
    
    return workflow
```

## Common Issues and Their Fixes

### AttributeError: 'str' object has no attribute 'id'

This occurs when trying to access an attribute on what is actually a string. For example:

```python
# Problem:
all_tasks_in_workflow = {t.id: t for t in workflow.tasks}  # Assume workflow.tasks returns strings

# Fix:
all_tasks_in_workflow = {}
for task_id, task in workflow.tasks.items():
    all_tasks_in_workflow[task_id] = task
```

### Tool 'X' not found in registry

This happens when the tools aren't properly registered or the access method has changed:

```python
# Problem:
if "log_alert" not in list(registry.tools.keys()):
    registry.register_tool("log_alert", log_alert_handler)

# Fix:
if "log_alert" not in registry.get_tool_names():
    registry.register_tool("log_alert", log_alert_handler)
```

### AttributeError when accessing workflow task attributes

This occurs when task attributes have changed names or structure:

```python
# Problem:
task.status  # Fails if 'status' doesn't exist

# Fix:
getattr(task, 'status', 'unknown')  # Provides a default
```

### Missing Exit Codes in Example Scripts

This occurs when example scripts don't properly signal errors via exit codes.

```python
# Problem:
def main():
    if error_condition:
        logger.error("Error occurred")
        return  # Just returns, doesn't signal error to calling scripts

# Fix:
def main():
    if error_condition:
        logger.error("Error occurred")
        sys.exit(1)  # Explicitly signals error to calling scripts
```

### Tool Registry Issues

This occurs when tasks can't find tools in the registry, even though they're registered:

```python
# Problem:
ERROR: Tool task task_name failed: Tool 'tool_name' not found in registry

# Fix 1: Check if tools are registered in the correct scope
def main():
    # Create registry in main scope
    registry = ToolRegistry()
    registry.register_tool("my_tool", my_handler)
    
    # Use the same registry instance in workflow
    workflow = build_workflow(registry=registry)
    
# Fix 2: Use DirectHandlerTask for custom tools
def build_workflow():
    # Apply engine patch
    patch_workflow_engine()
    
    # Create workflow
    workflow = Workflow()
    
    # Add task with direct handler
    task = DirectHandlerTask(
        task_id="my_task",
        name="My Task",
        handler=my_handler,
        input_data={"key": "value"}
    )
    workflow.add_task(task)
    
    return workflow
```

## Best Practices

1. **Use getattr with defaults**: Always use `getattr(obj, 'attribute', default_value)` for potentially missing attributes

2. **Check for attribute existence**: Use `hasattr(obj, 'attribute')` before attempting to use methods or attributes

3. **Handle multiple return formats**: Accommodate different return formats from framework methods

4. **Use wrapper functions**: Create wrapper functions for common operations that might change

5. **Always add error handling**: Catch and log exceptions for better debugging

By following these practices, your code will be more resilient to framework changes and easier to maintain over time. 