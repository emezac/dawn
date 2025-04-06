import unittest
from tools.registry import ToolRegistry

class TestWebSearchTool(unittest.TestCase):
    def setUp(self):
        """Set up the tool registry for testing."""
        self.registry = ToolRegistry()

    def test_web_search(self):
        """Test the web search tool."""
        # Define the input data for the web search tool
        input_data = {
            "query": "What was a positive news story from today?",
            "context_size": "medium",
            "user_location": {
                "type": "approximate",
                "country": "US",
                "city": "New York",
                "region": "NY"
            }
        }
        
        # Execute the web search tool
        result = self.registry.execute_tool("web_search", input_data)
        
        # Assert the result
        if result["success"]:
            # Check for expected content in the result
            positive_indicators = ["uplifting", "positive", "good news", "celebrate", "success", "achievement"]
            content = result["result"].lower()
            self.assertTrue(any(indicator in content for indicator in positive_indicators),
                            msg="No positive indicators found in the result.")
        else:
            self.fail(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    unittest.main()