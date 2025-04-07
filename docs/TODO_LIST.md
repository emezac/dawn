# 🧠 TODO List - Sprint Express (2 Weeks)

**Sprint Objective:**  
Develop an executable Python script demonstrating a simple agent using a basic Workflow Management System (WMS) to:

- Define a workflow with tasks (some using an LLM, others a simple tool).
- Execute tasks sequentially or with basic conditionals.
- Show how feedback (success/failure) affects the next steps (continue, stop, retry).
- Use a basic interface for LLM and a dummy/simple tool.

**Assumptions:**

- Developer has Python experience.
- LLM API access available (e.g., OpenAI with API key).
- Prioritize functionality over code perfection or full test/docs coverage. Tech debt is acceptable.

---

## 📅 Week 1: Foundations & WMS Logic

### ✅ Day 1: Setup & Base Structures

- [x] Create Git repository.
- [x] Set up Python virtual environment (`venv`).
- [x] Create initial `requirements.txt` (`openai`, `python-dotenv`, etc.).
- [x] Define **Task structure**: Class or dict with `id`, `name`, `status`, `input_data`, `output_data`, `is_llm_task`, `tool_name` (optional).
- [x] Define **Workflow structure**: Class with an ordered list of Tasks and general status (`running`, `completed`, `failed`).
- [x] Create **Basic Agent class** that loads a Workflow and has a `run()` method.

### ✅ Day 2: Basic Sequential Execution Engine

- [x] Implement Task status logic (e.g., `mark_running`, `mark_completed`).
- [x] Implement WMS v0.1 inside `Agent.run()` or separate `WorkflowEngine`:
  - [x] Iterate over tasks.
  - [x] Mark task as running.
  - [x] Simulate task execution (e.g., randomly mark as completed or failed).
  - [x] Update workflow state.
- [x] Create `main.py` to define and execute a dummy workflow (2–3 tasks).

### ✅ Day 3: Basic LLM Integration

- [x] Create `LLMInterface` with function `execute_llm_call(prompt)`:
  - [x] Load API key via `python-dotenv`.
  - [x] Call OpenAI Chat Completions.
  - [x] Return response or raise exception.
- [x] Modify WMS:
  - [x] If `task.is_llm_task`, call `LLMInterface` with `input_data`.
  - [x] Store result in `output_data`, update `status`.
- [x] Add a task in `main.py` that uses the LLM (e.g., "Generate a short story idea").

### ✅ Day 4: Simple Tool Integration

- [x] Define tool interface: Python function that takes specific parameters and returns a result or raises an exception.
- [x] Create a **tool registry**: Map `tool_name` to functions.
- [x] Implement a dummy tool: `calculate(operation: str, a: float, b: float)` to perform arithmetic operations.
- [x] Modify WMS:
  - [x] If `tool_name` is present, look up and execute the tool.
  - [x] Store result in `output_data`, update `status`.
- [x] Add a task in `main.py` that uses `calculate`.

### ✅ Day 5: Basic Flow + Feedback

- [x] **Failure handling**: If task fails, stop execution, mark workflow as failed.
- [x] **Data dependencies**: Support referencing prior task outputs (e.g., `${task_id}.output_data`) and resolve before execution.
- [x] **Basic logging**: Add `print()` statements for key events (start/end workflow, task result, inputs/outputs).
- [x] Test full flow in `main.py` with dependent tasks and error handling.

---

## 📅 Week 2: Basic Dynamics & MVP Completion

### ✅ Day 6: Conditional Logic

- [x] Extend Task/Workflow with optional `next_task_id_on_success` and `next_task_id_on_failure` OR a `condition` property.
- [x] Modify WMS to select the next task based on the result.
- [x] Update `main.py` with a branching workflow:
  - If LLM generates a "good" idea → draft email.
  - If not → retry idea generation.

### ✅ Day 7: Retry Logic & Refactor

- [x] Add `retry_count` and `max_retries` to Task.
- [x] In WMS:
  - [x] If a task fails and `retry_count < max_retries`, increment count and retry.
- [x] Light code refactoring: Simplify where obvious. Ensure clear function/class responsibilities.
- [x] Test retry logic in `main.py`.

### ✅ Day 8: End-to-End Example & Manual Testing

- [x] Create full example in `main.py` combining:
  - LLM task: Generate email topic.
  - Tool task: Perform a calculation using `calculate`.
  - LLM task: Draft email using prior outputs.
  - Conditional task: Check length (`check_length` tool), retry draft if too short.
  - Final task: Print "Email ready".
- [x] Execute and debug the full example.

### ✅ Day 9: Minimal Unit Tests + README

- [x] Write unit tests using `unittest` or `pytest`:
  - [x] Test Task status transitions.
  - [x] Test sequential execution.
  - [x] Test retry logic.
  - [x] Test `calculate` tool.
- [x] Create `README.md`:
  - [x] Brief description of the project and MVP goal.
  - [x] Installation steps (`pip install -r requirements.txt`).
  - [x] API key setup (`.env`).
  - [x] Run example (`python main.py`).
  - [x] Explain key concepts: Task, Workflow, WMS, LLM/Tool, feedback.

### ✅ Day 10: Final Polish & Delivery

- [x] Clean up logs/prints for clarity.
- [x] Add inline comments where logic is non-obvious.
- [x] Confirm README works as-is with example.
- [x] Remove unnecessary files.
- [x] Final commit to Git repo.
- [x] *(Optional)* Organize code into folders (e.g., `core/`, `tools/`, `examples/`).

🚀 **MVP Ready!** The code demonstrates the core concept of a dynamic WMS.

# 🧠 TODO List - Sprint Expansion (2 Weeks)

**Sprint Objective:**  
Enhance the AI Agent Framework by integrating Web Search, File Read (RAG), File Upload, and Markdown File Creation capabilities using OpenAI's new tools. This will extend the framework's ability to access and utilize external data sources, improving the agent's contextual understanding and response generation.

---

## 📅 Week 1: Web Search Tool Integration

### ✅ Day 1: Research and Setup

- [x] Review OpenAI's documentation on the Web Search tool.
- [x] Set up any necessary API configurations or permissions.

### ✅ Day 2-3: Web Search Tool Development

- [x] Implement a new tool interface for Web Search.
- [x] Create a function to perform web searches and return results.
- [x] Integrate the Web Search tool into the existing tool registry.

### ✅ Day 4: Testing and Debugging

- [x] Write unit tests for the Web Search tool.
- [x] Conduct manual testing to ensure accurate and relevant search results.

### ✅ Day 5: Documentation

- [x] Update the documentation to include usage instructions for the Web Search tool.
- [x] Provide examples of how to use the tool within a workflow.

---

## 📅 Week 2: File Read (RAG) and File Upload Tool Integration

### ✅ Day 6: Research and Setup

- [x] Review OpenAI's documentation on File Read (RAG) capabilities.
- [x] Set up any necessary API configurations or permissions.

### ✅ Day 7-8: File Read Tool Development

- [x] Implement a new tool interface for File Read (RAG).
- [x] Create a function to read and process file contents for context.
- [x] Integrate the File Read tool into the existing tool registry.

### ✅ Day 9: File Upload Tool Development

- [x] Implement a new tool interface for File Upload.
- [x] Create a function to upload files and return file IDs.
- [x] Integrate the File Upload tool into the existing tool registry.

### ✅ Day 10: Testing and Debugging

- [x] Write unit tests for the File Read and File Upload tools.
- [x] Conduct manual testing to ensure correct file reading, uploading, and context extraction.

### ✅ Day 11: Documentation and Finalization

- [x] Update the documentation to include usage instructions for the File Read and File Upload tools.
- [x] Provide examples of how to use the tools within a workflow.
- [x] Review and finalize all documentation and code changes.

---

## 📅 Week 3: Markdown File Creation Tool Integration

### Day 12: Research and Setup

- [x] Review requirements for creating and managing Markdown files.
- [x] Set up any necessary configurations or permissions.

### Day 13-14: Markdown File Creation Tool Development

- [x] Implement a new tool interface for Markdown File Creation.
- [x] Create a function to generate and save Markdown files.
- [x] Integrate the Markdown File Creation tool into the existing tool registry.

### Day 15: Testing and Debugging

- [x] Write unit tests for the Markdown File Creation tool.
- [x] Conduct manual testing to ensure correct file creation and content formatting.

### Day 16: Documentation and Finalization

- [x] Update the documentation to include usage instructions for the Markdown File Creation tool.
- [x] Provide examples of how to use the tool within a workflow.
- [x] Review and finalize all documentation and code changes.

---

## Additional Tasks

- [x] Review and update the PRD to reflect the new tool capabilities.
- [x] Ensure all new features are covered by tests and documentation.
- [x] Conduct a code review to ensure quality and consistency.
- [x] Create a complex example workflow that uses all the new tools.

🚀 **Sprint Goal Achieved!** Successfully integrated Web Search, File Read (RAG), File Upload, and Markdown File Creation tools into the AI Agent Framework, enhancing its ability to access and utilize external data sources.

# 🧠 TODO List - Sprint for Monitored Task Execution

**Sprint Objective:**  
Implement a system to monitor and log task execution within the AI Agent Framework to improve reliability and traceability.

---

## 📅 Week 1: Design and Setup

### Day 1: Research and Planning

- [x] Review existing monitoring and logging solutions.
- [x] Define requirements for task monitoring and logging.

### Day 2-3: System Design

- [ ] Design the architecture for the monitoring system.
- [ ] Identify key metrics and events to monitor.

### Day 4: Environment Setup

- [x] Set up necessary tools and environments for monitoring and logging.
- [ ] Configure initial logging settings.

---

## 📅 Week 2: Implementation and Testing

### Day 5-6: Implementation

- [ ] Implement logging for task execution.
- [ ] Integrate monitoring tools into the framework.

### Day 7: Testing and Debugging

- [ ] Write unit tests for the monitoring system.
- [ ] Conduct manual testing to ensure accurate logging and monitoring.

### Day 8: Alerts and Notifications

- [ ] Set up alerts for critical events or failures.
- [ ] Test alerting mechanisms.

### Day 9: Documentation and Finalization

- [ ] Update documentation to include monitoring and logging instructions.
- [ ] Review and finalize all code and documentation changes.

---

## Additional Tasks

- [ ] Conduct a code review to ensure quality and consistency.
- [ ] Gather feedback from stakeholders and make necessary adjustments.

🚀 **Sprint Goal:** Successfully implement a monitored task execution system within the AI Agent Framework, enhancing its reliability and traceability.

# 🧠 TODO List - Sprint for Conditional Workflow Implementation

**Sprint Objective:**  
Implement Conditional Workflow support within the AI Agent Framework to enhance its flexibility and adaptability.

---

## 📅 Week 1: Design and Setup

### Day 1: Research and Planning

- [x] Review existing workflow management systems for conditional logic.
- [x] Define requirements for implementing conditional workflows.

### Day 2-3: System Design

- [x] Design the architecture for conditional workflows.
- [x] Identify key conditions and branching logic to support.

### Day 4: Environment Setup

- [x] Set up necessary tools and environments for development.
- [x] Configure initial settings for conditional logic.

---

## 📅 Week 2: Implementation and Testing

### Day 5-6: Implementation

- [x] Implement conditional logic in the workflow management system.
- [x] Integrate conditional workflows into the existing framework.

### Day 7: Testing and Debugging

- [x] Write unit tests for conditional workflows.
- [x] Conduct manual testing to ensure correct branching and execution.

### Day 8: Documentation and Finalization

- [x] Update documentation to include instructions for using conditional workflows.
- [x] Review and finalize all code and documentation changes.

---

## Additional Tasks

- [x] Conduct a code review to ensure quality and consistency.
- [x] Gather feedback from stakeholders and make necessary adjustments.

🚀 **Sprint Goal:** Successfully implement Conditional Workflow support within the AI Agent Framework, enhancing its flexibility and adaptability.

## Web Search Tool

The web search tool has been updated to use the latest model version and includes a timeout setting for improved performance.

### Usage Example

```python
input_data = {
    "query": "What was a positive news story from today?",
    "context_size": "medium"
}
result = registry.execute_tool("web_search", input_data)
```

# 🧠 TODO List - Sprint for Parallel Workflow Implementation

**Sprint Objective:**  
Implement parallel task execution within the AI Agent Framework to improve efficiency and reduce execution time for independent tasks.

---

## 📅 Week 1: Design and Setup

### Day 1: Research and Planning

- [x] Review existing documentation on parallel task execution.
- [x] Define requirements for implementing parallel workflows.
  [x] Identify tasks that can be executed independently and analyze the dependency graph.
  [x] Decide on the concurrency model (e.g., `asyncio`, `threading`, `multiprocessing`).
  - Develop a scheduler for managing and dispatching tasks concurrently.
  - Implement dynamic updates and variable substitution mechanisms.
  - Ensure task isolation and introduce synchronization points.
  - Implement real-time logging and status updates for task tracking.
  - Develop unit and integration tests for parallel execution.
  - Benchmark performance improvements and monitor resource usage.
  - Provide documentation and examples for defining and executing parallel workflows.

### Day 2-3: System Design

- [x] Design the architecture for parallel workflows.
- [ ] Identify independent tasks and create a dependency graph.

### Day 4: Environment Setup

- [ ] Set up necessary tools and environments for development.
- [ ] Configure initial settings for parallel execution.

---

## 📅 Week 2: Implementation and Testing

### Day 5-6: Implementation

- [ ] Implement parallel execution logic in the workflow management system.
- [ ] Integrate parallel workflows into the existing framework using `asyncio` or similar libraries.

### Day 7: Testing and Debugging

- [ ] Write unit tests for parallel workflows.
- [ ] Conduct manual testing to ensure correct parallel execution and synchronization.

### Day 8: Error Handling and Synchronization

- [ ] Implement error handling to ensure task isolation.
- [ ] Introduce synchronization points where necessary.

### Day 9: Documentation and Finalization

- [ ] Update documentation to include instructions for using parallel workflows.
- [ ] Review and finalize all code and documentation changes.

---

## Additional Tasks

- [ ] Conduct a code review to ensure quality and consistency.
- [ ] Gather feedback from stakeholders and make necessary adjustments.

🚀 **Sprint Goal:** Successfully implement parallel workflow support within the AI Agent Framework, enhancing its efficiency and execution speed.
