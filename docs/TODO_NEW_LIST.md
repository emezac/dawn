Okay, here is the detailed TODO list for refactoring and improving the Dawn framework core, translated into English, based on the issues identified with `run_tourist_planner.py`:

**Overall Objective:** Make the framework more robust, flexible, and predictable, especially regarding data handling between tasks, custom logic execution, and error management, to better support dynamic and complex workflows like the tourist planner.

---

## 📋 Detailed TODO List: Dawn Framework Core Improvements

### Phase 1: Fundamental Refactoring of Data Handling and Tasks

**1. Rigorous Standardization of Task Output:**
    *   [ ] **Define Standard Output Schema:** Establish and document a *mandatory* Python dictionary format for the output of ANY task (standard `Task`, `DirectHandlerTask`, or LLM).
        *   **Mandatory Fields:** `success` (bool), `status` (str: "completed", "failed", "skipped", "warning").
        *   **Conditional Fields (Success):** `result` (Any) - Contains the primary data. `response` (Any) - Include *in addition* to `result` for compatibility, especially for LLM tasks, both pointing to the same data if possible.
        *   **Conditional Fields (Failure):** `error` (str) - Readable message. `error_code` (str, optional) - Standardized code. `error_details` (dict, optional) - Additional context.
        *   **Optional Fields (Success/Warning):** `warning` (str), `warning_code` (str), `metadata` (dict).
    *   [ ] **Refactor `WorkflowEngine.execute_task` (and `AsyncWorkflowEngine`):** Modify execution logic to *force* the output of any tool, handler, or LLM call to conform to this standard format before storing it in `task.output_data`. Catch exceptions during tool/handler execution and format them correctly into the standard error output.
    *   [ ] **Refactor `Task.set_output`:** Ensure it validates (or attempts to convert) the input to the standard format.
    *   [ ] **Create robust `core.errors`:** Define custom exceptions (`DawnError`, `ValidationError`, `ExecutionError`, etc.) and a standardized `ErrorCode` enum/class. Add utilities `create_success_response`, `create_error_response`, `create_warning_response`.

**2. Deep Improvement of the Variable Resolution System:**
    *   [ ] **Refactor `core.utils.variable_resolver.resolve_variables`:**
        *   **Native Dot-Notation Support:** Implement robust parsing to access nested fields in dictionaries and object attributes (e.g., `${task_1.output_data.result.user.name}`).
        *   **List Indexing Support:** Allow access to list elements (e.g., `${task_1.output_data.result.items[0].id}`).
        *   **Type Handling:** Do not assume resolved values are always strings. Return the original type (int, bool, list, dict, etc.). If a string is needed (e.g., for LLM prompts), conversion should be explicit where used, not within the resolver.
        *   **Default Value Syntax:** Implement and document a clear syntax for default values if the variable doesn't resolve (e.g., `${task_1.output_data.result.priority | 'medium'}`).
        *   **Detailed Error Reporting:** If a variable fails to resolve (and no default is provided), log a clear WARNING indicating the exact variable and task. *Optional:* Add a "strict" mode that fails the task if a variable doesn't resolve.
        *   **Complete Context:** Ensure the `data_context` passed to `resolve_variables` contains *all* `output_data` from completed tasks up to that point, plus global workflow variables.
    *   [ ] **Refactor `WorkflowEngine.process_task_input`:** Ensure it uses the improved `resolve_variables` and correctly handles the resolved data types.
    *   [ ] **Utility `Task.get_output_value(path)`:** Create or improve a helper method in the `Task` class that uses the enhanced resolver to get a specific value from its `output_data` using dot-notation and handling defaults.

**3. Promotion and Strengthening of `DirectHandlerTask`:**
    *   [ ] **Make First-Class Citizen:** Document `DirectHandlerTask` as the *recommended* way for custom logic within a workflow, clearly differentiating it from reusable global tools in the `ToolRegistry`.
    *   [ ] **Ensure Full Engine Compatibility:** Verify that `DirectHandlerTask` executes correctly in both `WorkflowEngine` (synchronous) and `AsyncWorkflowEngine` (asynchronous, if planned/exists).
    *   [ ] **Handler Signature Handling:** (Partially implemented) Finalize and document support for handlers with signatures `handler(input_data)` and `handler(task, input_data)`.
    *   [ ] **Access to Workflow Context:** Provide a documented and safe way for a `DirectHandlerTask` to access global workflow variables or output from other tasks if *absolutely necessary* (ideally, pass data via `input_data`).
    *   [ ] **Parameter Validation:** Implement or improve validation for parameters passed to the `DirectHandlerTask` constructor (e.g., `handler` must be callable).

### Phase 2: Improving Specific Tools and Handlers

**4. Refactor Tools Prone to Variable Issues (e.g., `write_markdown`):**
    *   [ ] **Modify `write_markdown_handler`:**
        *   Attempt to resolve variables in the `content` field *inside* the handler.
        *   If resolution fails for *any* variable, instead of failing the entire task:
            *   Log a detailed WARNING indicating which variables couldn't be resolved.
            *   Replace unresolved variables with a clear placeholder (e.g., `[UNRESOLVED_VARIABLE: ${task_id...}]`) in the final content.
            *   Allow the task to complete *successfully* (or with `status: "warning"`) but with partially resolved content.
        *   Ensure it correctly handles the data type of `content` (don't assume string if it comes from a resolved variable that's a dict/list). Safely convert to string if necessary.
    *   [ ] **Review Other Tools:** Apply similar logic to other tools that take complex strings with variables (e.g., prompts for LLMs if constructed outside LLMInterface, API call tools).

**5. Implement Explicit JSON Parsing Task/Handler:**
    *   [ ] **Create `parse_json_handler` (Direct Handler):**
        *   Take an `input_string` as input.
        *   Attempt to parse it as JSON (`json.loads`).
        *   **Markdown Cleaning:** Attempt to remove ` ```json ` and ` ``` ` fences if initial parsing fails.
        *   **Robust Error Handling:** If parsing fails, return `success: False` with a descriptive `error` and `error_code` `JSON_PARSE_ERROR`. *Optional:* Return `success: True` but with a `result` indicating the failure and the original string for workflows that can handle plain text as fallback.
    *   [ ] **Document Pattern:** Explicitly recommend using a `DirectHandlerTask` with `parse_json_handler` *after* any LLM task expected to return JSON, before attempting to access nested fields via variable resolution.

### Phase 3: Engine Improvements and Developer Experience

**6. Improve Engine Error Handling and Propagation:**
    *   [ ] **Persistent Error Context:** Introduce an `ErrorContext` object in the `WorkflowEngine` that tracks errors for each task (`task_id`, `error_message`, `error_code`, `error_details`, `timestamp`).
    *   [ ] **Access to Previous Errors:** Modify `resolve_variables` to allow referencing errors from previous tasks using special syntax (e.g., `${error.task_id.error_message}`, `${error.task_id.error_details.field}`).
    *   [ ] **Detailed Workflow Status:** The final workflow status (`result` from `engine.run()`) must include an `error_summary` if errors occurred (`tasks_with_errors`).
    *   [ ] **Handling Failures in `process_task_input`:** If variable resolution fails *before* task execution (and there are no defaults), mark the task as failed with a specific error (`VARIABLE_RESOLUTION_ERROR`).

**7. Strengthen Unit and Integration Tests:**
    *   [ ] **Tests for `resolve_variables`:** Add exhaustive test cases covering dot-notation, list indexing, mixed data types, default values, and error scenarios.
    *   [ ] **Tests for `DirectHandlerTask`:** Verify execution, signature handling, context passing, and standardized output.
    *   [ ] **Tests for `parse_json_handler`:** Test with valid, invalid, markdown-wrapped JSON, etc.
    *   [ ] **Tests for `write_markdown`:** Test handling of resolved and unresolved variables.
    *   [ ] **Workflow Tests:** Create test workflows that explicitly use these features (deep nesting, parsing, defaults, error handling) and verify behavior.

**8. Update Documentation and Examples:**
    *   [ ] **Document Variable Resolution:** Clearly explain the syntax (dot-notation, lists, defaults), data types, and error handling.
    *   [ ] **Document Standard Output:** Detail the expected format and how to access `result`, `response`, `error`, etc.
    *   [ ] **Document `DirectHandlerTask`:** Explain its purpose, usage, handler signatures, and differences from `ToolRegistry`.
    *   [ ] **Document JSON Parsing Pattern:** Show how and why to use the parsing task after LLM calls.
    *   [ ] **Refactor Existing Examples:** Update `smart_compliance_workflow.py`, `context_aware_legal_review_workflow.py`, and other relevant examples to use the new patterns and syntax. Remove temporary workarounds (like `create_task` wrappers).
    *   [ ] **Create New Examples:** Add a specific example demonstrating complex variable resolution and robust error handling.

---

This TODO list is extensive but addresses the root causes of the observed problems. Completing these tasks should result in a significantly more reliable, predictable, and user-friendly Dawn framework for building complex workflows.
