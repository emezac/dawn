"""
Unit tests for the list_vector_stores tool.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
from tools.openai_vs.list_vector_stores import ListVectorStoresTool
from core.tools.registry_access import get_registry, reset_registry


class TestListVectorStoresTool(unittest.TestCase):
    def setUp(self):
        """Set up for testing."""
        reset_registry()
        self.registry = get_registry()
        
        self.mock_client = MagicMock()
        
        self.patcher = patch("openai.OpenAI", return_value=self.mock_client)
        self.mock_openai = self.patcher.start()
        
        self.tool = ListVectorStoresTool(client=self.mock_client)
        
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()

    def test_list_vector_stores_success(self):
        """Test successful listing of vector stores."""
        mock_client = MagicMock()
        self.tool.client = mock_client

        mock_vs1 = MagicMock()
        mock_vs1.id = "vs_test123"
        mock_vs1.name = "Test Vector Store 1"

        mock_vs2 = MagicMock()
        mock_vs2.id = "vs_test456"
        mock_vs2.name = "Test Vector Store 2"

        mock_response = MagicMock()
        mock_response.data = [mock_vs1, mock_vs2]
        mock_client.vector_stores.list.return_value = mock_response

        result = self.tool.list_vector_stores()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "vs_test123")
        self.assertEqual(result[0]["name"], "Test Vector Store 1")
        self.assertEqual(result[1]["id"], "vs_test456")
        self.assertEqual(result[1]["name"], "Test Vector Store 2")

        mock_client.vector_stores.list.assert_called_once()

    def test_list_vector_stores_empty(self):
        """Test listing of vector stores when none exist."""
        mock_client = MagicMock()
        self.tool.client = mock_client

        mock_response = MagicMock()
        mock_response.data = []
        mock_client.vector_stores.list.return_value = mock_response

        result = self.tool.list_vector_stores()

        self.assertEqual(result, [])

        mock_client.vector_stores.list.assert_called_once()

    @patch("tools.openai_vs.list_vector_stores.ListVectorStoresTool.list_vector_stores")
    @patch("tools.openai_vs.list_vector_stores.OpenAI")
    def test_tool_registry_integration(self, mock_openai_class, mock_list):
        """Test the tool integration with the registry."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_list.return_value = [
            {"id": "vs_test123", "name": "Test Vector Store 1"},
            {"id": "vs_test456", "name": "Test Vector Store 2"},
        ]

        result = self.registry.execute_tool("list_vector_stores", {})

        self.assertTrue(result["success"], msg=f"Tool execution failed: {result.get('error')}")
        self.assertEqual(len(result["result"]), 2)
        self.assertEqual(result["result"][0]["id"], "vs_test123")

        mock_list.assert_called_once()


if __name__ == "__main__":
    unittest.main()
