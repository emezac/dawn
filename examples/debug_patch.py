#!/usr/bin/env python
"""
Debug script to test the framework compatibility patch.
This script isolates the patching code and tests it with simple examples.
"""
import inspect

# Configure basic logging
import logging
import os
import sys
import traceback
from typing import Any, Callable, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

print("Script started")
print(f"Python version: {sys.version}")

try:
    # Add the project root to the path for imports
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    print(f"PYTHONPATH: {sys.path}")

    # Import framework classes
    print("Importing framework classes...")
    from core.task import Task

    print("Imported Task")
    from core.workflow import Workflow

    print("Imported Workflow")
    from core.tools.registry import ToolRegistry

    print("Imported ToolRegistry")
    from core.agent import Agent

    print("Imported Agent")
    from core.tools.registry_access import get_registry

    print("Imported get_registry")

    # Display original class information
    print("\n--- Original Class Info ---")
    print(f"Agent.run signature: {inspect.signature(Agent.run)}")
    print(f"Task.__init__ signature: {inspect.signature(Task.__init__)}")
    print(f"ToolRegistry.register_tool signature: {inspect.signature(ToolRegistry.register_tool)}")
    print(f"Has get_tool_names: {hasattr(ToolRegistry, 'get_tool_names')}")

    # Store the original Task class init for patching
    original_task_init = Task.__init__

    # Create a new __init__ method that handles the additional parameters
    def patched_task_init(
        self,
        task_id,
        name,
        is_llm_task=False,
        tool_name=None,
        input_data=None,
        max_retries=0,
        next_task_id_on_success=None,
        next_task_id_on_failure=None,
        condition=None,
        parallel=False,
        use_file_search=False,
        file_search_vector_store_ids=None,
        file_search_max_results=5,
        depends_on=None,
        **kwargs,
    ):
        """Patched Task.__init__ method that handles the extra parameters."""
        print(f"Creating Task with id={task_id}, depends_on={depends_on}")

        # Convert dictionary condition to string if needed
        if isinstance(condition, dict):
            # Construct a condition string from the dictionary
            variable = condition.get("variable", "").replace("${", "").replace("}", "")
            operator = condition.get("operator", "==")
            value = condition.get("value", "")

            # Map custom operators to Python operators
            op_map = {
                "equals": "==",
                "not_equals": "!=",
                "greater_than": ">",
                "less_than": "<",
                "contains": "in",
            }
            python_op = op_map.get(operator, operator)

            # Create a Python condition string
            if isinstance(value, str):
                condition_str = f"{variable} {python_op} '{value}'"
            else:
                condition_str = f"{variable} {python_op} {value}"
            print(f"Converted condition dict to string: {condition} -> {condition_str}")
        else:
            condition_str = condition

        try:
            # Call the original __init__ with only the parameters it accepts
            original_task_init(
                self,
                task_id,
                name,
                is_llm_task,
                tool_name,
                input_data,
                max_retries,
                next_task_id_on_success,
                next_task_id_on_failure,
                condition_str,
                parallel,
                use_file_search,
                file_search_vector_store_ids,
                file_search_max_results,
                depends_on,
            )

            # Store the additional attributes for reference
            self.dependencies = depends_on or []
            self.original_condition = condition  # Store the original condition object/string
            print(f"Task {task_id} created successfully with dependencies {self.dependencies}")
        except Exception as e:
            print(f"Failed to initialize Task {task_id}: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise

    # Apply the monkey patch to the Task class
    Task.__init__ = patched_task_init
    print("Applied Task.__init__ patch")

    # Store original Agent.run method
    original_agent_run = Agent.run

    # Create a compatible run method that accepts initial_input parameter
    def patched_agent_run(self, initial_input=None, **kwargs):
        """Patched Agent.run method that handles initial_input parameter."""
        print(f"Agent.run called with initial_input={initial_input}")

        # If initial input is provided, set it on the workflow tasks
        if initial_input and self.workflow:
            # We could potentially set initial input on task inputs,
            # but for now we'll just store it for reference
            self.initial_input = initial_input
            print(f"Stored initial_input on agent")

        try:
            # Call the original run method
            print("Calling original Agent.run method")
            result = original_agent_run(self)
            print(f"Original Agent.run returned: {result.get('status') if result else None}")

            # Store execution history for later retrieval
            if not hasattr(self, "execution_history"):
                if self.workflow and hasattr(self.workflow, "tasks"):
                    # Create simplified execution history from task results
                    self.execution_history = []
                    for task_id, task in self.workflow.tasks.items():
                        self.execution_history.append(
                            {"task_id": task_id, "status": task.status, "output_data": task.output_data}
                        )
                    print(f"Created execution_history with {len(self.execution_history)} tasks")

            return result
        except Exception as e:
            print(f"Exception in patched_agent_run: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise

    # Add get_execution_history method to Agent class
    def get_execution_history(self):
        """Gets the execution history of the workflow."""
        print("get_execution_history called")
        if hasattr(self, "execution_history"):
            print(f"Returning stored execution_history with {len(self.execution_history)} tasks")
            return self.execution_history
        elif self.workflow and hasattr(self.workflow, "tasks"):
            # Create execution history on demand if not already created
            history = []
            for task_id, task in self.workflow.tasks.items():
                history.append({"task_id": task_id, "status": task.status, "output_data": task.output_data})
            self.execution_history = history
            print(f"Created and returning new execution_history with {len(history)} tasks")
            return history
        print("No workflow or tasks, returning empty execution_history")
        return []

    # Apply the monkey patches to the Agent class
    Agent.run = patched_agent_run
    Agent.get_execution_history = get_execution_history
    print("Applied Agent patches")

    # Extend ToolRegistry with the missing methods if not already defined
    if not hasattr(ToolRegistry, "get_tool_names"):
        # Monkey patch the ToolRegistry class to add the get_tool_names method
        def get_tool_names(self):
            """Return a list of registered tool names."""
            tool_names = list(self.tools.keys())
            print(f"get_tool_names returning: {tool_names}")
            return tool_names

        # Add the method to the class
        setattr(ToolRegistry, "get_tool_names", get_tool_names)
        print("Added get_tool_names to ToolRegistry")

    # Check the signature of the register_tool method and patch if needed
    original_register_tool = ToolRegistry.register_tool
    sig = inspect.signature(original_register_tool)
    print(f"Original register_tool signature: {sig}")

    # If register_tool doesn't support our call pattern, create a compatible version
    if len(sig.parameters) < 5:  # Original method has fewer parameters than we need

        def compatible_register_tool(self, name, description=None, schema=None, handler=None):
            """
            Compatible version of register_tool that handles more parameters.
            Falls back to the original register_tool with just name and handler.
            """
            print(f"compatible_register_tool called with name={name}, desc={description}, schema={schema}")
            if handler is None and schema is not None and callable(schema):
                # If handler wasn't provided but schema is callable, it might be the handler
                handler = schema
                schema = None
                print(f"Using schema as handler")

            if handler is None and description is not None and callable(description):
                # If handler wasn't provided but description is callable, it might be the handler
                handler = description
                description = None
                print(f"Using description as handler")

            # Call the original method with name and handler (ignoring other params)
            try:
                print(f"Calling original register_tool with name={name}, handler={handler}")
                result = original_register_tool(self, name, handler)
                print(f"Original register_tool succeeded")
                return result
            except Exception as e:
                print(f"Failed to register tool {name}: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                raise

        # Replace the original method with our compatible version
        setattr(ToolRegistry, "register_tool", compatible_register_tool)
        print("Replaced register_tool with compatible version")

    # Display patched class information
    print("\n--- Patched Class Info ---")
    print(f"Patched Agent.run signature: {inspect.signature(Agent.run)}")
    print(f"Patched Task.__init__ signature: {inspect.signature(Task.__init__)}")
    print(f"Patched ToolRegistry.register_tool signature: {inspect.signature(ToolRegistry.register_tool)}")
    print(f"Has get_tool_names now: {hasattr(ToolRegistry, 'get_tool_names')}")

    # Test the patches
    print("\n--- Testing Patches ---")

    # Test Task initialization with dependencies
    print("\nTesting Task initialization with dependencies...")
    try:
        task = Task(
            task_id="test_task",
            name="Test Task",
            is_llm_task=True,
            depends_on=["another_task"],
            input_data={"prompt": "Test prompt"},
        )
        print(f"Task created successfully: {task}")
        print(f"Task has dependencies attribute: {hasattr(task, 'dependencies')}")
        print(f"Task.dependencies = {task.dependencies}")
    except Exception as e:
        print(f"Failed to create Task: {e}")
        print(traceback.format_exc())

    # Test Task with dictionary condition
    print("\nTesting Task with dictionary condition...")
    try:
        condition_dict = {"variable": "result", "operator": "equals", "value": "success"}
        task = Task(task_id="condition_task", name="Condition Task", is_llm_task=True, condition=condition_dict)
        print(f"Task created successfully: {task}")
        print(f"Task has original_condition attribute: {hasattr(task, 'original_condition')}")
        print(f"Task.original_condition = {task.original_condition}")
    except Exception as e:
        print(f"Failed to create Task with condition: {e}")
        print(traceback.format_exc())

    # Test ToolRegistry with get_tool_names
    print("\nTesting ToolRegistry.get_tool_names...")
    try:
        registry = get_registry()
        tool_names = registry.get_tool_names()
        print(f"ToolRegistry has tools: {tool_names}")
    except Exception as e:
        print(f"Failed to use get_tool_names: {e}")
        print(traceback.format_exc())

    # Define a simple handler for testing register_tool
    def dummy_handler(input_data):
        return {"result": "ok"}

    # Test ToolRegistry with register_tool
    print("\nTesting ToolRegistry.register_tool with extra parameters...")
    try:
        registry = get_registry()
        registry.register_tool("test_tool", "Test Tool Description", {"input": "string"}, dummy_handler)
        print(f"Tool registered successfully")
        print(f"Registry now has tools: {registry.get_tool_names()}")
    except Exception as e:
        print(f"Failed to register tool: {e}")
        print(traceback.format_exc())

    # Create a minimally configured Agent for testing
    print("\nSetting up minimal Agent for testing without LLM...")
    try:
        # Create a mock LLMInterface that doesn't need API keys
        from unittest.mock import MagicMock

        from core.llm.interface import LLMInterface

        # Create a mock LLMInterface
        mock_llm = MagicMock(spec=LLMInterface)
        mock_llm.execute_llm_call.return_value = {"success": True, "response": "Mocked response"}

        # Create a simple workflow
        workflow = Workflow(workflow_id="test_workflow", name="Test Workflow")
        task = Task(task_id="workflow_task", name="Workflow Task", is_llm_task=True)
        workflow.add_task(task)

        # Create an agent with the mock LLM and load the workflow
        registry = get_registry()
        agent = Agent(
            agent_id="test_agent", 
            name="Test Agent", 
            llm_interface=mock_llm,
            tool_registry=registry
        )
        agent.load_workflow(workflow)

        # Test get_execution_history before run
        history = agent.get_execution_history()
        print(f"Initial execution history: {history}")

        # Test if initial_input parameter is accepted
        try:
            print("Running agent with initial_input parameter...")
            result = agent.run(initial_input={"test": "data"})
            print(f"Agent.run succeeded with result: {result}")
        except Exception as e:
            print(f"Error in agent.run: {e}")
            print(traceback.format_exc())

        # Test get_execution_history after run attempt
        history = agent.get_execution_history()
        print(f"Final execution history: {history}")

    except Exception as e:
        print(f"Failed to test Agent features: {e}")
        print(traceback.format_exc())

    print("\nAll tests completed!")

except Exception as e:
    print(f"ERROR in script: {e}")
    print(traceback.format_exc())
