"""
Unit tests for the save_text_to_vector_store tool.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
from tools.openai_vs.save_text_to_vector_store import SaveTextToVectorStoreTool
from core.tools.registry_access import get_registry, reset_registry


class TestSaveTextToVectorStoreTool(unittest.TestCase):
    def setUp(self):
        """Set up for testing."""
        reset_registry()
        self.registry = get_registry()

        self.mock_client = MagicMock()

        self.patcher = patch("openai.OpenAI", return_value=self.mock_client)
        self.mock_openai = self.patcher.start()

        self.tool = SaveTextToVectorStoreTool(client=self.mock_client)

        self.test_vector_store_id = "vs_test123"
        self.test_text_content = "This is test content for long-term memory."
        self.test_file_id = "file-test123"

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()

    def test_save_text_validation(self):
        """Test input validation for save_text_to_vector_store."""
        with self.assertRaises(ValueError):
            self.tool.save_text_to_vector_store("", self.test_text_content)

        with self.assertRaises(ValueError):
            self.tool.save_text_to_vector_store(self.test_vector_store_id, "")

    @patch("tempfile.NamedTemporaryFile")
    @patch("os.path.getsize", return_value=10)  # Simulate non-empty file
    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    def test_save_text_success(self, mock_remove, mock_exists, mock_getsize, mock_temp_file):
        """Test successful text saving to vector store."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_temp_file.txt"
        mock_temp_file.return_value.__enter__.return_value = mock_file

        mock_upload_tool = MagicMock()
        self.tool.upload_tool = mock_upload_tool

        mock_upload_result = {"file_id": self.test_file_id, "status": "completed"}
        mock_upload_tool.upload_and_add_file_to_vector_store.return_value = mock_upload_result

        result = self.tool.save_text_to_vector_store(self.test_vector_store_id, self.test_text_content)

        self.assertEqual(result, mock_upload_result)

        mock_file.write.assert_called_once_with(self.test_text_content)

        mock_upload_tool.upload_and_add_file_to_vector_store.assert_called_once_with(
            vector_store_id=self.test_vector_store_id, file_path=mock_file.name, purpose="assistants"
        )

        mock_remove.assert_called_once_with(mock_file.name)

    @patch("tempfile.NamedTemporaryFile")
    @patch("os.path.getsize", return_value=10)  # Simulate non-empty file
    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    def test_save_text_upload_failure(self, mock_remove, mock_exists, mock_getsize, mock_temp_file):
        """Test handling of upload failure when saving text."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_temp_file.txt"
        mock_temp_file.return_value.__enter__.return_value = mock_file

        mock_upload_tool = MagicMock()
        self.tool.upload_tool = mock_upload_tool
        mock_upload_tool.upload_and_add_file_to_vector_store.side_effect = RuntimeError("Upload failed")

        with self.assertRaises(RuntimeError):
            self.tool.save_text_to_vector_store(self.test_vector_store_id, self.test_text_content)

        mock_remove.assert_called_once_with(mock_file.name)

    @patch("tempfile.NamedTemporaryFile")
    @patch("os.path.getsize", return_value=0)  # Simulate empty file
    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    def test_save_text_empty_file_error(self, mock_remove, mock_exists, mock_getsize, mock_temp_file):
        """Test handling of empty file error."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_temp_file.txt"
        mock_temp_file.return_value.__enter__.return_value = mock_file

        with self.assertRaises(RuntimeError):
            self.tool.save_text_to_vector_store(self.test_vector_store_id, self.test_text_content)

        mock_remove.assert_called_once_with(mock_file.name)

    @patch("tools.openai_vs.save_text_to_vector_store.SaveTextToVectorStoreTool.save_text_to_vector_store")
    @patch("tools.openai_vs.save_text_to_vector_store.OpenAI")
    def test_tool_registry_integration(self, mock_openai_class, mock_save):
        """Test the tool integration with the registry."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_save.return_value = {"file_id": self.test_file_id, "status": "completed"}

        input_data = {"vector_store_id": self.test_vector_store_id, "text_content": self.test_text_content}

        result = self.registry.execute_tool("save_to_ltm", input_data)

        self.assertTrue(result["success"], msg=f"Tool execution failed: {result.get('error')}")
        self.assertEqual(result["result"]["file_id"], self.test_file_id)
        self.assertEqual(result["result"]["status"], "completed")

        mock_save.assert_called_once_with(self.test_vector_store_id, self.test_text_content)


if __name__ == "__main__":
    unittest.main()
