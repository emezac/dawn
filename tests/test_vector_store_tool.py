import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.registry import ToolRegistry
# Import the singleton access function
from core.tools.registry_access import get_registry, reset_registry


class TestVectorStoreTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        # Reset the registry before each test
        reset_registry()
        # Get the singleton instance
        self.registry = get_registry()

        # Directly modify the vector_store_create handler for testing
        self.original_handler = self.registry.tools.get("vector_store_create")

    def tearDown(self):
        """Restore the original handler."""
        if hasattr(self, "original_handler"):
            self.registry.tools["vector_store_create"] = self.original_handler

    def test_vector_store_create(self):
        """Test the vector store create tool using a custom handler."""  # noqa: D202

        # Replace the handler with a simple function that returns a known result
        def mock_handler(**kwargs):
            name = kwargs.get("name", "")
            file_ids = kwargs.get("file_ids", [])

            if not name:
                raise ValueError("Missing 'name' parameter")

            # Verify inputs are as expected
            assert name == "Test Vector Store"
            assert file_ids == [] or file_ids == ["file-test123"]

            return "vs_test123"

        # Register our mock handler
        self.registry.tools["vector_store_create"] = mock_handler

        # Prepare input data
        input_data = {"name": "Test Vector Store"}

        # Execute the vector store create tool via the registry
        result = self.registry.execute_tool("vector_store_create", input_data)

        # Verify the results
        self.assertTrue(result["success"], msg=f"Vector store creation failed: {result.get('error')}")
        self.assertEqual(result["result"], "vs_test123")


if __name__ == "__main__":
    unittest.main()
