"""
Unit tests for the delete_vector_store tool.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
from tools.openai_vs.delete_vector_store import DeleteVectorStoreTool


class TestDeleteVectorStoreTool(unittest.TestCase):
    def setUp(self):
        """Set up for testing."""
        self.registry = ToolRegistry()
        
        self.mock_client = MagicMock()
        
        self.patcher = patch("openai.OpenAI", return_value=self.mock_client)
        self.mock_openai = self.patcher.start()
        
        self.tool = DeleteVectorStoreTool(client=self.mock_client)

        self.test_vector_store_id = "vs_test123"

    def test_delete_vector_store_validation(self):
        """Test input validation for delete_vector_store."""
        with self.assertRaises(ValueError):
            self.tool.delete_vector_store("")

        with self.assertRaises(ValueError):
            self.tool.delete_vector_store(None)

    def test_delete_vector_store_success(self):
        """Test successful deletion of a vector store."""
        mock_client = MagicMock()
        self.tool.client = mock_client

        result = self.tool.delete_vector_store(self.test_vector_store_id)

        self.assertTrue(result["deleted"])
        self.assertEqual(result["id"], self.test_vector_store_id)

        mock_client.vector_stores.delete.assert_called_once_with(vector_store_id=self.test_vector_store_id)

    @patch("tools.openai_vs.delete_vector_store.DeleteVectorStoreTool.delete_vector_store")
    @patch("tools.openai_vs.delete_vector_store.OpenAI")
    def test_tool_registry_integration(self, mock_openai_class, mock_delete):
        """Test the tool integration with the registry."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_delete.return_value = {"deleted": True, "id": self.test_vector_store_id}

        input_data = {"vector_store_id": self.test_vector_store_id}

        result = self.registry.execute_tool("delete_vector_store", input_data)

        self.assertTrue(result["success"], msg=f"Tool execution failed: {result.get('error')}")
        self.assertTrue(result["result"]["deleted"])
        self.assertEqual(result["result"]["id"], self.test_vector_store_id)

        mock_delete.assert_called_once_with(self.test_vector_store_id)


if __name__ == "__main__":
    unittest.main()
