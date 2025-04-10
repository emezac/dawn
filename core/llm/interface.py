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
                request_params["tools"] = [
                    {
                        "type": "file_search",
                        "file_search": {
                            "vector_store_ids": file_search_vector_store_ids,
                            "max_results": file_search_max_results,
                        },
                    }
                ]

            response = self.client.chat.completions.create(**request_params)

            annotations = []

            # Validate response structure and extract content
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()

                if hasattr(response.choices[0].message, "annotations"):
                    annotations = response.choices[0].message.annotations

                log_info(f"Received response from model (first 100 chars): {content[:100]}...")
                return {"success": True, "response": content, "annotations": annotations}
            else:
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
