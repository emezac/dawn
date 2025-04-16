"""
Configuration helper for the Chat Planner Workflow.

This module provides easy access to all configuration options for the
chat planner workflow, including default prompt templates and LLM settings.
"""

import logging
import os
from typing import Any, Dict, Optional, Union

# Import the core configuration system
from core.config import get as config_get, set as config_set

logger = logging.getLogger(__name__)

# Default prompt templates
DEFAULT_AMBIGUITY_CHECK_PROMPT = """
You are an expert AI assistant for the Dawn workflow framework.
Your first task is to analyze a user's request and DETERMINE IF IT NEEDS CLARIFICATION before creating a plan.

**User Request:**
```
{user_request}
```

**Available Tools (Use ONLY these):**
```
{available_tools}
```

**Available Handlers (Use ONLY these):**
```
{available_handlers}
```

**STEP 1: ANALYZE FOR AMBIGUITY**

Carefully analyze the user request for ANY of these ambiguity issues:
1. Missing essential parameters needed to execute the request
2. Vague or underspecified goals that could be interpreted multiple ways
3. Insufficient context to choose appropriate tools/handlers
4. Undefined scopes or limits (time ranges, search scopes, etc.)

**STEP 2: DETERMINE IF CLARIFICATION IS NEEDED**

If you identified ANY ambiguity issues, output ONLY a JSON object with this structure:
```json
{
  "needs_clarification": true,
  "ambiguity_details": [
    {
      "aspect": "string", // The specific ambiguous aspect (e.g., "search_scope", "output_format")
      "description": "string", // Description of why this is ambiguous
      "clarification_question": "string", // Clear question to resolve the ambiguity
      "possible_options": ["string"], // Optional list of possible answers
    }
  ]
}
```

If NO clarification is needed (the request is complete and unambiguous), output ONLY:
```json
{
  "needs_clarification": false
}
```

YOUR RESPONSE MUST BE ONLY THE JSON OBJECT, nothing else.
"""

DEFAULT_PLANNING_PROMPT = """
You are an expert AI assistant for the Dawn workflow framework.
Your task is to create a detailed execution plan based on the user's request.

**User Request:**
```
{user_request}
```

**Available Tools (Use ONLY these):**
```
{available_tools}
```

**Available Handlers (Use ONLY these):**
```
{available_handlers}
```

**IMPORTANT INSTRUCTIONS:**
1. Analyze the request and determine what tools and handlers are needed to complete it
2. Create a step-by-step execution plan using ONLY the available tools and handlers
3. Structure your plan as a valid JSON array of step objects
4. Each step should include the following properties:
   - step_id: A unique identifier for the step (e.g., "step1", "search_step")
   - description: A brief description of what the step does
   - type: Either "tool" or "handler"
   - name: The exact name of the tool or handler to use
   - inputs: An object with the required input parameters
   - outputs: An array of output fields expected from this step
   - depends_on: An array of step_ids that must complete before this step

Your response should be ONLY the JSON array of steps, wrapped in triple backticks:
```json
[
  {{
    "step_id": "step1",
    "description": "...",
    "type": "...",
    "name": "...",
    "inputs": {{...}},
    "outputs": [...],
    "depends_on": [...]
  }},
  ...
]
```
"""

DEFAULT_PLAN_VALIDATION_PROMPT = """
You are an expert AI assistant for the Dawn workflow framework.
Your task is to validate a plan generated for the following user request.

**User Request:**
```
{user_request}
```

**Generated Plan:**
```json
{plan_json}
```

**Available Tools:**
```
{available_tools}
```

**Available Handlers:**
```
{available_handlers}
```

**VALIDATION INSTRUCTIONS:**
1. Check if all step_ids are unique
2. Verify that all tool and handler names exist in the available lists
3. Check that dependencies are valid (no circular dependencies, all referenced step_ids exist)
4. Verify that required inputs are provided for each step
5. Ensure the plan addresses the user's request completely

**OUTPUT FORMAT:**
Return a JSON object with the following structure:
```json
{
  "valid": true|false,
  "errors": [
    {
      "step_id": "step1",
      "error_type": "invalid_tool|missing_input|invalid_dependency|circular_dependency",
      "message": "Detailed error message"
    },
    ...
  ],
  "suggested_fixes": [
    {
      "step_id": "step1",
      "fix": "Suggested fix description",
      "fixed_step": {...}
    },
    ...
  ],
  "fixed_plan": [{...}]  // Include the fixed plan if errors were found and fixed
}
```

If the plan is completely valid, just return:
```json
{
  "valid": true,
  "errors": []
}
```
"""

DEFAULT_SUMMARIZATION_PROMPT = """
You are an expert AI assistant for the Dawn workflow framework.
Your task is to summarize the results of an executed plan.

**Original User Request:**
```
{user_request}
```

**Execution Results:**
```
{execution_results}
```

**SUMMARIZATION INSTRUCTIONS:**
1. Provide a concise summary of the results
2. Highlight any key findings or outputs
3. Mention any errors or issues that occurred
4. Format the response in a user-friendly way

Your summary should be clear, concise, and directly address the user's original request.
"""  # noqa: D202

class ChatPlannerConfig:
    """Helper class for accessing Chat Planner workflow configuration."""  # noqa: D202
    
    @classmethod
    def should_use_llm_validation(cls) -> bool:
        # Usa el método estático 'get' de esta misma clase
        return cls.get("validation.use_llm_validation", default=False)

    @classmethod
    def should_fix_with_llm(cls) -> bool:
        # Usa el método estático 'get' de esta misma clase
        return cls.get("validation.fix_with_llm", default=False)

    # Ya tienes un get_validation_strictness estático, pero si quieres
    # mantener el @classmethod, también debe usar cls.get
    @classmethod
    def get_validation_strictness(cls) -> str:
         # Usa el método estático 'get' de esta misma clase
        return cls.get("validation.strictness", default="strict")
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get a chat planner configuration value.
        Prefixes key with 'chat_planner.'.
        """
        full_key = f"chat_planner.{key}"
        # Llama a la función 'get' importada del módulo core.config
        return config_get(full_key, default)
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """
        Set a chat planner configuration value.
        Prefixes key with 'chat_planner.'.
        """
        full_key = f"chat_planner.{key}"
         # Llama a la función 'set' importada del módulo core.config
        config_set(full_key, value)
    
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
    def mock_get_max_clarifications() -> int:
        """Mock function for testing that returns a fixed value."""
        return 3
    
    @staticmethod
    def is_plan_validation_enabled() -> bool:
        """Check if plan validation is enabled."""
        return ChatPlannerConfig.get("enable_plan_validation", True)
    
    @staticmethod
    def get_validation_strictness() -> str:
        """Get the strictness level for plan validation."""
        return ChatPlannerConfig.get("validation_strictness", "medium")
    
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
        
        # If no custom prompt is configured, use the default
        if not prompt:
            if prompt_type == "ambiguity_check":
                return DEFAULT_AMBIGUITY_CHECK_PROMPT
            elif prompt_type == "planning":
                return DEFAULT_PLANNING_PROMPT
            elif prompt_type == "plan_validation":
                return DEFAULT_PLAN_VALIDATION_PROMPT
            elif prompt_type == "summarization":
                return DEFAULT_SUMMARIZATION_PROMPT
            else:
                logger.warning(f"Unknown prompt type: {prompt_type}")
                return ""
        
        return prompt
    
    @staticmethod
    def set_prompt(prompt_type: str, prompt_template: str) -> None:
        """
        Set a custom prompt template for a specific stage of the workflow.
        
        Args:
            prompt_type: One of 'ambiguity_check', 'planning', 'plan_validation', 'summarization'
            prompt_template: The prompt template as a string
        """
        prompt_key = f"prompts.{prompt_type}"
        ChatPlannerConfig.set(prompt_key, prompt_template)

# Example usage in code:
# from examples.chat_planner_config import ChatPlannerConfig
# model = ChatPlannerConfig.get_llm_model()
# prompt = ChatPlannerConfig.get_prompt("planning") 