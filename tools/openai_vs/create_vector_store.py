"""
Module for creating OpenAI Vector Stores.
"""
from typing import Dict, Optional

from openai import OpenAI


class CreateVectorStoreTool:
    """
    Tool for creating OpenAI Vector Stores.
    """

    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize the CreateVectorStoreTool.

        Args:
            client: Optional OpenAI client instance. If not provided, a new one will be created.
        """
        self.client = client or OpenAI()

    def create_vector_store(self, name: str) -> str:
        """
        Create a new OpenAI Vector Store.

        Args:
            name: The name for the new Vector Store.

        Returns:
            str: The ID of the created Vector Store.

        Raises:
            ValueError: If the name is invalid (empty or not a string).
            OpenAI API Errors: Various errors from the OpenAI API.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Vector Store name must be a non-empty string")

        response = self.client.vector_stores.create(name=name)

        return response.id
