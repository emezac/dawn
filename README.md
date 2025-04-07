# AI Agent Framework

The AI Agent Framework is designed to enhance the capabilities of AI agents, allowing them to perform tasks such as web searching, file reading, file uploading, and markdown file creation. Recent updates include support for conditional workflows, enhancements to the web search tool, and the ability to visualize workflow execution.

## Features

- **Conditional Workflows**: Enable dynamic task execution based on specific conditions or task outcomes, enhancing flexibility and adaptability.
- **Web Search Tool**: Updated to use the latest model version with improved performance and reliability.
- **Visualization of Workflow Execution**: Generate visual representations of workflows to aid in understanding and debugging.

## Usage

### Conditional Workflows

Conditional workflows allow for dynamic task execution based on specific conditions or task outcomes. This feature enhances the framework's flexibility and adaptability.

#### Usage Example

```python
workflow = [
    {
        "id": "task_1",
        "tool": "llm_generate_idea",
        "condition": None
    },
    {
        "id": "task_2a",
        "tool": "draft_email",
        "condition": {
            "depends_on": "task_1",
            "if_result": "good"
        }
    },
    ...
]
```

### Web Search Tool

The web search tool has been updated to use the latest model version and includes a timeout setting for improved performance.

#### Usage Example

```python
input_data = {
    "query": "What was a positive news story from today?",
    "context_size": "medium"
}
result = registry.execute_tool("web_search", input_data)
```

### Visualization of Workflow Execution

The framework supports generating visual representations of workflows using Graphviz, which helps in understanding and debugging complex workflows.

#### Usage Example

```python
from core.utils.visualizer import visualize_workflow

# Assuming 'workflow' is an instance of the Workflow class
visualize_workflow(workflow, filename="workflow_graph", format='pdf', view=True)
```

## Examples

- **Complex Conditional Workflow**: `examples/complex_conditional_workflow.py`
- **Simple Conditional Workflow**: `examples/simple_conditional_workflow.py`
- **Complex Workflow**: `examples/complex_workflow.py`

## Overview

The AI Agent Framework is an open-source Python framework designed to simplify the development of agent-based applications. It features a robust and explicit system for dynamic workflow management, allowing agents to break down complex tasks, execute sub-tasks, evaluate results, and dynamically adjust their action plans. This improves agent reliability and adaptability.

## Features

- **Dynamic Workflow Management System (WMS):**
  - Explicit task representation with state, dependencies, and tools.
  - Definition of workflows (sequential, parallel, conditional).
  - Monitored task execution with feedback integration for decision-making.
  - Workflow state tracking.
  - **Visualization of Workflow Execution:** Generate visual representations of workflows to aid in understanding and debugging.

- **LLM Interface:**
  - Compatibility with popular APIs (e.g., OpenAI).
  - Simple request/response pattern with function/tool calling.

- **Tool Interface:**
  - Easy integration of custom tools.
  - Example tools include a calculator for arithmetic operations.

- **Web Search Tool:**
  - Allows models to search the web for the latest information.
  - Configured in the `tools` array of an API request.
  - Supports user location and search context size customization.

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

3. **Integrate Web Search Tool:**
   - Use the Web Search tool to enhance your agent's ability to access real-time information.
   - Configure the tool in the `tools` array of your API requests.

4. **Visualize Workflow Execution:**
   - Use the `visualize_workflow` function to generate visual representations of your workflows.

## Key Concepts

- **Task:** Represents a unit of work with attributes like `id`, `name`, `status`, `input_data`, `output_data`, `is_llm_task`, and `tool_name`.
- **Workflow:** A collection of tasks with a defined execution order and logic.
- **Agent:** Manages workflows, LLM interfaces, and tool registries, providing methods to run workflows and get results.
- **Tool Interface:** Allows for the registration and execution of custom tools, including the Web Search tool.

## Development Plan

The project is structured into phases, with the initial version focusing on core functionality and basic examples. Future enhancements may include more complex multi-agent orchestration and advanced state persistence.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact Enrique Meza C: emezac at [gmail.com]
