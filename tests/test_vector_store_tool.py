import os
import sys
import unittest
from unittest.mock import patch

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry


class TestVectorStoreTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        self.registry = ToolRegistry()

    @patch("tools.vector_store_tool.VectorStoreTool.create_vector_store")
    def test_vector_store_create(self, mock_create_vector_store):
        """Test the vector store create tool with a mocked API call."""
        # Simulate a successful vector store creation returning "vs_test123"
        mock_create_vector_store.return_value = "vs_test123"

        # Prepare input data
        input_data = {"name": "Test Vector Store", "file_ids": ["file-test123"]}

        # Execute the vector store create tool via the registry
        result = self.registry.execute_tool("vector_store_create", input_data)

        # Check that the call was successful and the returned vector store ID starts with "vs_"
        self.assertTrue(result["success"], msg=f"Vector store creation failed: {result.get('error')}")
        self.assertTrue(result["result"].startswith("vs_"), msg="Vector store ID does not start with 'vs_'")


if __name__ == "__main__":
    unittest.main()
