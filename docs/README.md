# AI Agent Framework with Dynamic Workflow Management

## Overview

This project is an open-source Python framework designed to simplify the development of AI agents. It features a robust system for dynamic workflow management, allowing agents to break down complex tasks, execute sub-tasks, evaluate results, and dynamically adjust their action plans.

## Key Features

- **Workflow Management System (WMS):** Supports sequential, parallel, and conditional workflows with monitored task execution and feedback integration.
- **LLM Interface:** Compatible with popular APIs like OpenAI, providing a simple interface for language model interactions.
- **Tool Integration:** Easy integration of custom tools, such as web search and file access.
- **Observability:** Basic logging and tracing for debugging and workflow analysis.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your API key in a `.env` file:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

To run an example workflow, execute the following command:
```bash
python examples/complex_conditional_workflow.py
```

## Example Workflow

```python
workflow = [
    {"id": "task_1", "tool": "web_search", "dependencies": []},
    {"id": "task_2", "tool": "calculate", "dependencies": []},
    {"id": "task_3", "tool": "summarize_results", "dependencies": ["task_1", "task_2"]},
]
```

In this example, `task_1` and `task_2` can run in parallel, while `task_3` waits for both to complete.

## Testing

Run the unit tests using:
```bash
PYTHONPATH=. python -m unittest discover tests
```

## Documentation

For more detailed information, refer to the [Project Requirements Document](docs/PRD.md).

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. 