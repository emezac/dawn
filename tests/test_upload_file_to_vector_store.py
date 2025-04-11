"""
Unit tests for the upload_file_to_vector_store tool.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
from tools.openai_vs.upload_file_to_vector_store import UploadFileToVectorStoreTool
from core.tools.registry_access import get_registry, reset_registry


class TestUploadFileToVectorStoreTool(unittest.TestCase):
    def setUp(self):
        """Set up for testing."""
        # Reset the registry before each test
        reset_registry()
        # Get the singleton instance
        self.registry = get_registry()

        self.mock_client = MagicMock()
        self.mock_client.api_key = "test-api-key"

        self.patcher = patch("openai.OpenAI", return_value=self.mock_client)
        self.mock_openai = self.patcher.start()

        self.tool = UploadFileToVectorStoreTool(client=self.mock_client)

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            self.test_file_path = temp_file.name
            temp_file.write("Test content for vector store testing.")

        self.test_vector_store_id = "vs_test123"
        self.test_file_id = "file-test123"
        self.test_batch_id = "batch-test123"

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_upload_and_add_file_validation(self):
        """Test input validation for upload_and_add_file_to_vector_store."""
        with self.assertRaises(ValueError):
            self.tool.upload_and_add_file_to_vector_store("", self.test_file_path)

        with self.assertRaises(ValueError):
            self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, "")

        with self.assertRaises(FileNotFoundError):
            self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, "/non/existent/file.txt")

    @patch("time.sleep", return_value=None)  # Skip sleeping during tests
    @patch("httpx.Client")
    def test_upload_and_add_file_success(self, mock_httpx_client, mock_sleep):
        """Test successful file upload and addition to vector store."""
        # Mock file upload via OpenAI client
        mock_file_upload = MagicMock()
        mock_file_upload.id = self.test_file_id
        self.mock_client.files.create.return_value = mock_file_upload

        # Mock HTTPX client for direct API calls
        mock_client_instance = MagicMock()
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Mock successful response for adding file to vector store
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"id": self.test_batch_id}
        mock_client_instance.post.return_value = mock_post_response

        # Mock successful status check response
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"status": "completed"}
        mock_client_instance.get.return_value = mock_get_response

        # Run the test
        result = self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, self.test_file_path)

        # Verify results
        self.assertEqual(result["file_id"], self.test_file_id)
        self.assertEqual(result["status"], "completed")

        # Verify file upload was called
        self.mock_client.files.create.assert_called_once()

        # Verify HTTPX was used for direct API calls
        mock_client_instance.post.assert_called_once()
        expected_url = f"https://api.openai.com/v1/vector_stores/{self.test_vector_store_id}/files"
        mock_client_instance.post.assert_called_with(
            expected_url,
            json={"file_id": self.test_file_id},
            headers={"Authorization": "Bearer test-api-key", "Content-Type": "application/json"},
        )

        # Verify polling was done
        mock_client_instance.get.assert_called_once()

    @patch("time.sleep", return_value=None)  # Skip sleeping during tests
    @patch("httpx.Client")
    def test_upload_and_add_file_failure(self, mock_httpx_client, mock_sleep):
        """Test file upload failure handling."""
        # Mock file upload via OpenAI client
        mock_file_upload = MagicMock()
        mock_file_upload.id = self.test_file_id
        self.mock_client.files.create.return_value = mock_file_upload

        # Mock HTTPX client for direct API calls
        mock_client_instance = MagicMock()
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Mock successful response for adding file to vector store
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"id": self.test_batch_id}
        mock_client_instance.post.return_value = mock_post_response

        # Mock failed status check response
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"status": "failed", "last_error": "Test error message"}
        mock_client_instance.get.return_value = mock_get_response

        # Run the test expecting an error
        with self.assertRaises(RuntimeError):
            self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, self.test_file_path)

    @patch("time.sleep", return_value=None)  # Skip sleeping during tests
    @patch("httpx.Client")
    def test_upload_and_add_file_timeout(self, mock_httpx_client, mock_sleep):
        """Test file upload timeout handling."""
        # Mock file upload via OpenAI client
        mock_file_upload = MagicMock()
        mock_file_upload.id = self.test_file_id
        self.mock_client.files.create.return_value = mock_file_upload

        # Mock HTTPX client for direct API calls
        mock_client_instance = MagicMock()
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Mock successful response for adding file to vector store
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"id": self.test_batch_id}
        mock_client_instance.post.return_value = mock_post_response

        # Mock in-progress status check response
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"status": "in_progress"}
        mock_client_instance.get.return_value = mock_get_response

        # Limit polling attempts for test
        original_max_attempts = self.tool.upload_and_add_file_to_vector_store.__globals__.get(
            "max_polling_attempts", 30
        )
        try:
            self.tool.upload_and_add_file_to_vector_store.__globals__["max_polling_attempts"] = 2

            # Run the test - should return in_progress status instead of raising error
            result = self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, self.test_file_path)

            # Verify results
            self.assertEqual(result["file_id"], self.test_file_id)
            self.assertEqual(result["status"], "in_progress")
            self.assertIn("message", result)

        finally:
            # Restore original value
            self.tool.upload_and_add_file_to_vector_store.__globals__["max_polling_attempts"] = original_max_attempts

    @patch(
        "tools.openai_vs.upload_file_to_vector_store.UploadFileToVectorStoreTool.upload_and_add_file_to_vector_store"
    )
    @patch("tools.openai_vs.upload_file_to_vector_store.OpenAI")
    def test_tool_registry_integration(self, mock_openai_class, mock_upload):
        """Test the tool integration with the registry."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_upload.return_value = {"file_id": self.test_file_id, "status": "completed"}

        input_data = {
            "vector_store_id": self.test_vector_store_id,
            "file_path": self.test_file_path,
            "purpose": "assistants",
        }

        result = self.registry.execute_tool("upload_file_to_vector_store", input_data)

        self.assertTrue(result["success"], msg=f"Tool execution failed: {result.get('error')}")
        self.assertEqual(result["result"]["file_id"], self.test_file_id)
        self.assertEqual(result["result"]["status"], "completed")

        mock_upload.assert_called_once_with(self.test_vector_store_id, self.test_file_path, purpose="assistants")


if __name__ == "__main__":
    unittest.main()
