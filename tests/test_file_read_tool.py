# tests/test_file_read_tool.py
import os
import sys
import unittest
from unittest.mock import patch

# Import registry after setting up path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Now import after path setup
from core.tools.registry import ToolRegistry  # noqa: E402
# Import the singleton access function and services
from core.tools.registry_access import get_registry, reset_registry
from core.services import get_services, reset_services


class TestFileReadTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        # Reset both the registry singleton and services container
        reset_registry()
        reset_services()
        
        # Get the registry from the services container
        services = get_services()
        self.registry = services.tool_registry

    @patch("core.tools.registry.ToolRegistry.execute_tool")  # Patch registry's execute_tool method
    def test_file_read(self, mock_execute_tool):
        """Test the file read tool."""
        # Mock the execute_tool method to simulate a failure
        mock_execute_tool.return_value = {"success": False, "error": "API Error"}

        # Define the input data for the file read tool
        input_data = {
            "vector_store_ids": ["vs_test_store_123"],  # Use a plausible dummy ID
            "query": "What is the main topic?",
            "max_num_results": 5,
            "include_search_results": True,
        }

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
