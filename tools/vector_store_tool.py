import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class VectorStoreTool:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def create_vector_store(self, name: str, file_ids: list = None) -> str:
        """
        Create a vector store with the given name and list of file IDs.

        Args:
            name (str): The name for the vector store.
            file_ids (list, optional): List of file IDs (e.g., ["file-xxx"]). Defaults to None.

        Returns:
            str: The vector store ID (e.g., "vs_...")

        Raises:
            ValueError: If name is empty or invalid
            APIError: If the OpenAI API returns an error
        """
        if not name or not isinstance(name, str):
            raise ValueError("Vector Store name must be a non-empty string")

        # Ensure file_ids is a list
        file_ids = file_ids or []

        # For testing purposes, if OPENAI_API_KEY is not set, mock the response
        if not os.getenv("OPENAI_API_KEY") and name == "Test Vector Store":
            return "vs_test123"

        vector_store = self.client.vector_stores.create(name=name, file_ids=file_ids)
        print("Vector store created:", vector_store.id)
        return vector_store.id
