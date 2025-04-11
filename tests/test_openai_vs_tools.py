"""
Tests for OpenAI Vector Store tools.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path to allow importing from the project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.openai_vs.create_vector_store import CreateVectorStoreTool


class TestCreateVectorStoreTool(unittest.TestCase):
    """Test cases for the CreateVectorStoreTool."""

    @patch("openai.OpenAI")
    def test_create_vector_store(self, mock_openai):
        """Test creating a vector store with a name only."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.id = "vs_test123"
        mock_client.vector_stores.create.return_value = mock_response

        # Create tool instance and call method
        tool = CreateVectorStoreTool(mock_client)
        result = tool.create_vector_store("Test Vector Store")

        # Verify
        mock_client.vector_stores.create.assert_called_once_with(name="Test Vector Store", file_ids=[])
        self.assertEqual(result, "vs_test123")

    @patch("openai.OpenAI")
    def test_create_vector_store_with_files(self, mock_openai):
        """Test creating a vector store with name and file IDs."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.id = "vs_test456"
        mock_client.vector_stores.create.return_value = mock_response

        # Create tool instance and call method
        tool = CreateVectorStoreTool(mock_client)
        result = tool.create_vector_store("Test Vector Store", ["file-abc123", "file-def456"])

        # Verify
        mock_client.vector_stores.create.assert_called_once_with(
            name="Test Vector Store", file_ids=["file-abc123", "file-def456"]
        )
        self.assertEqual(result, "vs_test456")

    @patch("openai.OpenAI")
    def test_create_vector_store_error(self, mock_openai):
        """Test error handling when creating a vector store."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Simulate API error
        mock_client.vector_stores.create.side_effect = Exception("API Error")

        # Create tool instance and call method
        tool = CreateVectorStoreTool(mock_client)

        # Verify that the exception is propagated
        with self.assertRaises(Exception):
            tool.create_vector_store("Test Vector Store")

    def test_invalid_name(self):
        """Test validation for invalid vector store names."""
        tool = CreateVectorStoreTool()

        # Test empty name
        with self.assertRaises(ValueError):
            tool.create_vector_store("")

        # Test non-string name
        with self.assertRaises(ValueError):
            tool.create_vector_store(123)


if __name__ == "__main__":
    unittest.main()
