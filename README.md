# AI Agent Framework

## Overview

The AI Agent Framework is an open-source Python framework designed to simplify the development of agent-based applications. It features a robust and explicit system for dynamic workflow management, allowing agents to break down complex tasks, execute sub-tasks, evaluate results, and dynamically adjust their action plans. This improves agent reliability and adaptability.

## Features

- **Dynamic Workflow Management System (WMS):**
  - Explicit task representation with state, dependencies, and tools.
  - Definition of workflows (sequential, parallel, conditional).
  - Monitored task execution with feedback integration for decision-making.
  - Workflow state tracking.

- **LLM Interface:**
  - Compatibility with popular APIs (e.g., OpenAI).
  - Simple request/response pattern with function/tool calling.

- **Tool Interface:**
  - Easy integration of custom tools.
  - Example tools include a calculator for arithmetic operations.

- **Observability:**
  - Logging and tracing to support debugging and workflow analysis.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**
   - Create a `.env` file in the root directory.
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

## Usage

1. **Run the Example Workflow:**
   ```bash
   python examples/simple_workflow.py
   ```

2. **Define Your Own Workflow:**
   - Create tasks using the `Task` class.
   - Define workflows using the `Workflow` class.
   - Use the `Agent` class to load and run workflows.

## Key Concepts

- **Task:** Represents a unit of work with attributes like `id`, `name`, `status`, `input_data`, `output_data`, `is_llm_task`, and `tool_name`.
- **Workflow:** A collection of tasks with a defined execution order and logic.
- **Agent:** Manages workflows, LLM interfaces, and tool registries, providing methods to run workflows and get results.
- **Tool Interface:** Allows for the registration and execution of custom tools.

## Development Plan

The project is structured into phases, with the initial version focusing on core functionality and basic examples. Future enhancements may include more complex multi-agent orchestration and advanced state persistence.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact [Your Name] at [Your Email]. 