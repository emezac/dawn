"""
Module for creating OpenAI Vector Stores.
"""

from typing import List, Optional

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

    def create_vector_store(self, name: str, file_ids: Optional[List[str]] = None) -> str:
        """
        Create a new OpenAI Vector Store.

        Args:
            name: The name for the new Vector Store.
            file_ids: Optional list of file IDs to add to the vector store.
                     Files must have been previously uploaded with purpose='assistants'.

        Returns:
            str: The ID of the created Vector Store on success.

        Raises:
            ValueError: If the name is invalid (empty or not a string).
            OpenAI API Errors: Various errors from the OpenAI API.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Vector Store name must be a non-empty string")

        # Create vector store with specified name and optional file IDs
        file_ids = file_ids or []
        response = self.client.vector_stores.create(name=name, file_ids=file_ids)
        return response.id
