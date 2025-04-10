"""
Module for deleting OpenAI Vector Stores.
"""

from typing import Dict, Optional

from openai import OpenAI


class DeleteVectorStoreTool:
    """
    Tool for deleting OpenAI Vector Stores.
    """

    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize the DeleteVectorStoreTool.

        Args:
            client: Optional OpenAI client instance. If not provided, a new one will be created.
        """
        self.client = client or OpenAI()

    def delete_vector_store(self, vector_store_id: str) -> Dict:
        """
        Delete a Vector Store.

        Args:
            vector_store_id: The ID of the Vector Store to delete.

        Returns:
            Dict: A dictionary indicating the deletion status.
        """
        if not vector_store_id or not isinstance(vector_store_id, str):
            raise ValueError("Vector Store ID must be a non-empty string")

        self.client.vector_stores.delete(vector_store_id=vector_store_id)
        return {"deleted": True, "id": vector_store_id}
