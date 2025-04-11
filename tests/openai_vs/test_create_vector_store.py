"""
Tests for the CreateVectorStoreTool.
"""

import unittest
from unittest.mock import MagicMock, patch

from tools.openai_vs.create_vector_store import CreateVectorStoreTool


class TestCreateVectorStoreTool(unittest.TestCase):
    """
    Test cases for the CreateVectorStoreTool.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.mock_client = MagicMock()
        self.tool = CreateVectorStoreTool(client=self.mock_client)

    def test_create_vector_store_success(self):
        """
        Test successful vector store creation.
        """
        mock_response = MagicMock()
        mock_response.id = "vs_abc123"
        self.mock_client.vector_stores.create.return_value = mock_response

        result = self.tool.create_vector_store("Test Vector Store")

        self.assertEqual(result, "vs_abc123")
        self.mock_client.vector_stores.create.assert_called_once_with(name="Test Vector Store", file_ids=[])

    def test_create_vector_store_empty_name(self):
        """
        Test vector store creation with an empty name.
        """
        with self.assertRaises(ValueError):
            self.tool.create_vector_store("")

    def test_create_vector_store_invalid_name_type(self):
        """
        Test vector store creation with an invalid name type.
        """
        with self.assertRaises(ValueError):
            self.tool.create_vector_store(123)  # type: ignore

    @patch("tools.openai_vs.create_vector_store.OpenAI")
    def test_default_client_creation(self, mock_openai):
        """
        Test that a default client is created if none is provided.
        """
        CreateVectorStoreTool()

        mock_openai.assert_called_once()

    @patch("openai.OpenAI")
    def test_api_error_handling(self, mock_openai):
        """
        Test that API errors are properly propagated.
        """
        from openai import APIError

        mock_client = MagicMock()
        mock_request = MagicMock()
        mock_client.vector_stores.create.side_effect = APIError(message="API Error", request=mock_request, body=None)
        mock_openai.return_value = mock_client

        tool = CreateVectorStoreTool(client=mock_client)

        with self.assertRaises(APIError):
            tool.create_vector_store("Test Vector Store")


if __name__ == "__main__":
    unittest.main()
