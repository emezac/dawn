"""
LLM Interface for the AI Agent Framework.

This module provides an interface for interacting with Large Language Models (LLMs)
through various APIs like OpenAI.
"""

import os
from typing import Any, Dict, Optional

import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMInterface:
    """
    Interface for interacting with Large Language Models.

    This class provides methods to execute calls to LLM APIs and handle
    responses and errors.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM interface.

        Args:
            api_key: API key for the LLM provider (defaults to OPENAI_API_KEY env var)
            model: Model identifier to use for completions
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        self.model = model
        openai.api_key = self.api_key

    def execute_llm_call(self, prompt: str) -> Dict[str, Any]:
        """
        Execute a call to the LLM API.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            Dictionary containing the response and metadata

        Raises:
            Exception: If the API call fails
        """
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            # Extract the response text
            response_text = response.choices[0].message.content

            return {
                "success": True,
                "response": response_text,
                "model": self.model,
                "metadata": {
                    "finish_reason": response.choices[0].finish_reason,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                },
            }

        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle errors from the LLM API.

        Args:
            error: The exception that occurred

        Returns:
            Dictionary with error information
        """
        error_message = str(error)
        error_type = type(error).__name__

        return {"success": False, "error": error_message, "error_type": error_type}
