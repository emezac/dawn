import os
from typing import Any, Dict, List, Optional

from openai import (  # Import necessary OpenAI classes
    APIConnectionError,
    APIError,
    OpenAI,
    RateLimitError,
)

from core.utils.logger import log_error, log_info


class LLMInterface:
    """
    Handles interactions with the configured Language Model API (e.g., OpenAI).
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initializes the LLM interface client.

        Args:
            api_key: OpenAI API key. If None, attempts to read from
                     OPENAI_API_KEY environment variable.
            model: The specific model ID to use for completions.
        """
        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_api_key:
            log_error("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key.")
            # Consider raising a more specific configuration error
            raise ValueError("OpenAI API key not found.")
        try:
            self.client = OpenAI(api_key=resolved_api_key)
            self.model = model
            log_info(f"LLMInterface initialized with model '{self.model}'.")
        except Exception as e:
            log_error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
            raise ConnectionError(f"Failed to initialize OpenAI client: {e}")

    def execute_llm_call(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        use_file_search: bool = False,
        file_search_vector_store_ids: Optional[List[str]] = None,
        file_search_max_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Calls the configured OpenAI model with the given prompt and system message.

        Args:
            prompt: The user prompt for the LLM.
            system_message: The system message to guide the LLM's behavior.
            use_file_search: Whether to use the file_search tool.
            file_search_vector_store_ids: List of vector store IDs to search in.
            file_search_max_results: Maximum number of search results to return.

        Returns:
            A dictionary containing:
            {'success': True, 'response': str, 'annotations': list} on success, or
            {'success': False, 'error': str} on failure.
        """
        if not prompt:
            log_error("execute_llm_call received an empty prompt.")
            return {"success": False, "error": "Empty prompt received."}

        try:
            log_info(f"Sending prompt to model '{self.model}' (first 100 chars): {prompt[:100]}...")

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 1500,  # Sensible default, make configurable if needed
                "temperature": 0.7,  # Common default, make configurable if needed
            }

            if use_file_search and file_search_vector_store_ids:
                # Updated to match the new OpenAI API requirements for file search tool
                # Just provide the tool configuration and let the model decide how to use it
                request_params["tools"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": "file_search",
                            "description": "Search through files using vector search",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "vector_store_ids": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of vector store IDs to search in",
                                    },
                                    "max_results": {
                                        "type": "integer",
                                        "description": "Maximum number of results to return",
                                    },
                                },
                                "required": ["vector_store_ids"],
                            },
                        },
                    }
                ]

                # Just tell the model to use the file_search function but don't try to force the arguments
                request_params["tool_choice"] = {"type": "function", "function": {"name": "file_search"}}

            response = self.client.chat.completions.create(**request_params)

            annotations = []

            # Validate response structure and extract content
            if response.choices and response.choices[0].message:
                message = response.choices[0].message

                # Handle case where message has content
                if message.content:
                    content = message.content.strip()

                    if hasattr(message, "annotations"):
                        annotations = message.annotations

                    log_info(f"Received response from model (first 100 chars): {content[:100]}...")
                    return {"success": True, "response": content, "annotations": annotations}

                # Handle case where message has tool_calls but no content
                elif hasattr(message, "tool_calls") and message.tool_calls:
                    tool_call_info = []

                    for tool_call in message.tool_calls:
                        if tool_call.type == "function" and tool_call.function.name == "file_search":
                            tool_call_info.append(f"File search with parameters: {tool_call.function.arguments}")

                    if tool_call_info:
                        tool_response = "; ".join(tool_call_info)
                        log_info(f"Received tool call response: {tool_response}")
                        return {
                            "success": True,
                            "response": "Results from file search",
                            "annotations": annotations,
                            "tool_calls": tool_call_info,
                        }

            # Handle cases where the API response structure is unexpected
            error_msg = "LLM response object missing expected content structure."
            log_error(f"{error_msg} Full Response: {response}")  # Log the actual response object
            return {"success": False, "error": error_msg}

        except (APIError, APIConnectionError, RateLimitError) as api_e:
            # Handle specific OpenAI API errors
            log_error(f"OpenAI API Error during LLM call: {api_e}")
            return {"success": False, "error": f"OpenAI API Error: {str(api_e)}"}
        except Exception as e:
            # Handle other potential errors (network, unexpected issues)
            log_error(f"Unexpected error during LLM call: {e}", exc_info=True)
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
