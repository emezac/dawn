# Smart Compliance Workflow Fixes

## Problem

The `examples/smart_compliance_workflow.py` script was encountering several issues:

1. **Dictionary comprehension error**: The code was attempting to access Task attributes on string objects in the workflow.tasks dictionary.
2. **Tool registry access**: Custom tools ("log_alert" and "log_info") were registered in the registry but tasks couldn't access them.
3. **Exit code behavior**: The example wasn't properly signaling errors using system exit codes.
4. **Task execution**: Custom tools weren't being executed even though they were registered.

## Solution

We implemented several fixes to address these issues:

### 1. Fixed Task Dictionary Comprehension

```python
# Old code with error
all_tasks_in_workflow = {t.id: t for t in workflow.tasks}  # Error: 't' could be a string

# New code
all_tasks_in_workflow = {}
for task_id, task in agent.workflow.tasks.items():
    all_tasks_in_workflow[task_id] = task
```

### 2. Created a DirectHandlerTask Subclass

We created a specialized Task subclass that directly executes handler functions:

```python
class DirectHandlerTask(Task):
    """
    A Task subclass that directly executes a handler function instead of using the tool registry.
    """
    
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
        # Flag to indicate this is a direct handler task
        self._is_direct_handler = True
        
    def execute(self, agent=None):
        """Override the execute method to directly call the handler function."""
        try:
            # Execute handler directly
            result = self.handler(self.input_data)
            
            # Set output directly
            self.output_data = result
            
            # Check success
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
```

### 3. Patched the Workflow Engine

We patched the workflow engine to handle DirectHandlerTask instances:

```python
def patch_workflow_engine():
    """Apply patches to the workflow engine to support direct handler tasks."""
    # Store the original execute_task method
    original_execute_task = WorkflowEngine.execute_task
    
    # Define our patched method
    def patched_execute_task(self, task):
        # Check if this is a DirectHandlerTask
        if isinstance(task, DirectHandlerTask):
            # Call the DirectHandlerTask's execute method directly
            return task.execute(agent=None)
        else:
            # Call the original method for regular tasks
            return original_execute_task(self, task)
    
    # Apply the patch
    WorkflowEngine.execute_task = patched_execute_task
```

### 4. Modified Task Creation

We updated the `create_task` function to use DirectHandlerTask for custom tools:

```python
def create_task(task_id, name, is_llm_task=False, tool_name=None, input_data=None, 
            max_retries=0, next_task_id_on_success=None, next_task_id_on_failure=None,
            condition=None, parallel=False, use_file_search=False, 
            file_search_vector_store_ids=None, file_search_max_results=5, 
            dependencies=None, **kwargs):
    # Handle case where tool_name is one of our custom tools
    if tool_name in ["log_alert", "log_info"]:
        # Convert the tool name to a handler function for direct execution
        logger.info(f"Converting tool '{tool_name}' to direct handler for task '{task_id}'")
        
        # Select the appropriate handler function
        if tool_name == "log_alert":
            handler_func = log_alert_handler
        elif tool_name == "log_info":
            handler_func = log_info_handler
        else:
            handler_func = None
            
        # Create a DirectHandlerTask that directly calls our handler
        task = DirectHandlerTask(
            task_id=task_id,
            name=name,
            handler=handler_func,
            input_data=input_data,
            condition=condition,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            max_retries=max_retries
        )
    else:
        # Create a standard task
        task = Task(
            task_id=task_id,
            name=name,
            is_llm_task=is_llm_task,
            tool_name=tool_name,
            input_data=input_data,
            max_retries=max_retries,
            next_task_id_on_success=next_task_id_on_success,
            next_task_id_on_failure=next_task_id_on_failure,
            condition=condition,
            parallel=parallel,
            use_file_search=use_file_search,
            file_search_vector_store_ids=file_search_vector_store_ids,
            file_search_max_results=file_search_max_results
        )
    
    # Store dependencies as an attribute
    if dependencies:
        task.dependencies = dependencies
    else:
        task.dependencies = []
        
    return task
```

### 5. Used Explicit Exit Codes

We updated the script to use explicit exit codes to signal success or failure:

```python
# Old code
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY environment variable is required for LLM tasks.")
    return

# New code
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY environment variable is required for LLM tasks.")
    sys.exit(1)  # Exit with error code
```

### 6. Improved Tool Handler Return Format

We updated the tool handlers to return a consistent format:

```python
def log_alert_handler(input_data: Dict[str, str]) -> Dict[str, Any]:
    message = input_data.get('message', 'No message provided')
    level = input_data.get('level', 'CRITICAL')
    logger.critical(f"🚨 COMPLIANCE ALERT: {message}")
    # In a real tool, this would interact with a monitoring system, Slack, etc.
    return {
        "status": "success",  # For newer versions
        "success": True,      # For older versions
        "result": "Alert logged simulation",
        "error": None
    }
```

## Updated run_example.sh

We also fixed the `run_example.sh` script to properly capture and report exit codes:

```bash
# Run the example script and capture both its output and exit code
echo -e "${YELLOW}Running example: $EXAMPLE_SCRIPT${NC}"
python "$EXAMPLE_SCRIPT"
EXAMPLE_EXIT_CODE=$?

# Check if the example ran successfully
if [ $EXAMPLE_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}Example completed successfully!${NC}"
    exit 0
else
    echo -e "\n${RED}Example failed with exit code $EXAMPLE_EXIT_CODE!${NC}"
    exit $EXAMPLE_EXIT_CODE
fi
```

## Results

After implementing these fixes:

1. The workflow now successfully executes all tasks
2. Custom tool handlers are directly executed without needing to go through the registry
3. Errors are properly reported with appropriate exit codes
4. The example script properly handles task transitions

This approach creates a robust way to handle custom tools and varying framework implementations without relying on implementation details that may change between versions. 