"""
Minimal test to verify upload_file_to_vector_store.py changes.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.openai_vs.upload_file_to_vector_store import UploadFileToVectorStoreTool


class TestMinimalUploadFile(unittest.TestCase):
    """Test UploadFileToVectorStoreTool with minimal mocking."""

    def setUp(self):
        """Set up test case."""
        # Create a mock client
        self.mock_client = MagicMock()
        self.mock_client.api_key = "test-api-key"

        # Create the tool with the mock client
        self.tool = UploadFileToVectorStoreTool(client=self.mock_client)

        # Create a test file
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            self.test_file_path = temp_file.name
            temp_file.write("Test content")

        # Test vector store ID
        self.test_vector_store_id = "vs_test123"

    def tearDown(self):
        """Clean up after test."""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    @patch("openai.OpenAI")
    def test_validation(self, mock_openai):
        """Test input validation."""
        # Test with empty vector store ID
        with self.assertRaises(ValueError):
            self.tool.upload_and_add_file_to_vector_store("", self.test_file_path)

        # Test with empty file path
        with self.assertRaises(ValueError):
            self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, "")

        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, "/nonexistent/file.txt")

        # Test with invalid purpose
        with self.assertRaises(ValueError):
            self.tool.upload_and_add_file_to_vector_store(
                self.test_vector_store_id, self.test_file_path, purpose="invalid"
            )

    def test_purpose_validation(self):
        """Test purpose parameter validation."""
        valid_purposes = ["assistants", "fine-tune", "batch", "user_data", "vision", "evals"]
        for purpose in valid_purposes:
            # This should not raise an exception
            try:
                # Mock the file upload to avoid actual API calls
                with patch.object(self.mock_client.files, "create") as mock_create:
                    mock_create.return_value = MagicMock(id="file-123")

                    # Mock the HTTPX client
                    with patch("httpx.Client") as mock_client:
                        mock_http = MagicMock()
                        mock_client.return_value.__enter__.return_value = mock_http

                        # Mock the response
                        mock_response = MagicMock()
                        mock_response.status_code = 200
                        mock_response.json.return_value = {"id": "batch-123"}
                        mock_http.post.return_value = mock_response

                        # Mock the get response for status
                        mock_get_response = MagicMock()
                        mock_get_response.status_code = 200
                        mock_get_response.json.return_value = {"status": "completed"}
                        mock_http.get.return_value = mock_get_response

                        # Skip sleep to speed up tests
                        with patch("time.sleep"):
                            self.tool.upload_and_add_file_to_vector_store(
                                self.test_vector_store_id, self.test_file_path, purpose=purpose
                            )
            except ValueError:
                self.fail(f"Purpose {purpose} should be valid but raised ValueError")


if __name__ == "__main__":
    unittest.main()
