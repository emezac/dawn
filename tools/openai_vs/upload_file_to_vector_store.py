"""
Module for uploading files to OpenAI Vector Stores.
"""

import os
import time
from typing import Dict, Optional

import httpx
from openai import OpenAI

from tools.openai_vs.utils.vs_id_validator import assert_valid_vector_store_id


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

    def upload_and_add_file_to_vector_store(
        self, vector_store_id: str, file_path: str, purpose: str = "assistants"
    ) -> Dict:
        """
        Upload a file to OpenAI and add it to a Vector Store.

        Args:
            vector_store_id: The ID of the Vector Store to add the file to.
            file_path: The path to the file to upload.
            purpose: The purpose of the file upload. Must be one of: 'assistants', 'fine-tune',
                    'batch', 'user_data', 'vision', 'evals'. Defaults to 'assistants'.

        Returns:
            Dict: A dictionary containing the file_id and status information.

        Raises:
            ValueError: If vector_store_id or file_path is invalid.
            FileNotFoundError: If the file does not exist.
            Various OpenAI API Errors: If the API calls fail.
        """
        # Validate the vector store ID using the dedicated validator
        assert_valid_vector_store_id(vector_store_id)

        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate purpose parameter
        valid_purposes = ["assistants", "fine-tune", "batch", "user_data", "vision", "evals"]
        if purpose not in valid_purposes:
            raise ValueError(f"Invalid purpose: '{purpose}'. Must be one of: {', '.join(valid_purposes)}")

        try:
            # First upload the file to OpenAI
            with open(file_path, "rb") as file_obj:
                # Create the file with OpenAI using valid purpose value
                upload_response = self.client.files.create(file=file_obj, purpose=purpose)

                file_id = upload_response.id

                # Validate file_id format
                if not file_id or not isinstance(file_id, str) or not file_id.startswith("file-"):
                    raise ValueError(f"Invalid file_id format: {file_id}. Expected string starting with 'file-'")

            # Add the file to the vector store using direct API call
            try:
                # Get API key from the client
                api_key = self.client.api_key
                if not api_key:
                    raise ValueError("API key not found in OpenAI client")

                # Make direct API call using httpx
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

                url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
                payload = {"file_id": file_id}

                with httpx.Client(timeout=60.0) as http_client:
                    response = http_client.post(url, json=payload, headers=headers)

                    if response.status_code == 200 or response.status_code == 201:
                        pass
                    else:
                        # Try alternative payload format if first attempt failed
                        if response.status_code == 400:
                            payload = {"files": [file_id]}
                            response = http_client.post(url, json=payload, headers=headers)

                            if response.status_code == 200 or response.status_code == 201:
                                pass
                            else:
                                raise RuntimeError(f"Failed to add file to vector store: {response.text}")
                        else:
                            raise RuntimeError(f"Failed to add file to vector store: {response.text}")
            except Exception as e:
                raise RuntimeError(f"Error adding file to vector store: {str(e)}")

            # Poll for completion using direct API calls
            max_polling_attempts = 30
            polling_interval = 2  # seconds

            for attempt in range(max_polling_attempts):
                time.sleep(polling_interval)

                try:
                    # Use direct HTTPX call for polling file status
                    poll_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files/{file_id}"
                    poll_headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

                    with httpx.Client(timeout=30.0) as poll_client:
                        poll_response = poll_client.get(poll_url, headers=poll_headers)

                        if poll_response.status_code == 200:
                            poll_data = poll_response.json()
                            status = poll_data.get("status", "unknown")

                            if status == "completed" or status == "success":
                                return {"file_id": file_id, "status": "completed"}
                            elif status == "failed" or status == "error":
                                error_msg = poll_data.get("last_error", "Unknown error")
                                raise RuntimeError(f"File processing failed: {error_msg}")
                            elif status == "in_progress" or status == "pending":
                                # Continue polling
                                pass
                        else:
                            # Handle non-200 status code
                            raise RuntimeError(
                                f"Failed to check file status: {poll_response.status_code} - {poll_response.text}"
                            )
                except Exception as poll_e:
                    # Don't silently continue on all exceptions
                    # If this is an error status, propagate it
                    if isinstance(poll_e, RuntimeError) and "File processing failed" in str(poll_e):
                        raise

                    # Log other polling errors but continue polling
                    print(f"Warning: Error during polling attempt {attempt}: {str(poll_e)}")

                # Increase polling interval with backoff
                polling_interval = min(polling_interval * 1.5, 10)

            # If we get here, polling timed out but file might still be processing
            return {
                "file_id": file_id,
                "status": "in_progress",
                "message": "Polling timed out but file is being processed",
            }

        except Exception as e:
            error_type = type(e).__name__
            raise RuntimeError(f"Error in upload_and_add_file_to_vector_store ({error_type}): {str(e)}")
