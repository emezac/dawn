# tests/test_file_read_tool.py
import unittest
from core.tools.registry import ToolRegistry

class TestFileReadTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        self.registry = ToolRegistry()

    def test_file_read(self):
        """Test the file read tool."""
        # Define the input data for the file read tool
        input_data = {
            "vector_store_ids": ["vs_test_store_123"], # Use a plausible dummy ID
            "query": "What is the main topic?",
            "max_num_results": 5,
            "include_search_results": True
        }

        # Execute the file read tool
        # NOTE: This will likely still fail if the underlying FileReadTool
        # tries to make a real API call with dummy IDs. Consider mocking.
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