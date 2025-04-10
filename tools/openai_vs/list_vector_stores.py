"""
Module for listing OpenAI Vector Stores.
"""

from typing import Dict, List, Optional

from openai import OpenAI


class ListVectorStoresTool:
    """
    Tool for listing OpenAI Vector Stores.
    """

    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize the ListVectorStoresTool.

        Args:
            client: Optional OpenAI client instance. If not provided, a new one will be created.
        """
        self.client = client or OpenAI()

    def list_vector_stores(self) -> List[Dict]:
        """
        List all available Vector Stores.

        Returns:
            List[Dict]: A list of dictionaries containing vector store information.
        """
        response = self.client.vector_stores.list()
        return [{"id": vs.id, "name": vs.name} for vs in response.data]
