# AI Agent Framework

The AI Agent Framework is designed to enhance the capabilities of AI agents, allowing them to perform tasks such as web searching, file reading, file uploading, and markdown file creation. Recent updates include support for conditional workflows, enhancements to the web search tool, and the ability to visualize workflow execution.

## Features

- **Conditional Workflows**: Enable dynamic task execution based on specific conditions or task outcomes, enhancing flexibility and adaptability.
- **Web Search Tool**: Updated to use the latest model version with improved performance and reliability.
- **Visualization of Workflow Execution**: Generate visual representations of workflows to aid in understanding and debugging.
- **Vector Store ID Validation**: Robust utilities for validating OpenAI Vector Store IDs with different validation levels.
- **Error Propagation Between Tasks**: Comprehensive error tracking and propagation system allowing downstream tasks to access and handle errors from upstream tasks.
- **DirectHandlerTask Support:**
  - Register and use handler functions directly in workflows without needing global tool registry.
  - Improved task output and variable resolution for complex data structures.
  - Support for both synchronous and asynchronous workflow engines.
  - Enhanced debugging and error reporting for task execution.
- **Observability:**
  - Logging and tracing to support debugging and workflow analysis.
- **Services Container:**
  - Centralized dependency management for framework-wide singletons
  - Type-safe access to shared services like ToolRegistry and LLMInterface
  - Proper dependency injection support throughout the framework
  - Simplified management of service lifecycle and configuration

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

### Vector Store ID Validation

The framework provides utilities for validating OpenAI Vector Store IDs, ensuring consistent validation across all tools and workflows.

#### Usage Example

```python
from tools.openai_vs.utils.vs_id_validator import (
    is_valid_vector_store_id, 
    is_strict_valid_vector_store_id,
    validate_vector_store_id,
    assert_valid_vector_store_id
)

# Simple boolean validation
if is_valid_vector_store_id(vector_store_id):
    # Perform operation

# Strict validation with regex pattern
if is_strict_valid_vector_store_id(vector_store_id):
    # Perform operation requiring strict format

# Get validation status and error message
is_valid, error_message = validate_vector_store_id(vector_store_id, strict=True)
if not is_valid:
    print(f"Invalid vector store ID: {error_message}")

# Assert valid ID (raises ValueError if invalid)
try:
    assert_valid_vector_store_id(vector_store_id, strict=False)
    # Continue with operation
except ValueError as e:
    print(f"Validation error: {e}")
```

For more details on vector store ID validation, see the [Vector Store ID Validation documentation](docs/vector_store_id_validation.md).

### Error Propagation Between Tasks

The framework now supports robust error propagation between tasks, allowing workflows to implement sophisticated error handling and recovery strategies.

#### Usage Example

```python
# Define a task that might fail
data_processing_task = Task(
    task_id="process_data",
    name="Process Data",
    tool_name="data_processor",
    input_data={"data_source": "customer_data.csv"},
    next_task_id_on_success="analyze_data",  # Normal path on success
    next_task_id_on_failure="handle_error"   # Error handling path on failure
)

# Define an error handler task
error_handler_task = Task(
    task_id="handle_error",
    name="Error Handler",
    tool_name="error_recovery_tool",
    input_data={
        # Access error information from the failed task
        "error_message": "${error.process_data}",
        "error_code": "${error.process_data.error_code}",
        "error_details": "${error.process_data.error_details}",
        "original_input": "customer_data.csv"
    },
    next_task_id_on_success="retry_processing",  # Try again if recovery succeeded
    next_task_id_on_failure="report_failure"      # Report failure if recovery fails
)

# Add tasks to the workflow
workflow.add_task(data_processing_task)
workflow.add_task(error_handler_task)
```

The error propagation system automatically tracks errors across tasks and provides:
- Detailed error information with standardized format
- Error references in task inputs using the `${error.task_id}` syntax
- Error propagation chains to track error origins
- Workflow-level error summaries for monitoring and analysis

For more details, see the [Error Propagation documentation](docs/error_propagation.md).

### DirectHandlerTask Support

```python
from core.task import DirectHandlerTask

# Define a handler function with the new two-parameter format
def my_custom_handler(task, input_data):
    # Access task properties if needed
    print(f"Executing task: {task.name} (ID: {task.id})")
    
    # Process the input data
    result = process_data(input_data["value"])
    
    return {"success": True, "result": result}

# Create a task with the direct handler
task = DirectHandlerTask(
    task_id="custom_processor",
    name="Custom Data Processor",
    handler=my_custom_handler,
    input_data={"value": "sample_data"}
)

# Add to workflow
workflow.add_task(task)
```

> **Note:** DirectHandlerTask now supports both older single-parameter handlers (just `input_data`) and the new two-parameter format (`task, input_data`). The two-parameter format is recommended as it provides access to the task context.

### Services Container

The Services Container provides centralized management of framework dependencies and ensures consistent access to singleton services.

```python
from core.services import get_services

# Get the services container
services = get_services()

# Access the tool registry (singleton)
registry = services.tool_registry

# Register a custom LLM interface
from core.llm.interface import LLMInterface
llm = LLMInterface(model="gpt-4")
services.register_llm_interface(llm, name="gpt4_interface")

# Create an agent using services
agent = Agent(
    agent_id="my_agent",
    name="My Agent",
    # The registry will be automatically provided from the services container
    # Use a specific named LLM interface
    llm_interface=services.get_llm_interface("gpt4_interface")
)
```

## Examples

- **Complex Conditional Workflow**: `examples/complex_conditional_workflow.py`
- **Simple Conditional Workflow**: `examples/simple_conditional_workflow.py`
- **Complex Workflow**: `examples/complex_workflow.py`
- **Vector Store Example**: `examples/vector_store_example.py`
- **Smart Compliance Workflow**: `examples/smart_compliance_workflow.py`
- **Chat Planner Workflow**: `examples/chat_planner_workflow.py`

### Chat Planner Workflow

The Chat Planner Workflow represents an advanced implementation that processes natural language user requests and dynamically generates execution plans. This workflow demonstrates how to build "think before acting" patterns that analyze user requests, determine the required steps, and execute them.

#### Usage Example

```python
from core.services import get_services, reset_services
from core.handlers.registry_access import register_handler
from core.tools.registry_access import register_tool, execute_tool
from core.tools.framework_tools import get_available_capabilities
from core.utils.registration_manager import ensure_all_registrations
from core.workflow import Workflow
from core.task import DirectHandlerTask
from examples.chat_planner_config import ChatPlannerConfig

# Initialize services and registries
reset_services()
services = get_services()
ensure_all_registrations()  # Register all required tools and handlers

# Set up your custom handlers and tools if needed
register_handler("custom_handler", my_custom_handler_function)
register_tool("custom_tool", my_custom_tool_function)

# Create a workflow that implements the Chat Planner pattern
workflow = Workflow(workflow_id="chat_planner", name="Chat Planning Workflow")

# 1. Input Task - Start with the user's request
input_task = Task(
    task_id="get_user_input",
    name="Get User Input",
    input_data={"user_request": "Please search for the latest news about AI and summarize it"},
    next_task_id_on_success="get_capabilities"
)
workflow.add_task(input_task)

# 2. Get available capabilities (tools and handlers)
get_capabilities_task = DirectHandlerTask(
    task_id="get_capabilities",
    name="Get Available Capabilities",
    handler=get_available_capabilities,
    input_data={},
    next_task_id_on_success="think_analyze_plan"
)
workflow.add_task(get_capabilities_task)

# 3. Planning Task - Analyze the request and create an execution plan
plan_task = DirectHandlerTask(
    task_id="think_analyze_plan",
    name="Think & Analyze Planning",
    handler=plan_user_request_handler,
    input_data={
        "user_request": "${get_user_input.input_data.user_request}",
        "available_tools_context": "${get_capabilities.output_data.result.available_tools}",
        "available_handlers_context": "${get_capabilities.output_data.result.available_handlers}"
    },
    next_task_id_on_success="validate_plan"
)
workflow.add_task(plan_task)

# 4. Validate the generated plan
validate_plan_task = DirectHandlerTask(
    task_id="validate_plan",
    name="Validate Generated Plan",
    handler=validate_plan_handler,
    input_data={
        "plan": "${think_analyze_plan.output_data.result.plan}",
        "user_request": "${get_user_input.input_data.user_request}",
        "available_tools": "${get_capabilities.output_data.result.available_tools}",
        "available_handlers": "${get_capabilities.output_data.result.available_handlers}"
    },
    next_task_id_on_success="generate_tasks"
)
workflow.add_task(validate_plan_task)

# 5. Generate dynamic tasks based on the plan
generate_tasks_task = DirectHandlerTask(
    task_id="generate_tasks",
    name="Convert Plan to Tasks",
    handler=plan_to_tasks_handler,
    input_data={"validated_plan": "${validate_plan.output_data.result.validated_plan}"},
    next_task_id_on_success="execute_dynamic_tasks"
)
workflow.add_task(generate_tasks_task)

# 6. Execute the dynamically generated tasks
execute_tasks_task = DirectHandlerTask(
    task_id="execute_dynamic_tasks",
    name="Execute Dynamic Tasks",
    handler=execute_dynamic_tasks_handler,
    input_data={"dynamic_tasks": "${generate_tasks.output_data.result.tasks}"},
    next_task_id_on_success="summarize_results"
)
workflow.add_task(execute_tasks_task)

# 7. Summarize results for the user
summarize_task = DirectHandlerTask(
    task_id="summarize_results",
    name="Summarize Results",
    handler=summarize_results_handler,
    input_data={
        "user_request": "${get_user_input.input_data.user_request}",
        "execution_results": "${execute_dynamic_tasks.output_data.result}"
    },
    next_task_id_on_success=None  # End of workflow
)
workflow.add_task(summarize_task)

# Run the workflow
agent = Agent(agent_id="chat_planner_agent", name="Chat Planning Agent")
agent.load_workflow(workflow)
result = agent.run()
```

The Chat Planner demonstrates several advanced features:
- **Think before acting**: Uses LLMs to analyze user requests and plan execution steps
- **Dynamic task generation**: Creates tasks at runtime based on analysis of the request 
- **Capability discovery**: Automatically detects available tools and handlers
- **Validation**: Validates generated plans before execution
- **Clarification loop**: Detects ambiguity in requests and asks for clarification when needed
- **Error handling**: Handles various errors including malformed plans and execution failures

For more details, see the `examples/chat_planner_workflow.py` implementation and `docs/chat_planner_implementation.md` documentation.

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

- **Vector Store Tools:**
  - Create and manage OpenAI Vector Stores for efficient data storage and retrieval.
  - Utilities for validating vector store IDs with basic and strict validation options.
  - Integration with file uploads and text storage for comprehensive knowledge management.

- **DirectHandlerTask Support:**
  - Register and use handler functions directly in workflows without needing global tool registry.
  - Improved task output and variable resolution for complex data structures.
  - Support for both synchronous and asynchronous workflow engines.
  - Enhanced debugging and error reporting for task execution.

- **Observability:**
  - Logging and tracing to support debugging and workflow analysis.

## Dependencies

The framework has the following core dependencies:

- **OpenAI API**: For LLM access and vector store operations
- **HTTPX**: For direct API calls when the OpenAI client doesn't support certain operations
- **Pydantic**: For data validation and settings management
- **Graphviz** (optional): For workflow visualization
- **python-dotenv**: For environment variable management

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

4. **Install Development Dependencies (optional):**

   ```bash
   pip install -r requirements-dev.txt
   ```

5. **Set Up Environment Variables:**
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

## Development

### Code Style and Linting

This project uses several tools to maintain code quality:

- **Black**: For code formatting (line length: 120 characters)
- **isort**: For sorting imports (configured to work with Black)
- **Flake8**: For linting and style checking

The project is configured with appropriate settings for each tool:
- Line length is set to 120 characters for all tools
- Specific file patterns have customized linting rules
- Common errors are selectively ignored in example and test files

#### Setup Pre-commit Hooks

```bash
pre-commit install
```

#### Manual Linting

You can use the Makefile or the lint script for linting:

```bash
# Using Make
make format    # Run isort and black
make lint      # Run flake8
make lint-all  # Run both formatting and linting

# Using the lint script
./lint.sh
```

#### Running Tests

```bash
make test      # Run all tests with pytest
PYTHONPATH=.  python -m unittest tests/test_file_name.py  # Run a specific test file
```

#### Linting Configuration

The project includes the following configuration files:
- `setup.cfg`: Contains settings for flake8 and isort
  - Configures what errors to ignore globally and per file
  - Ignores common docstring-related errors (D100-D107, D200, D205, D400, D401)
- `pyproject.toml`: Contains settings for black
- `.pre-commit-config.yaml`: Configures pre-commit hooks for automatic linting
  - Includes flake8-docstrings as an additional dependency for pre-commit checks

**Note on docstring checking**: When running `flake8` directly, it uses the configuration in `setup.cfg`. 
However, the pre-commit hook includes additional docstring checking through flake8-docstrings. 
The setup is configured to ignore most docstring formatting errors to maintain a balance between 
code quality and development speed.

## Key Concepts

- **Task:** Represents a unit of work with attributes like `id`, `name`, `status`, `input_data`, `output_data`, `is_llm_task`, and `tool_name`.
- **Workflow:** A collection of tasks with a defined execution order and logic.
- **Agent:** Manages workflows, LLM interfaces, and tool registries, providing methods to run workflows and get results.
- **Tool Interface:** Allows for the registration and execution of custom tools, including the Web Search tool.

## Development Plan

The project is structured into phases, with the initial version focusing on core functionality and basic examples. Future enhancements may include more complex multi-agent orchestration and advanced state persistence.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

Before submitting a pull request:
1. Run the linting tools to ensure code quality
2. Make sure all tests pass
3. Update documentation if necessary

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact Enrique Meza C: emezac at [gmail.com]

## Documentation

The project includes comprehensive documentation:

- **Usage Guides**: Examples and tutorials on how to use the framework effectively.
- **API Reference**: Documentation of all public classes, methods, and interfaces.
- **Tool Documentation**: Detailed information on available tools and their usage.
- **Validation Utilities**: Guidelines for validating inputs and outputs, including [Vector Store ID Validation](docs/vector_store_id_validation.md).
- **OpenAI Integration**: Information on working with OpenAI APIs, including:
  - [File Purpose Parameters](docs/openai_file_purpose_parameters.md)
  - [API Parameter Changes](docs/openai_api_parameter_changes.md) (including Beta API header format)
- **Fixes and Enhancements**: Documentation of known issues and their solutions in the `fixes` directory.
