import unittest
from tools.registry import ToolRegistry

class TestFileReadTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        self.registry = ToolRegistry()

    def test_file_read(self):
        """Test the file read tool."""
        # Define the input data for the file read tool
        input_data = {
            "vector_store_ids": ["your_vector_store_id"],
            "max_num_results": 5,
            "include_search_results": True
        }
        
        # Execute the file read tool
        result = self.registry.execute_tool("file_read", input_data)
        
        # Assert the result
        if result["success"]:
            self.assertIsInstance(result["result"], str)
            self.assertNotEqual(result["result"], "No output text found")
        else:
            self.fail(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    unittest.main() 