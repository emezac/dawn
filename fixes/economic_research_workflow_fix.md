# Economic Research Workflow Fix

## Problem Description

The `economic_impact_researcher.py` script was failing with the following error:

```
economic_impact_researcher - ERROR - An error occurred: construct_economic_research_workflow() missing 1 required positional argument: 'topic'
```

This error occurred in the `main()` function when calling `construct_economic_research_workflow()` without providing the required `topic` parameter.

Additionally, after fixing the first issue, the script was failing with another error:

```
economic_impact_researcher - ERROR - An error occurred: Workflow.__init__() missing 1 required positional argument: 'name'
```

This error occurred when initializing a `Workflow` object without providing the required `name` parameter.

## Root Cause

1. First issue: The function `construct_economic_research_workflow()` is defined with a required `topic` parameter:

```python
def construct_economic_research_workflow(topic, instructions="") -> Workflow:
```

However, in the `main()` function, it was being called without any arguments:

```python
research_workflow = construct_economic_research_workflow()
```

This resulted in a `TypeError` due to the missing required positional argument.

2. Second issue: The `Workflow` class constructor had changed and now requires both a `workflow_id` and a `name` parameter:

```python
# Expected initialization
workflow = Workflow(workflow_id="some_id", name="Some Name")
```

But in the code, we were only providing one positional argument, which was being interpreted as the `workflow_id` parameter:

```python
# Incorrect initialization
workflow = Workflow("Economic Impact Research")
```

This also resulted in a `TypeError` due to the missing required positional argument.

## Solution

1. For the first issue, the solution was to update the function call in `main()` to include the `topic` parameter, using the `USER_REQUEST` variable that is defined earlier in the file:

```python
research_workflow = construct_economic_research_workflow(topic=USER_REQUEST)
```

2. For the second issue, the solution was to update the `Workflow` initialization to provide both required parameters:

```python
workflow = Workflow(workflow_id="economic_impact_research", name="Economic Impact Research")
```

## Verification

After making both changes, the script runs successfully without any TypeError exceptions. The script generates:

1. A research report file (`informe_tarifas_trump.md`)
2. A static workflow visualization (`economic_research_static_workflow.png`)

This confirms that the workflow is being properly constructed and executed.

## Additional Notes

- When calling functions with required parameters, always ensure all required parameters are provided
- For this specific workflow, the topic is used to populate task input data for the planning and summary tasks
- The workflow now correctly uses the user's request as the research topic

This is a simple bug fix but highlights the importance of checking function signatures and ensuring all required parameters are provided when calling functions. 