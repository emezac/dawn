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


class TestUploadFileToVectorStoreTool(unittest.TestCase):
    def setUp(self):
        """Set up for testing."""
        self.registry = ToolRegistry()
        
        self.mock_client = MagicMock()
        
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
    def test_upload_and_add_file_success(self, mock_sleep):
        """Test successful file upload and addition to vector store."""
        mock_client = MagicMock()
        self.tool.client = mock_client

        mock_file_upload = MagicMock()
        mock_file_upload.id = self.test_file_id
        mock_client.files.create.return_value = mock_file_upload

        mock_file_batch = MagicMock()
        mock_file_batch.id = self.test_batch_id
        mock_client.vector_stores.files.create.return_value = mock_file_batch

        mock_batch_status = MagicMock()
        mock_batch_status.status = "completed"
        mock_client.vector_stores.file_batches.retrieve.return_value = mock_batch_status

        result = self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, self.test_file_path)

        self.assertEqual(result["file_id"], self.test_file_id)
        self.assertEqual(result["batch_id"], self.test_batch_id)
        self.assertEqual(result["status"], "completed")

        mock_client.files.create.assert_called_once()
        mock_client.vector_stores.files.create.assert_called_once_with(
            vector_store_id=self.test_vector_store_id, file_ids=[self.test_file_id]
        )
        mock_client.vector_stores.file_batches.retrieve.assert_called_once_with(
            vector_store_id=self.test_vector_store_id, file_batch_id=self.test_batch_id
        )

    @patch("time.sleep", return_value=None)  # Skip sleeping during tests
    def test_upload_and_add_file_failure(self, mock_sleep):
        """Test file upload failure handling."""
        mock_client = MagicMock()
        self.tool.client = mock_client

        mock_file_upload = MagicMock()
        mock_file_upload.id = self.test_file_id
        mock_client.files.create.return_value = mock_file_upload

        mock_file_batch = MagicMock()
        mock_file_batch.id = self.test_batch_id
        mock_client.vector_stores.files.create.return_value = mock_file_batch

        mock_batch_status = MagicMock()
        mock_batch_status.status = "failed"
        mock_batch_status.error = "Test error message"
        mock_client.vector_stores.file_batches.retrieve.return_value = mock_batch_status

        with self.assertRaises(RuntimeError):
            self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, self.test_file_path)

    @patch("time.sleep", return_value=None)  # Skip sleeping during tests
    def test_upload_and_add_file_timeout(self, mock_sleep):
        """Test file upload timeout handling."""
        mock_client = MagicMock()
        self.tool.client = mock_client

        mock_file_upload = MagicMock()
        mock_file_upload.id = self.test_file_id
        mock_client.files.create.return_value = mock_file_upload

        mock_file_batch = MagicMock()
        mock_file_batch.id = self.test_batch_id
        mock_client.vector_stores.files.create.return_value = mock_file_batch

        mock_batch_status = MagicMock()
        mock_batch_status.status = "processing"
        mock_client.vector_stores.file_batches.retrieve.return_value = mock_batch_status

        self.tool.upload_and_add_file_to_vector_store.__globals__["max_polling_attempts"] = 3

        with self.assertRaises(TimeoutError):
            self.tool.upload_and_add_file_to_vector_store(self.test_vector_store_id, self.test_file_path)

    @patch(
        "tools.openai_vs.upload_file_to_vector_store.UploadFileToVectorStoreTool.upload_and_add_file_to_vector_store"
    )
    @patch("tools.openai_vs.upload_file_to_vector_store.OpenAI")
    def test_tool_registry_integration(self, mock_openai_class, mock_upload):
        """Test the tool integration with the registry."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_upload.return_value = {"file_id": self.test_file_id, "batch_id": self.test_batch_id, "status": "completed"}

        input_data = {"vector_store_id": self.test_vector_store_id, "file_path": self.test_file_path}

        result = self.registry.execute_tool("upload_file_to_vector_store", input_data)

        self.assertTrue(result["success"], msg=f"Tool execution failed: {result.get('error')}")
        self.assertEqual(result["result"]["file_id"], self.test_file_id)
        self.assertEqual(result["result"]["status"], "completed")

        mock_upload.assert_called_once_with(self.test_vector_store_id, self.test_file_path)


if __name__ == "__main__":
    unittest.main()
