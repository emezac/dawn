"""
Task Execution Strategy module for the Workflow Engine.

This module implements the Strategy pattern for task execution in the workflow engine.
It defines an abstract base class for task execution strategies and concrete
implementations for different types of tasks (LLM, Tool, Direct Handler).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Callable, Optional

from core.llm.interface import LLMInterface
from core.task import Task
from core.tools.registry import ToolRegistry
from core.tools.handler_registry import HandlerRegistry
from core.utils.logger import log_error, log_info


class TaskExecutionStrategy(ABC):
    """Abstract base class for task execution strategies."""  # noqa: D202

    @abstractmethod
    async def execute(self, task: Task, **kwargs) -> Dict[str, Any]:
        """Execute the task using the strategy.

        Args:
            task: The task to execute.
            **kwargs: Additional arguments required for execution.

        Returns:
            A dictionary containing the execution result.
        """
        pass


class LLMTaskExecutionStrategy(TaskExecutionStrategy):
    """Strategy for executing LLM tasks."""  # noqa: D202

    def __init__(self, llm_interface: LLMInterface):
        """Initialize the LLM task execution strategy.

        Args:
            llm_interface: An instance of LLMInterface for LLM tasks.
        """
        self.llm_interface = llm_interface

    async def execute(self, task: Task, **kwargs) -> Dict[str, Any]:
        """Execute an LLM task using the LLMInterface.

        Args:
            task: The LLM task to execute.
            **kwargs: Additional arguments (processed_input from the workflow engine).

        Returns:
            A dictionary containing the execution result.
        """
        import asyncio

        processed_input = kwargs.get("processed_input", {})
        prompt = processed_input.get("prompt", "")
        if not prompt:
            log_error(f"No 'prompt' found in processed input for LLM task '{task.id}'.")
            return {"success": False, "error": "No prompt provided for LLM task"}
        try:
            result = await asyncio.to_thread(self.llm_interface.execute_llm_call, prompt)
            if result.get("success"):
                return {"success": True, "response": result.get("response")}
            else:
                error_msg = result.get("error", "Unknown LLM error")
                log_error(f"LLM task '{task.id}' failed: {error_msg}")
                return {"success": False, "error": error_msg}
        except Exception as e:
            log_error(f"Exception during execution of LLM task '{task.id}': {e}", exc_info=True)
            return {"success": False, "error": f"Execution error: {str(e)}"}


class ToolTaskExecutionStrategy(TaskExecutionStrategy):
    """Strategy for executing Tool tasks."""  # noqa: D202

    def __init__(self, tool_registry: ToolRegistry):
        """Initialize the Tool task execution strategy.

        Args:
            tool_registry: An instance of ToolRegistry containing available tools.
        """
        self.tool_registry = tool_registry

    async def execute(self, task: Task, **kwargs) -> Dict[str, Any]:
        """Execute a tool task using the ToolRegistry.

        Args:
            task: The tool task to execute.
            **kwargs: Additional arguments (processed_input from the workflow engine).

        Returns:
            A dictionary containing the execution result.
        """
        import asyncio

        processed_input = kwargs.get("processed_input", {})
        if not task.tool_name:
            log_error(f"No 'tool_name' specified for tool task '{task.id}'.")
            return {"success": False, "error": "Tool name not specified"}
        try:
            result = await asyncio.to_thread(self.tool_registry.execute_tool, task.tool_name, processed_input)
            if result.get("success"):
                return {"success": True, "result": result.get("result")}
            else:
                error_msg = result.get("error", "Unknown tool execution error")
                log_error(f"Tool task '{task.id}' ({task.tool_name}) failed: {error_msg}")
                return {"success": False, "error": error_msg}
        except Exception as e:
            log_error(f"Exception during execution of tool task '{task.id}': {e}", exc_info=True)
            return {"success": False, "error": f"Execution error: {str(e)}"}


class DirectHandlerTaskExecutionStrategy(TaskExecutionStrategy):
    """Strategy for executing Direct Handler tasks."""  # noqa: D202

    def __init__(self, handler_registry: Optional[HandlerRegistry] = None):
        """Initialize the Direct Handler task execution strategy.

        Args:
            handler_registry: An optional instance of HandlerRegistry for looking up handler functions.
        """
        self.handler_registry = handler_registry

    async def execute(self, task: Task, **kwargs) -> Dict[str, Any]:
        """Execute a direct handler task.

        Args:
            task: The direct handler task to execute.
            **kwargs: Additional arguments (processed_input from the workflow engine).

        Returns:
            A dictionary containing the execution result.
        """
        import asyncio
        
        processed_input = kwargs.get("processed_input", {})
        
        # Check if task has direct access to a handler function
        if hasattr(task, "handler") and callable(task.handler):
            try:
                # Execute the handler directly using the task's execute method if available
                if hasattr(task, "execute") and callable(task.execute):
                    result = task.execute(processed_input)
                    return result
                
                # Fall back to direct handler execution
                import inspect
                handler_sig = inspect.signature(task.handler)
                
                if len(handler_sig.parameters) == 1:
                    # Handler takes only input_data
                    result = task.handler(processed_input)
                else:
                    # Handler takes both task and input_data
                    result = task.handler(task, processed_input)
                    
                # Ensure proper result format
                if isinstance(result, dict) and "success" in result:
                    return result
                else:
                    return {"success": True, "result": result}
            except Exception as e:
                log_error(f"Exception during execution of direct handler task '{task.id}': {e}", exc_info=True)
                return {"success": False, "error": f"Execution error: {str(e)}"}
        
        # If task has a handler_name and we have a handler registry, look up the handler
        elif hasattr(task, "handler_name") and self.handler_registry:
            try:
                # Look up handler by name
                handler_name = task.handler_name
                
                # Execute handler via handler registry
                result = await asyncio.to_thread(
                    self.handler_registry.execute_handler,
                    handler_name,
                    processed_input
                )
                
                if isinstance(result, dict) and "success" in result:
                    return result
                else:
                    return {"success": True, "result": result}
            except Exception as e:
                log_error(f"Exception during execution of handler '{task.handler_name}' for task '{task.id}': {e}", exc_info=True)
                return {"success": False, "error": f"Handler execution error: {str(e)}"}
        
        else:
            log_error(f"No callable handler or handler_name found for direct handler task '{task.id}'.")
            return {"success": False, "error": "No callable handler found"}


class TaskExecutionStrategyFactory:
    """Factory for creating task execution strategies."""  # noqa: D202

    def __init__(
        self, 
        llm_interface: LLMInterface, 
        tool_registry: ToolRegistry, 
        handler_registry: Optional[HandlerRegistry] = None
    ):
        """Initialize the task execution strategy factory.

        Args:
            llm_interface: An instance of LLMInterface for LLM tasks.
            tool_registry: An instance of ToolRegistry containing available tools.
            handler_registry: An optional instance of HandlerRegistry for direct handler tasks.
        """
        self.llm_interface = llm_interface
        self.tool_registry = tool_registry
        self.handler_registry = handler_registry
        
        # Pre-create strategy instances
        self.llm_strategy = LLMTaskExecutionStrategy(llm_interface)
        self.tool_strategy = ToolTaskExecutionStrategy(tool_registry)
        self.direct_handler_strategy = DirectHandlerTaskExecutionStrategy(handler_registry)
        
        # Registry for custom task types and their strategies
        self.custom_strategies = {}
        self.task_type_predicates = {}

    def register_strategy(self, task_type: str, strategy: TaskExecutionStrategy) -> None:
        """Register a custom strategy for a specific task type.

        Args:
            task_type: The name of the task type to register
            strategy: The strategy instance to use for executing tasks of this type
        """
        if task_type in self.custom_strategies:
            log_info(f"Replacing existing strategy for task type '{task_type}'")
        self.custom_strategies[task_type] = strategy
        log_info(f"Registered custom strategy for task type '{task_type}'")

    def register_task_type_predicate(self, task_type: str, predicate: Callable[[Task], bool]) -> None:
        """Register a predicate function that determines if a task is of a certain type.

        Args:
            task_type: The name of the task type to register
            predicate: A function that returns True if a task is of this type
        """
        if task_type in self.task_type_predicates:
            log_info(f"Replacing existing predicate for task type '{task_type}'")
        self.task_type_predicates[task_type] = predicate
        log_info(f"Registered predicate for task type '{task_type}'")

    def get_strategy(self, task: Task) -> TaskExecutionStrategy:
        """Get the appropriate execution strategy for a task.

        Args:
            task: The task to get a strategy for.

        Returns:
            A TaskExecutionStrategy instance appropriate for the task type.
        """
        # First check if task has an explicit task_type attribute
        if hasattr(task, "task_type") and task.task_type in self.custom_strategies:
            return self.custom_strategies[task.task_type]
            
        # Then check custom type predicates
        for task_type, predicate in self.task_type_predicates.items():
            if predicate(task):
                return self.custom_strategies.get(task_type, self.tool_strategy)  # Default to tool strategy if missing
        
        # Finally, use standard type detection
        if hasattr(task, "is_direct_handler") and task.is_direct_handler:
            return self.direct_handler_strategy
        elif task.is_llm_task:
            return self.llm_strategy
        else:
            return self.tool_strategy 