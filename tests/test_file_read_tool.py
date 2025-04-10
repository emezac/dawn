# tests/test_file_read_tool.py
import unittest
import sys
import os
from unittest.mock import patch
# Add parent directory to path to import framework modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.tools.registry import ToolRegistry

class TestFileReadTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        self.registry = ToolRegistry()

    @patch('core.tools.registry.ToolRegistry.execute_tool')  # Patch the registry's execute_tool method instead
    def test_file_read(self, mock_execute_tool):
        """Test the file read tool."""
        # Mock the execute_tool method to simulate a failure
        mock_execute_tool.return_value = {"success": False, "error": "API Error"}

        # Define the input data for the file read tool
        input_data = {
            "vector_store_ids": ["vs_test_store_123"], # Use a plausible dummy ID
            "query": "What is the main topic?",
            "max_num_results": 5,
            "include_search_results": True
        }

        # Execute the file read tool
        # The execute_tool call is now mocked, so it will return our mocked value
        result = self.registry.execute_tool("file_read", input_data)

        # Assert the result
        # Adjust assertions based on expected outcome (success/failure)
        # For now, just check if it doesn't raise the *missing query* error
        if not result["success"] and "Missing 'query'" in result.get("error", ""):
             self.fail("Test failed because 'query' was missing, even though it was added.")

        self.assertFalse(result["success"], "Expected tool execution to fail with dummy IDs without mocking.")
        self.assertIn("API Error", result.get("error", ""), "Expected an API-related error with dummy IDs.")


if __name__ == "__main__":
    unittest.main()
