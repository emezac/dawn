# TODO List: Chat-Driven "Think & Analyze" Workflow

This list outlines the key tasks required to implement a workflow that takes natural language input via chat, uses a planning ("Think & Analyze") component to generate an execution plan, and then dynamically creates and executes tasks based on that plan.

## Phase 1: Core Workflow Structure & Input

-   [X] **Define Chat Input Mechanism:** *(Decision Made)*
    -   [X] Initial user request passed via workflow start input dictionary (key: `user_prompt`).
    -   [X] First planning task accesses this via variable resolution (e.g., `input_data: {"user_request": "${user_prompt}"}`).
    -   [x] *Future Consideration:* Define structure for optional context (history, user ID).
-   [x] **Basic Workflow Definition:**
    -   [x] Create the main workflow file (e.g., `chat_planner_workflow.py`).
    -   [x] Define the overall sequence: Input -> Plan -> (Optional Validate Plan) -> Generate Tasks -> Execute Tasks -> Output.

## Phase 2: "Think & Analyze" Planning Component

*(Assumes details are in `PRD_THINK_ANALIZE.md`)*

-   [x] **Implement Core Planning Logic (`ThinkAnalyzeTask` or Handler):**
    -   [x] Create a new `Task` subclass or `DirectHandlerTask` handler responsible for the planning.
    -   [x] Develop the core prompt(s) for the LLM planner based on PRD requirements.
        -   [x] Incorporate instructions for generating a *structured* and *consistent* plan.
        -   [X] Ensure prompts guide the LLM to break down the request into logical, executable steps.
-   [X] **Provide Context to Planner:**
    -   [X] Implement mechanism to feed relevant context to the planner LLM. This *must* include:
        -   List of available tools from `ToolRegistry`.
        -   List of available handlers from `HandlerRegistry`.
        -   (Optional) Relevant conversation history or user profile data.
    -   [X] Design a `GetAvailableCapabilities` tool/handler to fetch current tools/handlers dynamically.
-   [x] **Define and Validate Plan Output:**
    -   [X] Specify the exact structured format for the plan (e.g., JSON list of steps with details like `step_description`, `required_tool_or_handler`, `inputs`, `outputs`, `dependencies`).
    -   [X] Implement robust parsing and validation for the LLM's plan output:
        -   [X] Added JSON Schema validation using `jsonschema` library in `validate_plan_handler`.
        -   [X] Schema enforces required fields, field types, and structure constraints.
        -   [X] Enables clear documentation of the expected plan structure.
    -   [X] Add error handling for malformed or invalid plans (retry with simplified prompt).
-   [X] **(Suggested Feature) Plan Validation Handler:**
    -   [X] Create a `DirectHandlerTask` to validate the *logical consistency* of the generated plan *before* task generation.
        -   [X] Check if specified tools/handlers exist.
        -   [X] Check if required inputs for steps are likely available from previous steps or initial input.
        -   [X] Check for circular dependencies (self-dependencies).
-   [X] **(Suggested Feature) Clarification Loop Mechanism:**
    -   [X] Allow the planner task to identify ambiguity in the user request.
    -   [X] Design a way for the planner to pause the workflow and request clarification via the chat interface.
    -   [X] Integrate the user's response back into the planning process.

## Phase 3: Dynamic Task Generation

-   [X] **Implement Plan-to-Task Converter (`PlanToTasksHandler`):**
    -   [X] Create a `DirectHandlerTask` handler responsible for converting the validated plan (structured format) into a list of executable `Task` or `DirectHandlerTask` objects.
    -   [X] Map plan steps to appropriate task types based on whether a tool or direct handler is specified.
    -   [X] Populate task parameters (`task_id`, `name`, `input_data`, `tool_name`, `handler_name`, `next_task_id_on_success`, etc.) based on the plan details.
    -   [X] Handle dependency mapping (converting plan step dependencies into `next_task_id_...` fields).
-   [X] **Dynamic Workflow Modification/Execution:**
    -   [X] Decide *how* the generated tasks will be executed:
        -   [X] **Option A: Dynamic modification:** Add generated tasks directly to the *current* workflow instance (might require `Workflow` class updates).
        -   [ ] **Option B: Sub-workflow:** Generate a *definition* for a new sub-workflow containing the tasks and execute it using the `WorkflowEngine`. (Potentially cleaner).
    -   [X] Implement the chosen mechanism for executing the dynamically generated tasks.

## Phase 4: Execution & Output

-   [x] **Workflow Engine Compatibility:**
    -   [X] Ensure `WorkflowEngine` can handle the chosen method for executing generated tasks (dynamic addition or sub-workflows).
    -   [X] Verify variable resolution works correctly for inputs/outputs of dynamically generated tasks.
-   [X] **Define Output Mechanism:**
    -   [X] Determine how the final results or status of the executed plan are reported back to the user (e.g., summary message via chat interface task).
    -   [X] Create a final `SummarizeResults` handler/task.

## Phase 5: Supporting Tasks & Quality Assurance

-   [X] **Error Handling:**
    -   [X] Implement robust error handling for failures during planning, task generation, and task execution phases.
    -   [X] Define how errors are reported back to the user.
-   [X] **Tool/Handler Registry:**
    -   [X] Ensure all necessary tools (like `GetAvailableCapabilities`) and handlers (`PlanToTasksHandler`, `PlanValidationHandler`, chat handlers) are registered correctly.
-   [X] **Configuration:**
    -   [X] Add necessary configuration options (e.g., planner LLM model, prompts, output schemas).
    -   [X] Improve environment-specific configurations for development/testing/production.
-   [x] **Documentation:**
    -   [X] Create documentation for the new workflow (`chat_planner_workflow.md`).
    -   [X] Document the "Think & Analyze" component (`ThinkAnalyzeTask` or handler).
    -   [X] Document the `PlanToTasksHandler`.
    -   [X] Document the Plan Schema Validation (`plan_schema_validation.md`).
    -   [X] Create comprehensive implementation overview (`chat_planner_implementation.md`).
    -   [X] Update `README.md` with usage examples.
-   [ ] **Testing:**
    -   [X] Unit tests for new handlers/tasks (`ThinkAnalyzeTask`, `PlanToTasksHandler`, etc.).
    -   [X] Unit tests for the plan validation logic. (All tests passing as of latest fixes)
    -   [X] Integration tests for the end-to-end chat -> plan -> execute workflow.
    -   [X] Test various chat inputs (simple, complex, ambiguous).
    -   [X] Test error handling scenarios.

## Phase 6: Advanced Features & Considerations (Suggestions)

-   [ ] **User Confirmation Step:** Add an optional step where the generated plan is presented to the user for confirmation/modification before task generation/execution.
-   [ ] **State Management:** Design a robust way to manage state across the potentially long-running interaction (chat -> planning -> clarification -> execution).
-   [ ] **Human-in-the-Loop:** Explore mechanisms for human intervention during plan execution if a task fails or produces unexpected results.
-   [ ] **Cost/Resource Estimation:** Enhance the planner to estimate the potential cost (e.g., LLM tokens, API calls) or complexity of the generated plan.
-   [ ] **Adaptive Planning:** Allow the workflow to re-plan if a task fails unexpectedly during execution.
-   [ ] **Tool/Handler Suggestion/Creation:** (Highly Advanced) Explore if the planner could suggest or even scaffold simple new `DirectHandlerTask` handlers if no existing tool/handler perfectly matches a required plan step. 