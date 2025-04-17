# Example Workflows

This document provides an overview of the example workflows included in the framework. These examples demonstrate different capabilities and can serve as templates for building custom workflows.

## Trump Tariff Analyzer (`examples/trump_tariff_analyzer.py`)

A specialized workflow that analyzes the impact of Trump's tariff policies on global trade.

### Features

- **Dynamic Planning**: Uses a planning mechanism similar to the chat planner workflow
- **Specialized Web Search**: Enhanced search queries focusing on Trump's tariff policies
- **Impact Analysis**: Analyzes effects on specific countries and sectors
- **Report Generation**: Creates comprehensive reports on tariff impacts
- **Fallback Mechanisms**: Provides mock data when web searches fail

### Usage

```bash
python examples/trump_tariff_analyzer.py --query "How did Trump's steel tariffs affect US manufacturing?"
```

## Dynamic Input Query Analyzer (`examples/dynamic_input_query_flow.py`)

A versatile workflow that accepts any user query, retrieves information, analyzes it, and generates an executive report.

### Features

- **User-defined Topics**: Accepts any topic for analysis
- **Web Search Integration**: Retrieves current information from the web
- **Data Analysis**: Identifies key facts, trends, and insights
- **Report Generation**: Creates structured executive reports
- **Workflow Visualization**: Can generate visual representations of the workflow execution

### Usage

```bash
# Run with a specific query
python examples/dynamic_input_query_flow.py

# Generate a visualization of the workflow
python examples/dynamic_input_query_flow.py --visualize --output workflow_visualization.png
```

### Dependencies for Visualization

- `graphviz` (both the Python package and system library)
- `networkx`

## Chat Planner (`examples/chat_planner_workflow.py`)

An advanced workflow that uses LLM-based planning to dynamically create and execute task sequences.

### Features

- **Dynamic Planning**: Generates execution plans based on user queries
- **Flexible Tool Integration**: Uses various tools as needed for the task
- **Clarification Requests**: Can ask for more information when needed
- **Detailed Summaries**: Provides comprehensive results of executed tasks

### Usage

```bash
python examples/chat_planner_workflow.py
```

## Creating Custom Workflows

When creating your own workflows based on these examples, consider:

1. **Task Dependencies**: Design your workflow to clearly define dependencies between tasks
2. **Error Handling**: Implement robust error detection and recovery mechanisms
3. **Data Flow**: Consider how data flows between tasks and how to handle intermediate results
4. **Visualization**: Use the visualization tools to understand and debug complex workflows
5. **Documentation**: Document your workflow's purpose, features, and usage instructions

You can combine elements from different example workflows to create custom solutions tailored to your specific needs.

## Available Example Workflows

### Dynamic Data Analysis Workflows

These workflows demonstrate dynamic data retrieval, analysis, and report generation capabilities.

#### Dynamic Input Query Analyzer (`examples/dynamic_input_query_flow.py`)

A versatile workflow that accepts any user query, retrieves information, analyzes it, and generates an executive report.

**Key Features:**
- User input-driven queries on any topic
- Real-time web search for latest information
- Intelligent extraction of key insights, statistics, and trends
- Executive report generation in Markdown format
- Workflow visualization capabilities

**Usage:**
```bash
# Run with user input prompt
python examples/dynamic_input_query_flow.py

# Generate workflow visualization
python examples/dynamic_input_query_flow.py --visualize --output workflow_diagram.png
```

**Output:**
- Interactive prompt for user query input
- Comprehensive executive report with insights, topics, statistics, and trends
- Optional workflow visualization diagram

### Chat & Planning Workflows

#### Chat Planner (`examples/chat_planner_workflow.py`)

An advanced workflow that uses LLM-based planning to dynamically create and execute task sequences.

**Key Features:**
- Dynamic plan generation based on user requests
- Plan validation and execution
- Support for clarification loops
- Fallback mechanisms for error handling

**Usage:**
```bash
python examples/chat_planner_workflow.py
```

### Task & Handler Demonstration Workflows

#### Basic Task Example (`examples/basic_task_example.py`)

A simple workflow demonstrating the core task execution capabilities.

#### Handler Registry Example (`examples/handler_registry_example.py`)

Demonstrates registration and use of custom handlers.

#### Direct Handler Tasks (`examples/direct_handler_tasks_example.py`)

Shows how to use DirectHandlerTask for more efficient execution.

## Guidelines for Creating New Workflows

When creating new workflows based on these examples, consider the following:

1. **Modularity**: Break complex workflows into reusable components
2. **Error Handling**: Implement proper error checking and fallback mechanisms
3. **Documentation**: Comment your code and provide clear usage instructions
4. **Testing**: Include test cases to verify your workflow's functionality
5. **Visualization**: Consider adding workflow visualization for complex flows

## Comparison of Workflows

| Workflow | User Input | Web Search | Analysis | Report Generation | Visualization |
|----------|------------|------------|----------|-------------------|---------------|
| Trump Tariff Analyzer | ✅ (via args) | ✅ | ✅ | ✅ | ❌ |
| Dynamic Input Query | ✅ (interactive) | ✅ | ✅ | ✅ | ✅ |
| Chat Planner | ✅ (interactive) | ✅ | ✅ | ❌ | ❌ |

## Common Patterns and Extensions

The examples demonstrate several common patterns that can be extended for your own workflows:

- **Dynamic Search and Analysis**: Both the Trump Tariff Analyzer and Dynamic Input Query workflows demonstrate how to retrieve and analyze data from external sources.
  
- **Input-Driven Workflows**: The Dynamic Input Query workflow shows how to create interactive, user-driven experiences.
  
- **Visualization**: The Dynamic Input Query workflow demonstrates how to generate visualizations of workflow structures.
  
- **Fallback Mechanisms**: All examples implement fallback handling for when primary functions fail.

- **Report Generation**: Both dynamic analysis workflows show structured report generation techniques.

## Next Steps

To get started with your own workflow:

1. Identify which example most closely matches your needs
2. Copy the example to a new file
3. Modify the components to match your specific requirements
4. Test thoroughly to ensure proper functionality 