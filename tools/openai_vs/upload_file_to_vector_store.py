"""
Module for uploading files to OpenAI Vector Stores.
"""

import os
import time
from typing import Dict, Optional

from openai import OpenAI


class UploadFileToVectorStoreTool:
    """
    Tool for uploading files to OpenAI Vector Stores.
    """

    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize the UploadFileToVectorStoreTool.

        Args:
            client: Optional OpenAI client instance. If not provided, a new one will be created.
        """
        self.client = client or OpenAI()

    def upload_and_add_file_to_vector_store(self, vector_store_id: str, file_path: str) -> Dict:
        """
        Upload a file to OpenAI and add it to a Vector Store.

        Args:
            vector_store_id: The ID of the Vector Store to add the file to.
            file_path: The path to the file to upload.

        Returns:
            Dict: A dictionary containing the file_id and status information.

        Raises:
            ValueError: If vector_store_id or file_path is invalid.
            FileNotFoundError: If the file does not exist.
            Various OpenAI API Errors: If the API calls fail.
        """
        if not vector_store_id or not isinstance(vector_store_id, str):
            raise ValueError("Vector Store ID must be a non-empty string")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as file:
            file_upload_response = self.client.files.create(file=file, purpose="assistants")

        file_id = file_upload_response.id

        file_batch = self.client.vector_stores.files.create(vector_store_id=vector_store_id, file_ids=[file_id])

        batch_id = file_batch.id
        max_polling_attempts = 30
        polling_interval = 2  # seconds

        for attempt in range(max_polling_attempts):
            time.sleep(polling_interval)

            batch_status = self.client.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store_id, file_batch_id=batch_id
            )

            if batch_status.status == "completed":
                return {"file_id": file_id, "batch_id": batch_id, "status": "completed"}
            elif batch_status.status == "failed":
                raise RuntimeError(f"File processing failed: {batch_status.error}")

            polling_interval = min(polling_interval * 1.5, 10)

        raise TimeoutError("File processing timed out")
