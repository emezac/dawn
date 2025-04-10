"""
Module for saving text to OpenAI Vector Stores for Long-Term Memory.
"""

import os
import tempfile
from typing import Dict, Optional

from openai import OpenAI

from tools.openai_vs.upload_file_to_vector_store import UploadFileToVectorStoreTool


class SaveTextToVectorStoreTool:
    """
    Tool for saving text content to OpenAI Vector Stores for Long-Term Memory.
    """

    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize the SaveTextToVectorStoreTool.

        Args:
            client: Optional OpenAI client instance. If not provided, a new one will be created.
        """
        self.client = client or OpenAI()
        self.upload_tool = UploadFileToVectorStoreTool(self.client)

    def save_text_to_vector_store(self, vector_store_id: str, text_content: str) -> Dict:
        """
        Save text content to a Vector Store by creating a temporary file and uploading it.

        Args:
            vector_store_id: The ID of the Vector Store to add the text to.
            text_content: The text content to save.

        Returns:
            Dict: A dictionary containing the file_id and status information.

        Raises:
            ValueError: If vector_store_id is invalid or text_content is empty.
            Various OpenAI API Errors: If the API calls fail.
        """
        if not vector_store_id or not isinstance(vector_store_id, str):
            raise ValueError("Vector Store ID must be a non-empty string")
        if not text_content or not isinstance(text_content, str):
            raise ValueError("Text content must be a non-empty string")

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(text_content)

        try:
            result = self.upload_tool.upload_and_add_file_to_vector_store(
                vector_store_id=vector_store_id, file_path=temp_file_path
            )

            return result
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
