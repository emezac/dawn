# Chat Planner Workflow Implementation

This document provides a comprehensive overview of the Chat Planner Workflow implementation in the Dawn framework, detailing the architecture, components, and integration points.

## Overview

The Chat Planner Workflow is a sophisticated workflow designed to:
1. Process natural language requests from users
2. Dynamically generate execution plans based on available capabilities
3. Validate and convert these plans into executable tasks
4. Execute the tasks in the appropriate sequence
5. Provide results back to the user

This workflow represents a significant advancement in the framework's capabilities, enabling more flexible, dynamic workflows that can adapt to user requests without requiring predefined task structures.

## Workflow Architecture

The Chat Planner Workflow follows a structured approach divided into several phases:

### Phase 1: Input Processing
- Processing of chat input and contextual information
- Collection of available capabilities (tools and handlers)

### Phase 2: Planning & Clarification Loop
- Generation of an initial plan based on user request and available capabilities
- Implementation of a clarification loop when requests are ambiguous
- Refinement of the plan based on user clarifications

### Phase 3: Validation & Task Generation
- Validation of the generated plan against a schema
- Conversion of the validated plan into a sequence of executable tasks
- Setup of task dependencies and data flow

### Phase 4: Dynamic Execution
- Execution of the dynamically generated tasks
- Handling of task outputs and errors
- Management of task transitions

### Phase 5: Results & Output
- Collection of execution results
- Generation of a summary for the user
- Presentation of the results through the chat interface

## Key Components

### Clarification Loop Mechanism

The Clarification Loop Mechanism is a critical component that handles ambiguity in user requests. When the planning task identifies ambiguity or missing information:

1. The workflow pauses at the planning phase
2. A clarification request is sent to the user through the chat interface
3. The user's response is captured and integrated back into the planning process
4. The plan is regenerated with the new information

Implementation details:
- The `plan_user_request_handler` contains logic to detect ambiguity in the request
- When ambiguity is detected, the handler returns a special response format indicating clarification is needed
- The workflow checks for this format and routes to a clarification task when necessary
- After receiving clarification, the workflow returns to the planning task with enhanced context

### Plan Generation

Plan generation occurs in the `plan_user_request_handler`, which:
1. Receives the user request, available capabilities, and any clarification
2. Utilizes an LLM to analyze the request and capabilities
3. Generates a structured plan with steps, dependencies, and expected inputs/outputs
4. Returns this plan in a standardized JSON format

### Plan Validation

Plan validation ensures that the generated plan adheres to the expected schema and contains all required information:
1. The generated plan is validated against a JSON schema that defines the required structure
2. The validation checks for required fields, data types, and logical consistency
3. If validation fails, the workflow can either request clarification or generate an improved plan

### Dynamic Task Generation

The `PlanToTasksHandler` handles the conversion of validated plans into executable tasks:
1. Each step in the plan is converted to an appropriate task type (`Task`, `DirectHandlerTask`, etc.)
2. Task parameters are populated based on the plan details
3. Dependencies between tasks are established based on the plan's dependency graph
4. The generated tasks are added to the workflow for execution

### Task Execution

The workflow executes the dynamically generated tasks through one of two mechanisms:
1. **Dynamic modification:** Adding generated tasks directly to the current workflow instance
2. **Sub-workflow execution:** Generating a new sub-workflow containing the tasks and executing it

## Workflow States and Transitions

The Chat Planner Workflow can exist in several states:
1. **Input Processing:** Gathering user input and available capabilities
2. **Planning:** Generating the initial plan
3. **Clarification:** Awaiting user clarification for ambiguous requests
4. **Validation:** Validating the generated plan
5. **Task Generation:** Converting the plan to executable tasks
6. **Execution:** Executing the generated tasks
7. **Output Generation:** Summarizing results for the user

Transitions between these states are determined by the outcome of each phase. For example:
- If planning detects ambiguity, the workflow transitions to the Clarification state
- If validation fails, the workflow may return to the Planning state
- Once tasks are generated, the workflow moves to the Execution state

## Implementation Example

The complete implementation can be found in `examples/chat_planner_workflow.py`, which provides:
- A full workflow definition with all necessary tasks
- Handler implementations for planning, clarification, validation, and task generation
- Integration with the Dawn framework's core components
- Visualization capabilities for debugging and monitoring

## Integration with Dawn Framework

The Chat Planner Workflow integrates with several core components of the Dawn framework:
- **Tool Registry:** For accessing available tools
- **Handler Registry:** For accessing available handlers
- **Workflow Engine:** For executing the workflow and managing state
- **Task System:** For defining and executing tasks
- **Variable Resolution:** For managing data flow between tasks

## Best Practices for Extensions

When extending or modifying the Chat Planner Workflow:
1. **Prompt Engineering:** Carefully design prompts for the planning LLM to ensure effective plan generation
2. **Schema Evolution:** When changing the plan schema, update both the validation and task generation components
3. **Error Handling:** Implement robust error handling at each phase of the workflow
4. **Testing:** Thoroughly test with a variety of user requests to ensure robustness
5. **Documentation:** Keep documentation updated as the workflow evolves

## Configuration

The Chat Planner Workflow requires proper configuration to function correctly. The configuration is managed through environment-specific configuration files (`config/development.json`, `config/production.json`, etc.) and the `ChatPlannerConfig` class.

### Required Configuration Structure

To use the Chat Planner, ensure your environment configuration files include the following structure:

```json
{
  "chat_planner": {
    "llm_model": "gpt-4", 
    "llm_temperature": 0.2,
    "max_tokens": 4000,
    "enable_plan_validation": true,
    "validation_strictness": "high",
    "prompts": {
      "ambiguity_check": "", 
      "planning": "",
      "plan_validation": "",
      "summarization": ""
    }
  }
}
```

If the `prompts` section is empty or missing, the system will fall back to default prompt templates defined in the `ChatPlannerConfig` class. However, it's recommended to provide custom prompt templates for production use to ensure optimal planning quality.

### Customizing Prompts

For more control over the planning process, customize the prompts in your configuration:

- `ambiguity_check`: Prompt template for detecting ambiguity in user requests
- `planning`: Main prompt for generating the execution plan
- `plan_validation`: Prompt for validating the generated plan
- `summarization`: Prompt for summarizing execution results

Each template can contain placeholders like `{user_request}`, `{available_tools}`, etc. that will be replaced with actual values during execution.

## Conclusion

The Chat Planner Workflow represents a significant advancement in the Dawn framework's capabilities, enabling more dynamic, user-driven workflows. By following the implementation details and best practices outlined in this document, developers can effectively utilize, extend, and customize this powerful component to meet their specific needs. 