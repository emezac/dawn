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
    
    An agent manages workflows, LLM interfaces, and tool registries, and
    provides methods to run workflows and get results.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        llm_interface: Optional[LLMInterface] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo"
    ):
        """
        Initialize a new Agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            llm_interface: Optional pre-configured LLM interface
            api_key: API key for the LLM provider (if llm_interface not provided)
            model: Model identifier to use for completions (if llm_interface not provided)
        """
        self.id = agent_id
        self.name = name
        
        # Initialize LLM interface if not provided
        self.llm_interface = llm_interface or LLMInterface(api_key=api_key, model=model)
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        
        # Current workflow
        self.workflow = None
        
        # Results of the last workflow execution
        self.last_results = None
    
    def load_workflow(self, workflow: Workflow) -> None:
        """
        Load a workflow into the agent.
        
        Args:
            workflow: The workflow to load
        """
        self.workflow = workflow
    
    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool with the agent.
        
        Args:
            name: Name of the tool
            func: Function to call when the tool is used
        """
        self.tool_registry.register_tool(name, func)
    
    def run(self) -> Dict[str, Any]:
        """
        Run the current workflow.
        
        Returns:
            Dictionary with workflow execution results
            
        Raises:
            ValueError: If no workflow is loaded
        """
        if not self.workflow:
            raise ValueError("No workflow loaded. Call load_workflow() first.")
        
        # Create workflow engine
        engine = WorkflowEngine(
            workflow=self.workflow,
            llm_interface=self.llm_interface,
            tool_registry=self.tool_registry
        )
        
        # Run the workflow
        self.last_results = engine.run()
        
        return self.last_results
    
    def get_results(self) -> Optional[Dict[str, Any]]:
        """
        Get the results of the last workflow execution.
        
        Returns:
            Dictionary with workflow execution results, or None if no workflow has been run
        """
        return self.last_results
