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
