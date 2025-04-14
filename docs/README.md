# AI Agent Framework with Dynamic Workflow Management

## Overview

This project is an open-source Python framework designed to simplify the development of AI agents. It features a robust system for dynamic workflow management, allowing agents to break down complex tasks, execute sub-tasks, evaluate results, and dynamically adjust their action plans.

## Key Features

- **Workflow Management System (WMS):** Supports sequential, parallel, and conditional workflows with monitored task execution and feedback integration.
- **Error Handling and Propagation:** Robust error tracking and propagation between tasks, enabling sophisticated error recovery strategies.
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

## Error Handling Example

```python
# Define a workflow with error handling
workflow = Workflow("data_processing", "Data Processing with Error Handling")

# Task that might fail
task1 = Task(
    task_id="validate_data",
    name="Validate Input Data",
    tool_name="data_validator", 
    input_data={"data_source": "customer_records.csv"},
    next_task_id_on_success="process_data",
    next_task_id_on_failure="handle_validation_error"  # Error path
)

# Error handler task
task2 = Task(
    task_id="handle_validation_error",
    name="Handle Validation Error",
    tool_name="error_recovery_tool",
    input_data={
        "error_message": "${error.validate_data}",  # Reference to error from task1
        "error_details": "${error.validate_data.error_details}"
    },
    next_task_id_on_success="retry_processing"  # Continue if recovery succeeds
)

# Add tasks to workflow
workflow.add_task(task1)
workflow.add_task(task2)
```

This workflow demonstrates how to implement error recovery using the error propagation system. For more details, see the [Error Propagation documentation](error_propagation.md).

## Testing

Run the unit tests using:
```bash
PYTHONPATH=. python -m unittest discover tests
```

## Documentation

- [Project Requirements Document](PRD.md)
- [Error Propagation](error_propagation.md)
- [Workflow Patterns](workflow_patterns.md)
- [Error Codes Reference](error_codes_reference.md)

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# Documentation

This directory contains documentation for the AI Agent Framework.

## Contents

- [Architecture](architecture.md) - Overview of the framework's architecture
- [API Reference](api_reference.md) - Detailed API documentation
- [Error Propagation](error_propagation.md) - How to handle errors between tasks
- [Vector Store ID Validation](vector_store_id_validation.md) - Utilities for validating Vector Store IDs

## Development Resources

- [Contributing](contributing.md) - Guidelines for contributing to the project
- [Testing](testing.md) - How to run and write tests
- [Code Style](code_style.md) - Coding standards and style guide

## Troubleshooting

For common issues and their solutions, check the `/fixes` directory at the root of the project. This contains markdown files documenting issues that have been encountered and fixed, including:

- [Graphviz Dependency Fix](../fixes/graphviz_dependency_fix.md) - How to handle optional graphviz dependency
- [Nested JSON in Plan Validation Fix](../fixes/nested_json_in_plan_validation_fix.md) - Fix for nested JSON structures in plan validation 