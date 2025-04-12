# Dawn Framework Enhancements

This document describes the implementation of two major enhancements to the Dawn workflow framework:

1. **Support for Custom Task Types with their own Execution Logic**
2. **Improved Condition Evaluation with Proper Variable Scoping**

## 1. Custom Task Types

### Overview

We've enhanced the workflow system to support custom task types with specialized execution logic. This allows developers to create domain-specific tasks without modifying the core framework.

### Implementation Details

1. **New Base Class**: Added a `CustomTask` base class extending the standard `Task` class
2. **Task Type Registry**: Enhanced the `TaskExecutionStrategyFactory` to support custom task types
3. **Strategy Pattern**: Implemented the Strategy pattern for task execution
4. **Predicate-Based Selection**: Added support for dynamic task classification

### Key Components

#### CustomTask Base Class

The `CustomTask` base class extends the standard `Task` class, adding a `task_type` attribute to identify the task's type and support for custom attributes:

```python
class CustomTask(Task):
    def __init__(self, task_id, name, task_type, **kwargs):
        super().__init__(task_id=task_id, name=name, **kwargs)
        self.task_type = task_type
        # Store any additional parameters as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
```

#### TaskExecutionStrategyFactory Enhancements

We extended the `TaskExecutionStrategyFactory` with:

1. A registry for custom strategies
2. Methods to register custom strategies and predicates
3. An enhanced `get_strategy()` method that checks for custom task types

```python
class TaskExecutionStrategyFactory:
    def __init__(self, llm_interface, tool_registry):
        # Pre-create standard strategies
        self.llm_strategy = LLMTaskExecutionStrategy(llm_interface)
        self.tool_strategy = ToolTaskExecutionStrategy(tool_registry)
        self.direct_handler_strategy = DirectHandlerTaskExecutionStrategy()
        
        # Custom strategies registry
        self.custom_strategies = {}
        self.task_type_predicates = {}
        
    def register_strategy(self, task_type, strategy):
        self.custom_strategies[task_type] = strategy
        
    def register_task_type_predicate(self, task_type, predicate):
        self.task_type_predicates[task_type] = predicate
        
    def get_strategy(self, task):
        # Check for explicit task_type
        if hasattr(task, "task_type") and task.task_type in self.custom_strategies:
            return self.custom_strategies[task.task_type]
            
        # Check predicates
        for task_type, predicate in self.task_type_predicates.items():
            if predicate(task):
                return self.custom_strategies.get(task_type, self.tool_strategy)
        
        # Standard strategies
        if hasattr(task, "is_direct_handler") and task.is_direct_handler:
            return self.direct_handler_strategy
        elif task.is_llm_task:
            return self.llm_strategy
        else:
            return self.tool_strategy
```

#### WorkflowEngine Integration

The `WorkflowEngine` now uses the strategy pattern for task execution:

```python
def execute_task(self, task):
    # Get the appropriate strategy for the task
    strategy = self.strategy_factory.get_strategy(task)
    
    # Execute the task using the strategy
    execution_result = asyncio.run(strategy.execute(task, processed_input=processed_input))
    
    # Process the result...
```

### Usage Examples

See the example implementation in `examples/minimal_custom_task.py` and documentation in `docs/custom_task_types.md`.

## 2. Improved Condition Evaluation

### Overview

We've enhanced workflow conditions with proper variable scoping, providing access to more context and increasing security.

### Implementation Details

1. **Rich Context**: Added a method to build a comprehensive context for condition evaluation
2. **Safe Execution**: Implemented a restricted execution environment with only safe built-ins
3. **Helper Functions**: Added support for registering custom helper functions for conditions
4. **Cross-Task Access**: Enabled access to other tasks' outputs

### Key Components

#### Context Building

Added the `_build_condition_context()` method to create a comprehensive evaluation context:

```python
def _build_condition_context(self, task):
    context = {
        "output_data": task.output_data,
        "task": task,
        "workflow_id": self.workflow.id,
        "workflow_name": self.workflow.name,
        "task_id": task.id,
        "task_status": task.status,
    }
    
    # Add helper functions
    for func_name, func in self._condition_helper_funcs.items():
        context[func_name] = func
        
    # Add access to other task outputs
    task_outputs = {}
    for task_id, other_task in self.workflow.tasks.items():
        if other_task.status == "completed":
            task_outputs[task_id] = other_task.output_data
        else:
            task_outputs[task_id] = None
    context["task_outputs"] = task_outputs
    
    # Add workflow variables
    if hasattr(self.workflow, "variables"):
        context["workflow_vars"] = self.workflow.variables
    else:
        context["workflow_vars"] = {}
        
    return context
```

#### Helper Function Registration

Added support for registering helper functions:

```python
def register_condition_helper(self, name, function):
    self._condition_helper_funcs[name] = function
```

#### Safe Condition Evaluation

Enhanced the `get_next_task_by_condition()` method to use the improved context:

```python
def get_next_task_by_condition(self, current_task):
    if current_task.status == "completed" and current_task.condition:
        try:
            # Build a rich context for condition evaluation
            eval_context = self._build_condition_context(current_task)
            
            # Create a restricted builtins dict
            safe_builtins = {
                "True": True, "False": False, "None": None,
                "abs": abs, "all": all, "any": any, "bool": bool, 
                # ... more safe builtins ...
            }
            
            # Execute the condition
            condition_met = bool(
                eval(
                    current_task.condition,
                    {"__builtins__": safe_builtins},
                    eval_context
                )
            )
            
            # Determine next task based on condition
            next_task_id = current_task.next_task_id_on_success if condition_met else current_task.next_task_id_on_failure
        
        except Exception as e:
            # Handle errors...
    
    # Continue with task selection...
```

### Usage Examples

See the detailed documentation in `docs/variable_scoping_in_workflows.md` for examples and best practices.

## Testing and Verification

Both enhancements have been implemented and tested:

1. The `custom_task_example.py` and `minimal_custom_task.py` examples demonstrate custom task types
2. Existing workflows benefit from the improved condition evaluation automatically
3. Documentation has been added to help developers use these new features

## Documentation

- **Custom Task Types**: `docs/custom_task_types.md`
- **Variable Scoping**: `docs/variable_scoping_in_workflows.md`
- **Examples**: `examples/minimal_custom_task.py` and `examples/custom_task_example.py`

# Custom Tasks and Enhanced Conditions Documentation

## Custom Task Support

The Dawn framework now supports flexible custom task creation and registration, enabling users to develop specialized task types with dedicated execution logic.

### Key Features
- Create custom task types by extending the `CustomTask` base class
- Define task-specific execution strategies through the Strategy Pattern
- Register strategies with the workflow engine for automatic discovery
- Support for task-specific properties and execution handling

### Usage Example

```python
from core.task import CustomTask
from core.task_execution_strategy import TaskExecutionStrategy

# 1. Define a custom task type
class DataProcessingTask(CustomTask):
    """A custom task for data processing operations."""
    
    def __init__(
        self,
        task_id: str,
        name: str,
        operation: str,
        input_data: Dict[str, Any] = None,
        **kwargs
    ):
        super().__init__(
            task_id=task_id,
            name=name,
            task_type="data_processing",  # Unique identifier for this task type
            input_data=input_data,
            is_llm_task=True,  # Set to True to bypass tool_name requirement
            **kwargs
        )
        self.operation = operation  # Task-specific attribute

# 2. Define an execution strategy
class DataProcessingStrategy(TaskExecutionStrategy):
    """Strategy for executing data processing tasks."""
    
    async def execute(self, task: Task, **kwargs) -> Dict[str, Any]:
        """Execute the data processing logic."""
        processed_input = kwargs.get("processed_input", {})
        operation = getattr(task, "operation", None)
        data = processed_input.get("data", [])
        
        if not data:
            return {"success": False, "error": "No data provided"}
            
        try:
            # Execute operation-specific logic
            if operation == "filter":
                result = [item for item in data if item.get("value") > 10]
            elif operation == "transform":
                result = [{"id": item.get("id"), "value_squared": item.get("value") ** 2} for item in data]
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"Processing error: {str(e)}"}

# 3. Register the strategy with the workflow engine
workflow = Workflow(workflow_id="data_workflow", name="Data Processing Workflow")
engine = WorkflowEngine(workflow=workflow, llm_interface=llm, tool_registry=registry)

# Register the custom strategy
engine.strategy_factory.register_strategy("data_processing", DataProcessingStrategy())

# 4. Create and use custom tasks in workflows
filter_task = DataProcessingTask(
    task_id="filter_data",
    name="Filter Data Items",
    operation="filter",
    input_data={"data": sample_data}
)

transform_task = DataProcessingTask(
    task_id="transform_data",
    name="Transform Data Items",
    operation="transform",
    input_data={"data": "${filter_data.result}"},
    next_task_id_on_success="final_task"
)

# Add tasks to the workflow
workflow.add_task(filter_task)
workflow.add_task(transform_task)

# Run the workflow
result = engine.run()
```

> **Note**: Setting `is_llm_task=True` in your custom task allows it to bypass the requirement for a tool name. This is especially useful for tasks that implement their own execution logic through the strategy pattern rather than relying on the tool registry. 