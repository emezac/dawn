# Dependencies Parameter Migration Fix

## Problem Description

Several workflow scripts were using the deprecated `dependencies` parameter in the `Task` and `DirectHandlerTask` constructor calls, which has been renamed to `depends_on` in the current Dawn framework API.

This parameter is used to specify which tasks a particular task depends on for execution order. Scripts using the old parameter name would still run but would ignore the dependency relationships, potentially causing tasks to execute in an incorrect order.

## Affected Files

The following files were identified as using the deprecated parameter:

1. `examples/run_tourist_planner.py`
2. `examples/smart_compliance_workflow.py`
3. `examples/simplified_compliance_workflow.py`
4. `examples/debug_patch.py`

## Root Cause

The constructor signature for both `Task` and `DirectHandlerTask` was updated in the framework to use `depends_on` instead of `dependencies` for better clarity and consistency with other parameters. However, not all example scripts were updated to use the new parameter name.

## Solution

Updated all affected files to replace `dependencies=` with `depends_on=` in task constructor calls, ensuring that task dependencies are correctly established.

Examples of the changes made:

```python
# Before
task_search_route = Task(
    task_id="search_route",
    name="Search Public Transport Route",
    tool_name="web_search",
    input_data={"query": "${build_route_query.result.query}"},
    dependencies=["build_route_query"],
    next_task_id_on_success="extract_route_steps"
)

# After
task_search_route = Task(
    task_id="search_route",
    name="Search Public Transport Route",
    tool_name="web_search",
    input_data={"query": "${build_route_query.result.query}"},
    depends_on=["build_route_query"],
    next_task_id_on_success="extract_route_steps"
)
```

In some files, we also needed to update references to the attribute:

```python
# Before
if dependencies:
    task.dependencies = dependencies
else:
    task.dependencies = []

# After
if depends_on:
    task.depends_on = depends_on
else:
    task.depends_on = []
```

## Implementation Details

1. The following changes were made to ensure compatibility with the current API:
   - Replace all instances of `dependencies=` with `depends_on=` in constructor calls
   - Update references to the attribute name from `task.dependencies` to `task.depends_on`
   - Update warning messages and debug prints to use the new parameter name

2. In some cases, additional changes were needed:
   - Updating attribute removal code that checked for the presence of `dependencies` attribute
   - Updating parameter passing in function calls

## Verification

We created a simple test script (`fixes/dependencies_update.py`) to verify that the `depends_on` parameter is correctly recognized and used by the framework. The test output confirms that tasks correctly recognize their dependencies:

```
INFO:dependencies_test:Workflow tasks and their dependencies:
INFO:dependencies_test:Task: task1, Dependencies: []
INFO:dependencies_test:Task: task2, Dependencies: ['task1']
INFO:dependencies_test:Task: task3, Dependencies: ['task1', 'task2']
```

After making these changes, all the affected scripts run correctly with task dependencies working as expected. The tasks now properly respect the execution order specified by the `depends_on` parameter.

## API Inconsistency Notes

During our investigation, we discovered some inconsistencies in the framework API:

1. The `WorkflowEngine` class constructor requires parameters (`workflow`, `llm_interface`, `tool_registry`), but many example scripts initialize it without parameters and pass the workflow to the `run` method.

2. The class has an `execute` method that allows passing a workflow parameter, which seems to be backward compatible with older code.

3. There's a helper method `create_workflow_engine` in the `ServicesContainer` class that can be used to properly initialize the engine.

For consistency, new code should either:
1. Use `services.create_workflow_engine(workflow)` to create a properly initialized engine
2. Use `engine = WorkflowEngine(workflow, llm_interface, tool_registry, services)` for explicit initialization
3. Use `engine = WorkflowEngine()` followed by `engine.execute(workflow, initial_data)` only for backward compatibility

## Best Practices

When developing new tasks for the Dawn framework:

1. Always use `depends_on=` parameter to specify task dependencies
2. Check the latest API documentation for parameter names when upgrading to a new framework version
3. Use automated tools to find and update deprecated parameter names across the codebase
4. Include version compatibility notes when making breaking changes to API parameters

## Related Changes

This update is part of ongoing efforts to standardize the Dawn framework API and improve developer experience. Similar parameter renames may be needed in future versions of the framework.

## Fixed Files

The following files were updated to use the correct `depends_on` parameter:

1. `examples/run_tourist_planner.py`
2. `examples/smart_compliance_workflow.py`
3. `examples/simplified_compliance_workflow.py`
4. `examples/debug_patch.py` 