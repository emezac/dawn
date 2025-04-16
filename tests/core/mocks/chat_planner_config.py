"""
Mock ChatPlannerConfig for testing.

This module provides a mock implementation of the ChatPlannerConfig class
to avoid the dependency on PyYAML during testing.
"""

from . import yaml_config

class ChatPlannerConfig:
    """Helper class for accessing Chat Planner workflow configuration."""  # noqa: D202
    
    @classmethod
    def should_use_llm_validation(cls) -> bool:
        return cls.get("validation.use_llm_validation", default=False)

    @classmethod
    def should_fix_with_llm(cls) -> bool:
        return cls.get("validation.fix_with_llm", default=False)

    @classmethod
    def get_validation_strictness(cls) -> str:
        return cls.get("validation.strictness", default="strict")
    
    @staticmethod
    def get(key: str, default: any = None) -> any:
        """
        Get a chat planner configuration value.
        Prefixes key with 'chat_planner.'.
        """
        full_key = f"chat_planner.{key}"
        return yaml_config.get(full_key, default)
    
    @staticmethod
    def set(key: str, value: any) -> None:
        """
        Set a chat planner configuration value.
        Prefixes key with 'chat_planner.'.
        """
        full_key = f"chat_planner.{key}"
        yaml_config.set(full_key, value)
    
    @staticmethod
    def get_llm_model() -> str:
        """Get the LLM model to use for plan generation."""
        return ChatPlannerConfig.get("llm_model", "gpt-3.5-turbo")
    
    @staticmethod
    def get_llm_temperature() -> float:
        """Get the temperature setting for LLM calls."""
        return ChatPlannerConfig.get("llm_temperature", 0.7)
    
    @staticmethod
    def get_max_tokens() -> int:
        """Get the maximum tokens for LLM responses."""
        return ChatPlannerConfig.get("max_tokens", 2000)
    
    @staticmethod
    def get_max_clarifications() -> int:
        """Get the maximum number of clarification iterations."""
        return ChatPlannerConfig.get("max_clarifications", 3)
    
    @staticmethod
    def is_plan_validation_enabled() -> bool:
        """Check if plan validation is enabled."""
        return ChatPlannerConfig.get("enable_plan_validation", True)
    
    @staticmethod
    def get_planning_system_message() -> str:
        """Get the system message for the planning LLM."""
        return ChatPlannerConfig.get("planning_system_message", 
            "You are an expert AI assistant for the Dawn workflow framework. "
            "Your task is to analyze the user's request and create a detailed execution plan.")
    
    @staticmethod
    def get_prompt(prompt_type: str) -> str:
        """
        Get a prompt template for a specific stage of the workflow.
        
        Args:
            prompt_type: One of 'ambiguity_check', 'planning', 'plan_validation', 'summarization'
            
        Returns:
            The prompt template as a string
        """
        prompt_key = f"prompts.{prompt_type}"
        prompt = ChatPlannerConfig.get(prompt_key, "")
        
        # Return default prompts for testing
        if not prompt:
            if prompt_type == "ambiguity_check":
                return "Ambiguity check prompt template"
            elif prompt_type == "planning":
                return "Planning prompt template"
            elif prompt_type == "plan_validation":
                return "Plan validation prompt template"
            elif prompt_type == "summarization":
                return "Summarization prompt template"
            else:
                return ""
        
        return prompt
    
    @staticmethod
    def set_prompt(prompt_type: str, prompt_template: str) -> None:
        """Set a custom prompt template for a specific stage of the workflow."""
        prompt_key = f"prompts.{prompt_type}"
        ChatPlannerConfig.set(prompt_key, prompt_template) 