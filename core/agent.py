"""
Agent class for the AI Agent Framework.

This module defines the Agent class which is the main entry point for using
the framework. It manages workflows, LLM interfaces, and tool registries.
"""

from typing import Dict, Any, Optional, Callable
from core.workflow import Workflow
from core.engine import WorkflowEngine
from core.llm.interface import LLMInterface
from core.tools.registry import ToolRegistry


class Agent:
    """
    Main agent class for the AI Agent Framework.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        llm_interface: Optional[LLMInterface] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo"
    ):
        self.id = agent_id
        self.name = name
        self.llm_interface = llm_interface or LLMInterface(api_key=api_key, model=model)
        self.tool_registry = ToolRegistry()
        self.workflow = None
        self.last_results = None
    
    def load_workflow(self, workflow: Workflow) -> None:
        self.workflow = workflow
    
    def register_tool(self, name: str, func: Callable) -> None:
        self.tool_registry.register_tool(name, func)
    
    def run(self) -> Dict[str, Any]:
        if not self.workflow:
            raise ValueError("No workflow loaded. Call load_workflow() first.")
        engine = WorkflowEngine(
            workflow=self.workflow,
            llm_interface=self.llm_interface,
            tool_registry=self.tool_registry
        )
        self.last_results = engine.run()
        return self.last_results
    
    def get_results(self) -> Optional[Dict[str, Any]]:
        return self.last_results
