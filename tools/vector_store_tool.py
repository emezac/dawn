import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class VectorStoreTool:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def create_vector_store(self, name: str, file_ids: list) -> str:
        """
        Create a vector store with the given name and list of file IDs.

        Args:
            name (str): The name for the vector store.
            file_ids (list): List of file IDs (e.g., ["file-xxx"]).

        Returns:
            str: The vector store ID (e.g., "vs_...") or an error message.
        """
        try:
            vector_store = self.client.vector_stores.create(name=name, file_ids=file_ids)
            print("Vector store created:", vector_store.id)
            return vector_store.id
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            return f"Error: {str(e)}"
