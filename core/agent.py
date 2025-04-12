"""
Agent module for the AI Agent Framework.

This module provides the Agent class which serves as the central entry point for the framework.
It manages workflows, interfaces with LLMs, and coordinates tool execution.
"""

import asyncio
import os
import sys
from typing import Any, Callable, Dict, Optional

from core.tools.registry_access import get_registry
from core.engine import WorkflowEngine
from core.async_workflow_engine import AsyncWorkflowEngine
from core.workflow import Workflow
from core.llm.interface import LLMInterface
from core.tools.registry import ToolRegistry
from core.utils.logger import log_error, log_info
from core.services import get_services

# Add parent directory to path if needed (e.g., for running tests)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Agent:
    """Main agent class for the AI Agent Framework.

    Manages workflows, LLM interfaces, and tool registries. The Agent class
    serves as the primary interface for users of the framework, handling
    the loading and execution of workflows.
    """  # noqa: D202

    def __init__(
        self,
        agent_id: str,
        name: str,
        llm_interface: Optional[LLMInterface] = None,
        tool_registry: Optional[ToolRegistry] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
    ):
        """Initialize an Agent instance.

        Args:
            agent_id: Unique identifier for the agen
            name: Human-readable name for the agen
            llm_interface: LLMInterface instance, or None to create a default one
            tool_registry: ToolRegistry instance. If None, uses the one from the services container.
            api_key: API key for LLM service if no interface is provided
            model: Model name to use if no interface is provided
        """
        self.id = agent_id
        self.name = name
        
        # Initialize LLM interface
        self.llm_interface = llm_interface or LLMInterface(api_key=api_key, model=model)
        
        # Initialize tool registry
        if tool_registry is None:
            # Get the tool registry from the services container
            services = get_services()
            self.tool_registry = services.tool_registry
        else:
            self.tool_registry = tool_registry
            
        self.workflow: Optional[Workflow] = None
        self.last_results: Optional[Dict[str, Any]] = None

        # --- Optional Debug Print ---
        # print(f"DEBUG: Agent '{self.id}' initialized.")
        # print(f"DEBUG: Agent using ToolRegistry instance ID: {id(self.tool_registry)}")
        # print(f"DEBUG: Tools in agent's registry: {list(self.tool_registry.tools.keys())}")
        # --- End Optional Debug Print ---

    def load_workflow(self, workflow: Workflow) -> None:
        """Loads a workflow into the agent."""
        self.workflow = workflow
        self.last_results = None

    def register_tool(self, name: str, func: Callable) -> None:
        """Registers a tool directly with the agent's tool registry."""
        # This method allows adding tools after agent creation if needed,
        # but it's better to pass a pre-configured registry if possible.
        self.tool_registry.register_tool(name, func)
        print(f"DEBUG: Tool '{name}' registered with agent '{self.id}'. " f"Registry ID: {id(self.tool_registry)}")

    def run(self) -> Dict[str, Any]:
        """Runs the loaded workflow using the synchronous engine."""
        if not self.workflow:
            raise ValueError("No workflow loaded. Call load_workflow() first.")

        engine = WorkflowEngine(
            workflow=self.workflow,
            llm_interface=self.llm_interface,
            tool_registry=self.tool_registry,
        )
        try:
            self.last_results = engine.run()
        except AttributeError as e:
            # Handle cases where workflow doesn't have an expected attribute
            if "'Workflow' object has no attribute 'set_error'" in str(e):
                log_error(f"Error running synchronous workflow {self.workflow.id}: {e}")
                # Create a basic error result without using workflow.set_error
                self.workflow.status = "failed"  # Set status directly
                self.last_results = self._format_error_results(e)
            else:
                # Re-raise other AttributeError exceptions
                raise
        except Exception as e:
            log_error(f"Error running synchronous workflow {self.workflow.id}: {e}")
            try:
                if self.workflow:
                    self.workflow.set_status("failed")
            except AttributeError:
                # Direct attribute access if set_status is not available
                self.workflow.status = "failed"
            self.last_results = self._format_error_results(e)
        return self.last_results

    def run_async(self) -> Dict[str, Any]:
        """Runs the loaded workflow using the asynchronous (parallel) engine."""
        if not self.workflow:
            raise ValueError("No workflow loaded. Call load_workflow() first.")

        # --- Optional Debug Print ---
        # print(f"DEBUG: Agent.run_async called for workflow '{self.workflow.id}'.")
        # print(f"DEBUG: Passing ToolRegistry instance ID: "
        #       f"{id(self.tool_registry)} to AsyncWorkflowEngine.")
        # print(f"DEBUG: Tools available in registry being passed: "
        #       f"{list(self.tool_registry.tools.keys())}")
        # --- End Optional Debug Print ---

        engine = AsyncWorkflowEngine(
            workflow=self.workflow,
            llm_interface=self.llm_interface,
            tool_registry=self.tool_registry,  # Pass the agent's registry instance
        )

        try:
            self.last_results = asyncio.run(engine.async_run())
        except Exception as e:
            log_error(f"Error running asynchronous workflow {self.workflow.id}: {e}")
            if self.workflow:
                self.workflow.set_status("failed")
            self.last_results = self._format_error_results(e)
        return self.last_results

    def get_results(self) -> Optional[Dict[str, Any]]:
        """Returns the results of the last workflow execution."""
        return self.last_results

    def _format_error_results(self, error: Exception) -> Dict[str, Any]:
        """Helper to create a consistent error result dictionary."""
        wf_id = self.workflow.id if self.workflow else "N/A"
        wf_name = self.workflow.name if self.workflow else "N/A"
        tasks = {}
        if self.workflow:
            tasks = {task_id: task.to_dict() for task_id, task in self.workflow.tasks.items()}

        return {
            "workflow_id": wf_id,
            "workflow_name": wf_name,
            "status": "failed",
            "error": str(error),
            "tasks": tasks,
        }
